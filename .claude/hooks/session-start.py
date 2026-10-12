#!/usr/bin/env python3
"""
AIOS Session Start Hook

Injects the vault's core context at the start of every Claude Code session.

IMPORTANT: fires on the SessionStart event. SessionStart stdout IS injected into
the model's context. The old event (PreToolUse) does NOT inject stdout into the
context, which is why the agent looked "not connected" even with the hook running.

Robustness rules:
- Output always under 10,000 characters (the per-hook limit). Ceiling of 9,000 here.
- No dependency on /tmp (it does not exist on native Windows). SessionStart runs
  once per session, so no lock is needed.
- Always read as utf-8. Every file operation tolerates failure without breaking.
- The vault is detected from this file's location, with no absolute paths.

Even if this hook fails (no python, for example), the agent still connects:
CLAUDE.md (always loaded by Claude Code) tells the AI to read these files.
"""
import os
import re
import sys
from datetime import date
from pathlib import Path

# Windows uses cp1252 on stdout by default and breaks on any character outside
# Latin-1 (e.g. the U+2192 arrow coming from vault content). Force UTF-8 here
# so the context is injected without UnicodeEncodeError. Tolerates failure.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Anti-recursion guard: the automatic end-of-session documentation calls
# headless 'claude -p', which fires SessionStart again. On that run, exit.
if os.environ.get("AIOS_DOCUMENTING") == "1":
    sys.exit(0)

# Consume the hook's stdin (the SessionStart JSON) without depending on it.
try:
    sys.stdin.read()
except Exception:
    pass

# Vault root = parent of .claude/hooks/
VAULT = Path(__file__).resolve().parent.parent.parent

CHAR_BUDGET = 9000  # safety margin under the 10k per-hook limit

TRUNCATED = "\n[... truncated, read the whole file if you need it ...]"


def read_capped(rel_path, limit):
    p = VAULT / rel_path
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return None
    if len(text) > limit:
        text = text[:limit] + TRUNCATED
    return text


def detect_mode():
    op = VAULT / "02 Context" / "operator.md"
    org = VAULT / "02 Context" / "organization.md"
    return "team" if (op.exists() and org.exists()) else "solo"


def latest_daily():
    d = VAULT / "01 Daily"
    if not d.exists():
        return None
    files = sorted(d.glob("????-??-??.md"), reverse=True)
    return files[0] if files else None


