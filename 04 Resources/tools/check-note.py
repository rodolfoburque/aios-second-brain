#!/usr/bin/env python3
"""Mechanical checker for a vault note.

Component 4 of the harness (verification). Checks only what is objectively
verifiable: frontmatter, wikilink resolution, orphan notes and internal markdown
links. It has no opinion about content.

Usage:
    python check-note.py <file.md | folder> [...]
    python check-note.py --new          # only what git sees as new/modified

Output: findings as file:line. Exit 0 = passed, 1 = there are findings.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# Windows: a cp1252 stdout blows up on accented characters and arrows, so force UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[2]
IGNORE = {".git", ".obsidian", "node_modules", ".claude", "__pycache__", ".vercel", ".github"}
REQUIRED_FIELDS = ("type", "date", "status", "tags")

# The agent's memories live OUTSIDE the vault (~/.claude/projects/<slug>/memory/).
# The vault links to them on purpose: the agent resolves them, Obsidian does not.
# That is not a broken link, it is a link that points outside. It is still a dead
# click in the app, so it comes out as a warning and not as a failure.
# Claude Code names the project folder after the vault's absolute path, with every
# character that is not a letter or a digit replaced by a hyphen.
MEMORY_DIR = (
    Path.home() / ".claude" / "projects"
    / re.sub(r"[^A-Za-z0-9]", "-", str(VAULT)) / "memory"
)

# [[target]] · [[target|alias]] · [[target#section]] · [[folder/target|alias]]
RE_WIKILINK = re.compile(r"\[\[([^\[\]|#]+)(?:#[^\[\]|]*)?(?:\|[^\[\]]*)?\]\]")
# [text](path.md): markdown link to an internal file, forbidden by the vault rule
RE_INTERNAL_MDLINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+\.md)\)")
RE_FENCE = re.compile(r"^\s*(```|~~~)")
# inline code: `like this`. A wikilink in there is a quoted example, not a link.
RE_INLINE_CODE = re.compile(r"`[^`]*`")


def vault_files():
    """Index every file in the vault by basename and by relative path."""
    by_name, by_path = {}, set()
    for root, dirs, names in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for name in names:
            p = Path(root) / name
            rel = p.relative_to(VAULT).as_posix()
            by_path.add(rel)
            by_path.add(rel.rsplit(".", 1)[0] if "." in name else rel)
            by_name.setdefault(p.stem.lower(), []).append(rel)
            by_name.setdefault(name.lower(), []).append(rel)
    return by_name, by_path


def code_lines(text):
    """Lines that Obsidian does NOT render as links: code blocks and HTML
    comments. A wikilink in there is an example or a draft, not a live link, and
    flagging it fills the report with noise."""
    inside, comment, marked = False, False, set()
    for i, line in enumerate(text.splitlines(), 1):
        if RE_FENCE.match(line):
            inside = not inside
            marked.add(i)
            continue
        if inside:
            marked.add(i)
            continue
        if comment:
            marked.add(i)
            if "-->" in line:
                comment = False
            continue
        if "<!--" in line and "-->" not in line:
            comment = True
            marked.add(i)
    return marked


def check_frontmatter(text, rel):
    findings = []
    # AIOS/agents/ (except the README) is a byte-for-byte MIRROR of
    # ~/.claude/agents/. The frontmatter there is the one Claude Code requires
    # (name, description, tools); adding vault fields would break the equality
    # that sync-agents.py --check compares, and the check would report a
    # divergence forever.
    rel_norm = str(rel).replace("\\", "/")
    if rel_norm.startswith("AIOS/agents/") and not rel_norm.endswith("README.md"):
        return []
    if not text.startswith("---"):
        return [(rel, 1, "NO FRONTMATTER", "note has no YAML block at the top")]
    end = text.find("\n---", 3)
    if end == -1:
        return [(rel, 1, "UNCLOSED FRONTMATTER", "YAML block does not close with ---")]
    block = text[3:end]
    for field in REQUIRED_FIELDS:
        if not re.search(rf"(?m)^{field}\s*:", block):
            findings.append((rel, 1, "FRONTMATTER", f"missing the field '{field}'"))
    return findings


def known_memories():
    if not MEMORY_DIR.is_dir():
        return set()
    return {p.stem.lower() for p in MEMORY_DIR.glob("*.md")}


def check_links(text, rel, by_name, by_path, memories):
    findings = []
    skip = code_lines(text)
    for i, line in enumerate(text.splitlines(), 1):
        if i in skip:
            continue
        # A wikilink inside inline code (`[[like this]]`) is a quoted EXAMPLE,
        # not a real link: Obsidian does not resolve it and the author did not
        # want it resolved. Counting it as broken is noise.
        line = RE_INLINE_CODE.sub(" ", line)
        for m in RE_WIKILINK.finditer(line):
            # Inside a TABLE Obsidian requires the pipe to be escaped:
            # [[note\|alias]]. The target group captures the backslash too, and
            # without stripping it every link in a table came out "broken".
            # Mass false positives make people stop reading the checker, which
            # is worse than having no checker.
            target = m.group(1).strip().rstrip("\\").strip()
            if not target:
                continue
            found = (
                target in by_path
                or f"{target}.md" in by_path
                or target.lower() in by_name
                or f"{target.lower()}.md" in by_name
            )
            if not found:
                if target.lower() in memories:
                    findings.append(
                        (rel, i, "WARNING/MEMORY",
                         f"[[{target}]] is an agent memory, not a note: it does not open in Obsidian")
                    )
                else:
                    findings.append((rel, i, "BROKEN LINK", f"[[{target}]] does not exist in the vault"))
        for m in RE_INTERNAL_MDLINK.finditer(line):
            findings.append(
                (rel, i, "INTERNAL MARKDOWN LINK", f"({m.group(1)}) should be a [[wikilink]]")
            )
    return findings


def check_orphan(rel, by_name):
    """Does any other note link to this one? Indexes and maps do not count as orphans."""
    stem = Path(rel).stem
    if stem.lower() in {"home", "readme", "index", "memory"} or "/index" in rel.lower():
        return []
    target_re = re.compile(re.escape(stem), re.I)
    for root, dirs, names in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for name in names:
            if not name.endswith(".md"):
                continue
            p = Path(root) / name
            if p.relative_to(VAULT).as_posix() == rel:
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not target_re.search(content):
                continue
            for m in RE_WIKILINK.finditer(content):
                if Path(m.group(1).strip()).name.lower() == stem.lower():
                    return []
    return [(rel, 1, "ORPHAN", "no other note links here; the vault never reaches it again")]


def git_targets():
    try:
        output = subprocess.run(
            ["git", "status", "--porcelain"], cwd=VAULT,
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        ).stdout
    except Exception as e:  # noqa: BLE001
        print(f"could not read git: {e}")
        return []
    targets = []
    for line in output.splitlines():
        path = line[3:].strip().strip('"')
        if path.endswith(".md"):
            targets.append(VAULT / path)
    return targets


def expand(args):
    targets = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            p = (VAULT / a) if (VAULT / a).exists() else p.resolve()
        if p.is_dir():
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if d not in IGNORE]
                targets += [Path(root) / n for n in names if n.endswith(".md")]
        elif p.suffix == ".md":
            targets.append(p)
        else:
            print(f"ignored (not a .md): {a}")
    return targets


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    targets = git_targets() if args[0] == "--new" else expand(args)
    targets = [t for t in targets if t.exists()]
    if not targets:
        print("nothing to check.")
        return 0

    by_name, by_path = vault_files()
    memories = known_memories()
    findings = []
    for file in targets:
        rel = file.relative_to(VAULT).as_posix()
        if rel == "README.md":
            # the repository's front page is written for GitHub, not a vault note
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        findings += check_frontmatter(text, rel)
        findings += check_links(text, rel, by_name, by_path, memories)
        findings += check_orphan(rel, by_name)

    failures = [f for f in findings if not f[2].startswith("WARNING")]
    warnings = [f for f in findings if f[2].startswith("WARNING")]

    print(f"checked {len(targets)} note(s).")
    if warnings:
        print(f"\n{len(warnings)} warning(s) (do not fail the check):\n")
        for rel, line, kind, detail in warnings:
            print(f"  {rel}:{line}  [{kind}] {detail}")
    if not failures:
        print("\nPASSED: frontmatter complete, wikilinks resolve, no orphans.")
        return 0
    print(f"\n{len(failures)} failure(s):\n")
    for rel, line, kind, detail in failures:
        print(f"  {rel}:{line}  [{kind}] {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
