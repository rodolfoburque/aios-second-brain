#!/usr/bin/env python3
"""PreToolUse: blocks killing a process BY NAME (node, python, claude).

WHY IT EXISTS (a real failure in the vault this template came from)
-------------------------------------------------------------------
While testing an agent's keep-alive, `Stop-Process -Name node` was run to prove that the
supervisor brings the process back up. It worked, and it also took down THREE Claude Code
MCP servers: one of them went down and only came back with /mcp by hand. `node` and `python`
are the runtime of half the things running on a machine like this: agents, scheduled tasks,
the MCPs and Claude Code itself.

Killing by PID stays allowed: it is surgical, it targets ONE known process. What this hook
stops is the version that hits everything sharing the runtime.

To stop one of your own services without killing the runtime, register the right command in
SERVICES, just below. The list only changes the help message; what gets blocked does not
depend on it.

Hook contract: reads JSON on stdin, exit 0 allows, exit 2 BLOCKS and the stderr text goes
back to the agent explaining why. UTF-8 forced on I/O (the vault standard on Windows).
"""
import json
import re
import sys

# Each pattern targets one way of killing by NAME. `-Id`/`/PID` are left out on purpose.
PATTERNS = [
    (r"stop-process\b[^|;\r\n]*-name\b", "Stop-Process -Name"),
    (r"\btaskkill\b[^|;\r\n]*/im\b", "taskkill /IM"),
    (r"\b(pkill|killall)\b", "pkill/killall"),
    (r"get-process\b[^|\r\n]*\|[^|\r\n]*stop-process", "Get-Process | Stop-Process"),
]

TARGETS = r"(node|python|pythonw|claude|npm|pwsh|powershell)"

# CONFIGURABLE: services on this machine that run on top of a shared runtime, with the
# right command to stop each one. It goes into the block message as an alternative. Examples:
#   ("the support agent",  'Stop-ScheduledTask -TaskName "<task name>"'),
#   ("the queue worker",   "systemctl --user stop <service-name>"),
SERVICES = []


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # an unreadable payload is no reason to block the user's work

    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "")
    if not command:
        sys.exit(0)

    lowered = command.lower()
    for pattern, label in PATTERNS:
        if re.search(pattern, lowered) and re.search(TARGETS, lowered):
            alternatives = "".join(
                "  - stop %s: %s\n" % (name, how) for name, how in SERVICES
            )
            sys.stderr.write(
                f"BLOCKED by the vault hook: `{label}` targeting a shared runtime.\n\n"
                "Killing by name also takes down the MCP servers, the agents and the "
                "scheduled tasks that use the same runtime (it has happened: an MCP went "
                "down and only came back by hand).\n\n"
                "Alternatives:\n"
                + alternatives
                + "  - stop a scheduled task: Stop-ScheduledTask -TaskName \"<name>\"\n"
                "  - kill ONE process: Stop-Process -Id <pid>  (targets only that one)\n"
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
