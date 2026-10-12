#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vault-metrics.py - measures what the current lint does NOT measure.

`check-wikilinks.py` measures INTEGRITY (does the link open?) and the graph closed at zero
because of it. Closed integrity does not mean a smart vault: a vault can have zero dead
links and still be a warehouse of dated reports that never became knowledge. The first
measurement on the source vault: 660 notes, mean degree 12.2, median 8. The graph was
healthy, and even so the knowledge was not where the agent finds it.

It measures four ratios, the first three borrowed from neuroscience and all of them with a
real counterpart here. The order is the same as in the output:

  1. CONSOLIDATION (cortex / hippocampus). The brain records a cheap episode in the
     hippocampus and during replay transfers the pattern to the neocortex, throwing the
     detail away. A big hippocampus and a small cortex can only answer questions with a
     date. In the vault, hippocampus is `01 Daily`, transcript, lesson, log, research and
     decision; cortex is `knowledge/`, `04 Resources/frameworks/` and `02 Context/`:
     timeless notes, which state instead of report. It rises by consolidating, never by
     capturing.

  2. HOT PATH (cortex within reach of a cue). Having a cortex is not enough: the brain
     only uses what it can retrieve, and retrieval works by CUE, not by search. The
     automatic cue here is `session-start.py` (it injects `02 Context/me.md` and the daily
     note) plus what `CLAUDE.md` says to read on the first message. A note counts as hot
     when it is in those folders AND when one of them cites it: 1 hop, because a pointer
     IS a cue. This was the real defect in the source vault: healthy consolidation (2.4
     to 1) and only 15.5% of the cortex within reach, with a pitfalls note pulled by 22
     notes and loaded by none. After adding pointers that same afternoon: 37.9%.

  3. LONG EDGE (small-world topology). The brain is not fully connected because wiring
     costs energy: it is dense local clusters plus a few long-distance connections, and
     those few are what let one area talk to another. Here, a long edge is a link that
     crosses clusters (from `03 Projects/X` to `knowledge`, from a lesson in one course
     to a problem in a project). A link inside the same folder is a local cluster, and
     that is already dense.

  4. PRUNING. From birth to the end of adolescence the brain LOSES about half of its
     synapses, and that is when it gets fast. An isolated note or one with no `type` is
     not an asset, it is a retrieval cost charged to every future search.

