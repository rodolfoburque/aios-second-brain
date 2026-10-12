#!/usr/bin/env python3
"""
AIOS Session Capture Hook

Fires on Stop. Asks the AI to persist the session in the daily note before the
turn ends.

The old version (a print in PreCompact) had a dead channel, and the self test
proved it: 631 chars written, zero read.

WHY Stop AND NOT PreCompact
---------------------------
This hook used to run on PreCompact, writing the reminder with print() and
exiting with code 0. Per the Claude Code hooks spec, only UserPromptSubmit,
UserPromptExpansion and SessionStart put the hook's stdout into the model's
context. Everything else, PreCompact included, sends stdout to the transcript
and nobody reads it. In other words: the reminder was written and read zero
times. It is the same defect that made session-start.py do nothing when it was
on PreToolUse.

Stop is the only lifecycle event with a documented channel back into the
conversation: returning {"decision": "block", "reason": "..."} prevents the stop
and hands the `reason` to the AI as an instruction for what to do now. That is
the mechanism, not stdout.

TWO GUARDS, AND WHY THE FIRST IS NOT ENOUGH
-------------------------------------------
1. stop_hook_active. Blocking Stop makes the AI work and try to stop again.
   Without this guard it becomes an infinite loop. The payload carries
   stop_hook_active: true from the second attempt onward WITHIN THE SAME TURN,
   so the guard exits with 0 and lets that turn finish.

   Careful: the flag resets every turn. Guard 1 prevents a loop, not repetition.

2. Daily note freshness. Firing on every turn is noise, including on the turns
   that just wrote the daily note. So if today's note was modified in the last
   FRESH_MINUTES, the session is already being persisted and the hook exits
   silently. The reminder only shows up when persistence has really gone stale.

Anti-recursion guard: the automatic documentation in session-end.py calls
headless 'claude -p', which fires the hooks again. AIOS_DOCUMENTING=1 makes it
exit early.

Output is ASCII only on purpose: on Windows the console uses cp1252 and a raw
non-ASCII character breaks the write.
"""
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

# Vault root = parent of .claude/hooks/ (no absolute path, works on any machine)
VAULT = Path(__file__).resolve().parent.parent.parent

FRESH_MINUTES = 20


def main() -> int:
    # Never runs inside its own headless documentation run.
    if os.environ.get("AIOS_DOCUMENTING") == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Without a readable payload the guard cannot be checked. Staying
        # silent is better than risking a loop.
        return 0

    if payload.get("stop_hook_active"):
        return 0

    today = date.today().isoformat()

    note = VAULT / "01 Daily" / f"{today}.md"
    try:
        if (time.time() - note.stat().st_mtime) < FRESH_MINUTES * 60:
            return 0
    except OSError:
        # The note does not exist yet or cannot be read. That is exactly when
        # the reminder is worth it, so carry on.
        pass

    reason = (
        f"[AIOS Session Capture] Before you finish: persist this session in "
        f"01 Daily/{today}.md.\n\n"
        "Add a `## Session` entry with:\n"
        "- **Decisions made:** real decisions from this session\n"
        "- **What was done:** concrete actions carried out\n"
        "- **Learnings:** what worked, what failed, what was discovered\n"
        "- **Next steps:** pending actions, specific and dated\n\n"
        "Then route the rest to the right place: an important decision goes to "
        "03 Intelligence/decisions/, a new project state goes to the project "
        "note, a correction the user gave you becomes a permanent rule in "
        "02 Context/me.md. When in doubt, check AIOS/knowledge-routing.md.\n\n"
        "If the session was only conversation and there is nothing worth "
        "keeping, say so in one line and stop. Do not invent an entry to "
        "satisfy the hook."
    )

    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
