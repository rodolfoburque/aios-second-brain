#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-wikilinks.py - finds every [[wikilink]] that does not resolve to a vault target.

It comes from the vault's precedence rule (02 Context/me.md): the vault is the source of
documentation, and the agent's automatic memory is only a pointer. Because BOTH systems
use the same [[name]] syntax, memory slugs ended up written inside vault notes, turning
into links that promise a source and deliver nothing.

Revised once. The earlier version overestimated the damage by 2.2x (231 reported for 106
real ones) and because of that it sent people to repair links that were not broken. Three
defects, all in target RESOLUTION, none in detection:

  1. ESCAPED PIPE IN A TABLE. `[[target\\|alias]]` inside a markdown table is a valid
     link in Obsidian: the backslash escapes the pipe for the table renderer. The regex
     `[^\\]\\|#]+` stopped at the pipe but carried the backslash along, and "target\\"
     never resolved. 109 false occurrences.
  2. TARGET THAT IS NOT A .md. The vault stores artifacts that are not notes and are
     cited as notes: `[[some-report]]` points to an .html, `[[some-script]]` to a .py.
     The index only had .md files, so every artifact became a dead link. Now the index
     loads the whole vault and the MISSING EXTENSION class already says what to write
     instead.
  3. EXTENSION WRITTEN IN THE LINK. `[[note.md]]` resolves in Obsidian; here it did not.

Runs with no external dependency:
    python "04 Resources/tools/check-wikilinks.py"
    python "04 Resources/tools/check-wikilinks.py" --memory-slugs        # only that class
    python "04 Resources/tools/check-wikilinks.py" --missing-extension   # only that class

Exits with code 1 if it finds a broken link, so it can become a hook later.
"""

import io
import os
import re
import sys

# CLAUDE.md rule: a script that runs on Windows forces UTF-8 on its I/O.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Claude Code names the project folder after the vault's absolute path, with every
# character that is not a letter or a digit replaced by a hyphen.
MEMORY = os.path.join(
    os.path.expanduser("~"),
    ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", ROOT), "memory",
)
IGNORE = (".agents", ".claude", ".git", ".obsidian", "node_modules", "__pycache__", ".github")

# Code is not a reference: `[[wikilinks]]` quoted as syntax is not a broken link.
# Neither is an HTML comment: the project-map keeps its template example inside one.
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[\[([^\]\|#]+)")


def clean(target):
    """Strip whitespace and the backslash that escapes the pipe inside a table."""
    return target.strip().rstrip("\\").strip()


def build_index():
    """Index the WHOLE vault, not only the notes.

    Returns (notes, files, artifacts, complete):
      notes     - .md targets that Obsidian resolves (basename and relative path, no .md)
      files     - the .md notes that will be scanned
      artifacts - {key without extension -> relative path} for what is NOT a .md
      complete  - the same set WITH the extension, for the link that wrote it correctly.
                  An ambiguous basename (same name in different folders, like SKILL) stays
                  only under its full path: pointing to the wrong file is worse than not
                  pointing at all.
    """
    notes, files = set(), []
    by_base, artifacts, complete = {}, {}, set()
    for folder, subs, names in os.walk(ROOT):
        subs[:] = [s for s in subs if s not in IGNORE]
        for name in names:
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            base, ext = os.path.splitext(name)
            if ext == ".md":
                notes.add(base)
                notes.add(rel[:-3])
                files.append(path)
            else:
                artifacts[rel[: -len(ext)] if ext else rel] = rel
                complete.add(rel)
                by_base.setdefault(base, []).append(rel)
    for base, found in by_base.items():
        if len(found) != 1:
            continue
        complete.add(os.path.basename(found[0]))   # the extension already disambiguates
        if base not in notes:
            artifacts[base] = found[0]
    return notes, files, artifacts, complete


def memory_slugs():
    if not os.path.isdir(MEMORY):
        return set()
    return {n[:-3] for n in os.listdir(MEMORY) if n.endswith(".md") and n != "MEMORY.md"}


def resolve(target, notes, artifacts, complete):
    """Returns (kind, real_target). kind: ok | missing_extension | dead."""
    if not target:
        return "ok", None
    if target in notes:
        return "ok", None
    if target.endswith(".md") and target[:-3] in notes:   # extension written in the link
        return "ok", None
    if target in complete:                                # already wrote the right extension
        return "ok", None
    if target in artifacts:                               # [[x]] for x.html / x.py / x.json
        return "missing_extension", artifacts[target]
    return "dead", None


def main():
    only_memory = "--memory-slugs" in sys.argv
    only_extension = "--missing-extension" in sys.argv
    notes, files, artifacts, complete = build_index()
    memory = memory_slugs()

    missing_ext, dead, suggestion, total = {}, {}, {}, 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        text = INLINE.sub(" ", FENCE.sub(" ", COMMENT.sub(" ", text)))
        rel = os.path.relpath(path, ROOT)
        for m in LINK.finditer(text):
            target = clean(m.group(1))
            total += 1
            kind, real_target = resolve(target, notes, artifacts, complete)
            if kind == "missing_extension":
                missing_ext.setdefault(target, []).append(rel)
                suggestion[target] = real_target
            elif kind == "dead":
                dead.setdefault(target, []).append(rel)

    from_memory = {k: v for k, v in dead.items() if k in memory}
    others = {k: v for k, v in dead.items() if k not in memory}
    occurrences = lambda d: sum(len(v) for v in d.values())

    print("%d wikilinks checked in %d notes\n" % (total, len(files)))
    print("  MEMORY SLUG used as a wikilink     : %3d targets / %3d occurrences"
          % (len(from_memory), occurrences(from_memory)))
    print("  MISSING EXTENSION (target exists)  : %3d targets / %3d occurrences"
          % (len(missing_ext), occurrences(missing_ext)))
    print("  TARGET DOES NOT EXIST              : %3d targets / %3d occurrences"
          % (len(others), occurrences(others)))

    def listing(title, data, with_suggestion=False):
        if not data:
            return
        print("\n--- %s (by frequency) ---" % title)
        for target, where in sorted(data.items(), key=lambda kv: -len(kv[1])):
            mark = "  [memory]" if target in memory else ""
            if with_suggestion and suggestion.get(target):
                mark = "  ->  %s" % suggestion[target]
            print("%4dx  %s%s" % (len(where), target, mark))
            for file in sorted(set(where))[:3]:
                print("         %s" % file)
            if len(set(where)) > 3:
                print("         ... and %d more note(s)" % (len(set(where)) - 3))

    if only_memory:
        listing("MEMORY SLUGS", from_memory)
    elif only_extension:
        listing("MISSING EXTENSION", missing_ext, with_suggestion=True)
    else:
        listing("MISSING EXTENSION", missing_ext, with_suggestion=True)
        listing("TARGET DOES NOT EXIST", dead)

    return 1 if (missing_ext or dead) else 0


if __name__ == "__main__":
    sys.exit(main())