FOUR HONESTIES, because a metric that oversells itself turns into theater:

  a. `decision` is counted as HIPPOCAMPUS. That is debatable: a decision record is the
     middle step. It stayed episodic because its FORM is dated ("on that day we decided
     X"), and that is exactly why it is the biggest stock of promotion to the cortex. If
     one day it becomes cortex by decree, change it here and say so in the log. Do not
     change it in silence.
  a2. `reference` is counted as CORTEX, and that fixed a wrong diagnosis. The first
     measurement only counted `knowledge/` as cortex and announced 16 report notes for 1
     knowledge note, which would have sent you to consolidate what was already
     consolidated. The `reference` notes in `04 Resources/` (a platform doctrine, an
     industry map, a brand system) are timeless statements distilled from raw material:
     they are cortex by content, they are just not on the hot path. One caveat remains:
     a handful of them are dated snapshots ("state of the account on a given day") and
     should be `report`; until they are, the cortex is slightly overestimated.
  b. The long-edge rate is reported TWICE: raw and without summary notes. An index note
     (Home, README, index, map) links everything to everything by trade, so it inflates
     the rate without any idea having connected to another. The rate without summary
     notes is the honest one.
  c. The hot path stops at 1 HOP on purpose. Two notes away is already a search, and a
     search depends on someone remembering. Counting 2+ hops would make the rate look
     great in a vault where nobody finds anything. Counting ONLY the folder would be the
     opposite mistake: it would reward moving files to `knowledge/`, which blows the
     context ceiling and is exactly what /consolidate forbids. 1 hop is the only cut
     that rewards the right action, the pointer.
  d. This does NOT measure use. An edge only becomes memory when it is traveled (Hebb),
     and what this script counts is anatomy, not firing. Measuring firing requires
     reading the session history; that is out of scope here and is noted as a known gap.

Runs with no external dependency:
    python "04 Resources/tools/vault-metrics.py"
    python "04 Resources/tools/vault-metrics.py" --triage    # lists pruning candidates
    python "04 Resources/tools/vault-metrics.py" --summary   # 4 lines, for the hook
    python "04 Resources/tools/vault-metrics.py" --json

Always exits with code 0. This is a thermometer, never a gate: none of the four ratios
has a "wrong" value that justifies blocking someone's work.
"""

import io
import json
import os
import re
import sys

# CLAUDE.md rule: a script that runs on Windows forces UTF-8 on its I/O.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IGNORE = (".agents", ".claude", ".git", ".obsidian", "node_modules", "__pycache__", ".github")

# ARTIFACT: a .md that is MACHINE OUTPUT, not a note. It counts in the graph (the link to
# it is real) but never in pruning. The first run on the source vault flagged 44 isolated
# notes and 41 were this: 31 report.md files from an audit tool (one per target, two
# rounds) and 10 chat conversation archives. None of them should be linked by anything:
# the report exists to be read once and the conversation archive is an agent dump. A
# metric that flags 41 items nobody should touch trains the owner to ignore the metric,
# which is worse than not measuring.
ARTIFACT = ("04 Resources/tools/ux-audit/", "04 Resources/conversations/")
ARTIFACT_NAME = ("report.md",)

# EXEMPT from the note contract (frontmatter `type`), for the same reason: they are not
# notes. CLAUDE.md is an instruction read by Claude Code, and YAML frontmatter in it would
# show up as literal text in the injection. README is a folder cover. AIOS/agents/*.md are
# agent definitions, with their own frontmatter (name/description/tools/model) that is not
# the vault's. They stay in the graph and in the ratio; they are just not asked for `type`.
EXEMPT_NAME = ("CLAUDE.md", "README.md")
EXEMPT_FOLDER = ("AIOS/agents/",)

COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[\[([^\]\|#]+)")
TYPE = re.compile(r"^type:\s*(\S+)", re.M)
STATUS = re.compile(r"^status:\s*(\S+)", re.M)
ALIAS = re.compile(r"^aliases:\s*\[(.*?)\]", re.M)

# --- memory layers --------------------------------------------------------------
# Dated report. Cheap to record, expensive to keep, answers questions with a date.
HIPPOCAMPUS = {
    "daily", "daily-note", "transcript", "lesson", "log", "research", "decision",
    "meeting", "report", "audit", "whatsapp-archive", "session",
}
# Timeless statement. Expensive to write, answers questions without a date.
CORTEX = {
    "knowledge", "framework", "context", "identity", "playbook", "checklist",
    "principle", "reference", "process", "protocol", "guide",
}
# System infrastructure. Not memory, stays out of the ratio (otherwise 89 skills mask
# everything). The second group came from sweeping the UNDEFINED layer: 21 types with one
# occurrence each, legitimate and outside the vocabulary. A new type is not an error, it
# is missing vocabulary: a legitimate exception becomes code instead of a mental note.
OPERATIONAL = {
    "skill", "command", "prompt", "index", "map", "harness", "project", "spec",
    "resource", "asset", "content-plan", "content-queue", "content-asset", "draft",
    "offer", "idea", "template", "tool", "readme",
    "design", "outreach", "outreach-batch", "project-note", "backlog", "review",
    "plan", "prd", "ads-audit", "proposal", "capture", "content", "copy",
    "brief", "archive", "system", "hub",
}
# The folder outranks the type when the type is missing or too generic.
CORTEX_FOLDER = ("knowledge/", "02 Context/", "04 Resources/frameworks/")
HIPPOCAMPUS_FOLDER = ("01 Daily/", "03 Intelligence/")

# A summary note links by trade: it inflates the long edge without connecting any idea.
SUMMARY_TYPES = {"index", "map"}
SUMMARY_NAMES = {"home", "readme", "index", "vault-index", "moc"}

# Hot path = what session-start.py injects on its own in every session, plus what
# CLAUDE.md says to read on the first message. Cortex outside of this depends on someone
# remembering. If the hook changes what it loads, this tuple changes with it, otherwise
# the metric lies.
HOT = ("knowledge/", "02 Context/", "CLAUDE.md", "AIOS/index.md",
       "AIOS/operating-rules.md", "AIOS/knowledge-routing.md")


def layer(rel, note_type, status=""):
    """Returns cortex | hippocampus | operational | artifact | undefined.

    `status: template` is NEVER cortex, no matter what the folder and the type say.
    A template is FORM, not a statement: the file carries the "edit with your real
    principles" banner and generic content that does not belong to the vault owner.
    Found by a usage measurement on the source vault: 4 of the 10 files in `knowledge/`
    were templates, and 3 of them were not touched once in 30 days. Counting a template
    as durable knowledge inflated the cortex with someone else's starter-kit material.

    `artifact` exists so that UNDEFINED does not lie. Machine output has no type and
    never will; leaving it in undefined makes the number look like frontmatter debt when
    it is just the nature of the file. It stays out of the ratio, like operational.
    """
    if rel.startswith(ARTIFACT) or os.path.basename(rel) in ARTIFACT_NAME:
        return "artifact"
    if status == "template":
        return "operational"
    if os.path.basename(rel) in EXEMPT_NAME or rel.startswith(EXEMPT_FOLDER):
        return "operational"          # harness and navigation, not memory
    if any(rel.startswith(p) for p in CORTEX_FOLDER):
        return "cortex"
    if note_type in OPERATIONAL:
        return "operational"
    if note_type in CORTEX:
        return "cortex"
    if note_type in HIPPOCAMPUS:
        return "hippocampus"
    if any(rel.startswith(p) for p in HIPPOCAMPUS_FOLDER):
        return "hippocampus"
    if "/transcripts/" in rel or "/lessons/" in rel or "/logs/" in rel:
        return "hippocampus"
    return "undefined"


def cluster(rel):
    """Local cluster = the neighborhood that is already dense by construction.

    A project is its own cluster: linking two notes of the same project is a local
    link, not the long bridge that matters.
    """
    parts = rel.split("/")
    top = parts[0]
    if top in ("03 Projects",) and len(parts) > 1:
        return "%s/%s" % (top, parts[1])
    if top == "04 Resources" and len(parts) > 1:
        return "%s/%s" % (top, parts[1])
    return top


def is_summary(rel, note_type):
    return note_type in SUMMARY_TYPES or os.path.basename(rel)[:-3].lower() in SUMMARY_NAMES


def build_index():
    notes = {}
    for folder, subs, names in os.walk(ROOT):
        subs[:] = [s for s in subs if s not in IGNORE]
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            m = TYPE.search(text)
            note_type = m.group(1).strip().strip("\"'") if m else ""
            ms = STATUS.search(text)
            status = ms.group(1).strip().strip("\"'") if ms else ""
            notes[rel] = {
                "text": text,
                "type": note_type,
                "layer": layer(rel, note_type, status),
                "status": status,
                "cluster": cluster(rel),
                "summary": is_summary(rel, note_type),
            }
    return notes


def resolve_targets(notes):
    """Same resolution criteria as check-wikilinks: path, basename and alias."""
    idx = {}
    for rel, n in notes.items():
        idx.setdefault(rel[:-3].lower(), rel)
        idx.setdefault(os.path.basename(rel)[:-3].lower(), rel)
        m = ALIAS.search(n["text"])
        if m:
            for a in m.group(1).split(","):
                a = a.strip().strip("\"'").lower()
                if a:
                    idx.setdefault(a, rel)
    return idx


def edges(notes, idx):
    outgoing = {rel: set() for rel in notes}
    incoming = {rel: set() for rel in notes}
    pairs = []
    for rel, n in notes.items():
        text = INLINE.sub(" ", FENCE.sub(" ", COMMENT.sub(" ", n["text"])))
        for m in LINK.finditer(text):
            target = m.group(1).strip().rstrip("\\").strip().lower()
            if target.endswith(".md"):
                target = target[:-3]
            destination = idx.get(target)
            if destination and destination != rel:
                outgoing[rel].add(destination)
                incoming[destination].add(rel)
    for origin, destinations in outgoing.items():
        for destination in destinations:
            pairs.append((origin, destination))
    return outgoing, incoming, pairs


def measure():
    notes = build_index()
    idx = resolve_targets(notes)
    outgoing, incoming, pairs = edges(notes, idx)

    layers = {"cortex": [], "hippocampus": [], "operational": [], "artifact": [],
              "undefined": []}
    for rel, n in notes.items():
        layers[n["layer"]].append(rel)

    n_cortex, n_hippo = len(layers["cortex"]), len(layers["hippocampus"])
    ratio = (n_hippo / n_cortex) if n_cortex else float("inf")

    long_edges = [(a, b) for a, b in pairs if notes[a]["cluster"] != notes[b]["cluster"]]
    no_summary = [(a, b) for a, b in pairs
                  if not notes[a]["summary"] and not notes[b]["summary"]]
    long_no_summary = [(a, b) for a, b in no_summary
                       if notes[a]["cluster"] != notes[b]["cluster"]]

    degrees = {rel: len(outgoing[rel]) + len(incoming[rel]) for rel in notes}

    def is_artifact(rel):
        return rel.startswith(ARTIFACT) or os.path.basename(rel) in ARTIFACT_NAME

    prunable = [rel for rel in notes if not is_artifact(rel)]
    isolated = sorted(rel for rel in prunable if degrees[rel] == 0)
    no_incoming = sorted(rel for rel in prunable if not incoming[rel])
    no_type = sorted(rel for rel in prunable if not notes[rel]["type"]
                     and os.path.basename(rel) not in EXEMPT_NAME
                     and not rel.startswith(EXEMPT_FOLDER))

    sorted_degrees = sorted(degrees.values())
    median = sorted_degrees[len(sorted_degrees) // 2] if sorted_degrees else 0

    # Hot path is NOT location, it is reach by cue. Retrieval in the brain works by
    # trigger, not by search: a note cited by a loaded note is already within reach,
    # because the agent reads the cue and knows it exists. Counting only by folder would
    # make the metric reward MOVING files to `knowledge/`, which is exactly the mistake
    # the skill forbids (the hook has a 9,000 character ceiling and the folder is read
    # whole). So: 1 hop counts. More than 1 hop does not count: at that distance it is
    # already a search, and a search depends on someone remembering. The cheap fix is
    # always the one-line pointer in the loaded note.
    loaded = {r for r in notes if r.startswith(HOT)}
    within_reach = set(loaded)
    for r in loaded:
        within_reach |= outgoing[r]
    hot = [r for r in layers["cortex"] if r in within_reach]
    cold = [r for r in layers["cortex"] if r not in within_reach]
    in_folder = [r for r in layers["cortex"] if r in loaded]
    # Cold cortex sorted by what MOST notes pull: a note that 20 others cite and nobody
    # loads is the obvious candidate to become a pointer on the hot path.
    cold_pulled = sorted(cold, key=lambda r: -len(incoming[r]))

    return {
        "notes": len(notes),
        "artifacts": len(notes) - len([r for r in notes if not (r.startswith(ARTIFACT) or os.path.basename(r) in ARTIFACT_NAME)]),
        "edges": len(pairs),
        "mean_degree": round(sum(degrees.values()) / len(notes), 1) if notes else 0,
        "median_degree": median,
        "cortex": n_cortex,
        "hippocampus": n_hippo,
        "operational": len(layers["operational"]),
        "artifact_layer": len(layers["artifact"]),
        "undefined": len(layers["undefined"]),
        "consolidation_ratio": round(ratio, 1) if n_cortex else None,
        "long_edge_raw": round(100 * len(long_edges) / len(pairs), 1) if pairs else 0,
        "long_edge_no_summary": (
            round(100 * len(long_no_summary) / len(no_summary), 1) if no_summary else 0),
        "cortex_hot": len(hot),
        "cortex_in_folder": len(in_folder),
        "cortex_cold": len(cold),
        "hot_rate": round(100 * len(hot) / (len(hot) + len(cold)), 1) if layers["cortex"] else 0,
        "isolated": isolated,
        "no_incoming": no_incoming,
        "no_type": no_type,
        "undefined_notes": sorted(layers["undefined"]),
        "cortex_notes": sorted(layers["cortex"]),
        "cold_most_pulled": [(r, len(incoming[r])) for r in cold_pulled[:20]],
    }


def report(m, summary=False):
    if summary:
        print("consolidation: %s report notes for 1 knowledge note (%d hippocampus / %d cortex)"
              % (m["consolidation_ratio"], m["hippocampus"], m["cortex"]))
        print("hot path: %.1f%% of the cortex is within reach of a cue (%d of %d)"
              % (m["hot_rate"], m["cortex_hot"], m["cortex_hot"] + m["cortex_cold"]))
        print("long edge    : %.1f%% of the links cross clusters (summary notes excluded)"
              % m["long_edge_no_summary"])
        print("pruning      : %d isolated notes, %d with no type"
              % (len(m["isolated"]), len(m["no_type"])))
        return

    print("=" * 66)
    print("VAULT INTELLIGENCE METRICS")
    print("=" * 66)
    print("%d notes · %d edges · mean degree %.1f · median %d"
          % (m["notes"], m["edges"], m["mean_degree"], m["median_degree"]))

    print("\n--- 1. CONSOLIDATION (hippocampus -> cortex) ---")
    print("  cortex      (timeless statement) : %4d" % m["cortex"])
    print("  hippocampus (dated report)       : %4d" % m["hippocampus"])
    print("  operational (infra, out of ratio): %4d" % m["operational"])
    print("  artifact    (machine output)     : %4d" % m["artifact_layer"])
    print("  undefined   (no useful type)     : %4d" % m["undefined"])
    print("  RATIO: %s notes of raw material for each 1 of durable knowledge"
          % m["consolidation_ratio"])
    print("  It rises by consolidating (promoting an episode to a statement), never by capturing more.")

    print("\n--- 2. HOT PATH (cortex within reach of a cue) ---")
    print("  in the loaded folder     : %4d" % m["cortex_in_folder"])
    print("  + cited by it (1 hop)    : %4d" % (m["cortex_hot"] - m["cortex_in_folder"]))
    print("  out of reach             : %4d" % m["cortex_cold"])
    print("  RATE: %.1f%% of the durable knowledge is within reach" % m["hot_rate"])
    print("  Knowledge that nobody loads is knowledge that nobody uses.")
    print("  The fix is NOT moving files (the hook has a 9,000 character ceiling):")
    print("  it is adding a 1-line pointer in knowledge/index.md to the cold note.")
    if m["cold_most_pulled"]:
        print("  Cold notes most cited by other notes (pointer candidates):")
        for rel, n in m["cold_most_pulled"][:8]:
            print("    %3d incoming  %s" % (n, rel))

    print("\n--- 3. LONG EDGE (a link that crosses clusters) ---")
    print("  raw                  : %.1f%%" % m["long_edge_raw"])
    print("  without summary notes: %.1f%%   <- the honest one" % m["long_edge_no_summary"])
    print("  A summary links by trade; an idea connected to a distant idea is what counts.")

    print("\n--- 4. PRUNING ---")
    print("  isolated (degree 0)     : %4d" % len(m["isolated"]))
    print("  no incoming link        : %4d" % len(m["no_incoming"]))
    print("  no frontmatter `type`   : %4d" % len(m["no_type"]))
    print("  (%d machine artifacts left out of pruning: audit reports, conversations)"
          % m["artifacts"])
    print("  Run with --triage to see the list.")
    print("\nKnown gap: this measures anatomy, not use. An edge only becomes memory")
    print("when it is traveled; measuring traversal requires the session history.")


def triage(m):
    def block(title, items, note):
        print("\n--- %s (%d) ---" % (title, len(items)))
        print("    %s" % note)
        for rel in items:
            print("    %s" % rel)

    block("ISOLATED: nothing in, nothing out", m["isolated"],
          "binary decision: promote it (it gets a type and a link) or it goes to 05 Archives")
    block("NO TYPE", m["no_type"],
          "with no type the note does not show up in a frontmatter search: it exists and is invisible")
    block("UNDEFINED LAYER", m["undefined_notes"],
          "type present but not classifiable: either the type is new, or it is wrong")


def main():
    m = measure()
    if "--json" in sys.argv:
        output = dict(m)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif "--triage" in sys.argv:
        report(m)
        triage(m)
    else:
        report(m, summary="--summary" in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