def last_session_block(path, limit, titles_budget=600):
    """Return the LAST `## Session` block of the daily note, not the top of the file.

    The daily note accumulates sessions by APPEND: the first one of the day sits
    at the top and the most recent at the bottom. Cutting `text[:limit]` handed
    over the OLDEST session under the "Last Session" label: on a 20-session day
    the agent opened the next session with a status 19 sessions old.

    Returns (text, index_of_last, total). With no `## Session` in the file (a
    freshly created daily note, or an older format), returns the top, as before.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None, 0, 0

    # The chronological chain footer is not session content. Anchored to the
    # start of a LINE on purpose: the session that documents this hook quotes
    # the marker in prose, and a raw split() truncated the daily note there and
    # swallowed every session after it.
    cut = re.search(r"^<!-- daily-chain -->", text, re.MULTILINE)
    if cut:
        text = text[:cut.start()]
    text = text.rstrip().rstrip("-").rstrip()

    marks = [m.start() for m in re.finditer(r"^## Session", text, re.MULTILINE)]
    if not marks:
        if len(text) > limit:
            text = text[:limit] + TRUNCATED
        return text, 0, 0

    total = len(marks)
    block = text[marks[-1]:].rstrip()
    if len(block) > limit:
        block = block[:limit] + TRUNCATED

    # titles of the earlier ones, most recent first: the day is not lost
    if total > 1:
        earlier = []
        spent = 0
        for i in range(total - 2, -1, -1):
            end = text.find("\n", marks[i])
            title = text[marks[i]:end if end != -1 else len(text)].strip()
            title = title.lstrip("#").strip()
            if title.startswith("Session"):
                title = title[len("Session"):].strip(" -")
            if spent + len(title) + 3 > titles_budget:
                earlier.append("...")
                break
            earlier.append(title)
            spent += len(title) + 3
        block += "\n\nBefore it today (most recent first): " + " | ".join(earlier)

    return block, total, total


def ensure_today_daily():
    today = date.today().isoformat()
    d = VAULT / "01 Daily"
    try:
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{today}.md"
        if not f.exists():
            f.write_text(
                f"---\ntype: daily\ndate: {today}\nstatus: active\ntags: [daily]\n---\n",
                encoding="utf-8",
            )
    except Exception:
        pass
    return today


header = "[AIOS Session Start] You are the personal AI that operates this vault. Context loaded below.\n"
parts = [header]
used = len(header)


def add(block):
    global used
    if used + len(block) < CHAR_BUDGET:
        parts.append(block)
        used += len(block)


# 1. Identity (top priority, it is what makes the agent "know you")
if detect_mode() == "team":
    identity = [
        ("02 Context/operator.md", "Operator", 2500),
        ("02 Context/organization.md", "Organization", 2500),
    ]
else:
    identity = [("02 Context/me.md", "Identity", 4000)]

for rel, label, lim in identity:
    txt = read_capped(rel, lim)
    if txt:
        add(f"--- {label} ({rel}) ---\n{txt}\n")

# 2. Last session (continuity)
ld = latest_daily()
if ld:
    txt, idx, total = last_session_block(ld, 2000)
    if txt:
        position = f" - session {idx} of {total}" if total else ""
        add(f"--- Last Session ({ld.stem}{position}) ---\n{txt}\n")

# 3. Pointers to the rest (read on demand by the AI)
add(
    "--- Read on demand ---\n"
    "- AIOS/index.md (available skills and commands)\n"
    "- AIOS/operating-rules.md (how to operate in this vault)\n"
    "- AIOS/knowledge-routing.md (where to save each thing)\n"
    "- knowledge/index.md (permanent knowledge)\n"
)

# 3.5 Graph state. A WARNING, NEVER A GATE.
#
# Once the graph reaches zero dead links, without measurement it drifts again in
# silence. The temptation was to turn this into a pre-commit hook; that was
# dropped for three reasons:
#   - a forward link is LEGITIMATE here. vault-lint itself says to create a note
#     after 3 mentions, so a dead link is a sign of a note to write, not an error.
#     block-secret-on-commit can block because a secret has no legitimate case; a
#     wikilink does.
#   - the checker had just been fixed for 5 defects that made it overestimate by
#     2.2x. A freshly repaired tool does not become a gate the next day; it needs
#     mileage first.
#   - the damage it catches is cosmetic and reversible (a link that does not open).
#     A leaked secret is irreversible. The cost of blocking wrongly does not pay
#     for the benefit.
# So: measure once per session (0.85s), inform, and the decision stays with you.
NL = chr(10)
try:
    import subprocess
    _r = subprocess.run(
        [sys.executable, str(VAULT / "04 Resources" / "tools" / "check-wikilinks.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
        cwd=str(VAULT),
    )
    _summary = [l.strip() for l in _r.stdout.splitlines()
                if ":" in l and "occurrences" in l and not l.strip().startswith("0 targets")]
    _dirty = [l for l in _summary if not l.split(":")[1].strip().startswith("0 targets")]
    if _dirty:
        _cmd = chr(96) + 'python "04 Resources/tools/check-wikilinks.py"' + chr(96)
        add("--- Vault graph ---" + NL + NL.join(_dirty) + NL
            + "Run " + _cmd + " to see where. "
            + "A warning, not a block: a forward link is legitimate." + NL)
except Exception:
    pass  # a hook that breaks the session over a warning is worse than no warning

# 3.6 Intelligence metrics. A WARNING, NEVER A GATE, same doctrine as 3.5.
#
# 3.5 measures INTEGRITY (does the link open?). Integrity at zero does not mean a
# smart vault: you can have zero dead links and still be a warehouse of dated
# reports. `vault-metrics.py` measures the two ratios that were missing,
# consolidation (cortex over hippocampus) and hot path (how much of the cortex the
# agent loads on its own), and the second one is what finds the real defect: a
# knowledge note that many notes link to and nothing loads. It is not a gate
# because neither ratio has a "wrong" value that justifies stopping work; it is a
# trend thermometer, read over weeks.
try:
    import subprocess
    _m = subprocess.run(
        [sys.executable, str(VAULT / "04 Resources" / "tools" / "vault-metrics.py"),
         "--summary"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
        cwd=str(VAULT),
    )
    _lines = [l.rstrip() for l in _m.stdout.splitlines() if l.strip()]
    if _lines:
        _cmd = chr(96) + 'python "04 Resources/tools/vault-metrics.py" --triage' + chr(96)
        add("--- Vault intelligence ---" + NL + NL.join(_lines) + NL
            + "Consolidate an episode into a claim: " + chr(96) + "/consolidate" + chr(96)
            + ". Pruning list: " + _cmd + "." + NL)
except Exception:
    pass


# 4. Make sure today's daily note exists + documentation instruction
today = ensure_today_daily()
add(
    f"--- Documentation ---\n"
    f"Today's note exists at `01 Daily/{today}.md`. Record real decisions in it "
    f"or in `03 Intelligence/decisions/` as you work.\n"
)

sys.stdout.write("\n".join(parts))
