#!/usr/bin/env python3
"""
AIOS Session End Hook (OPT-IN automatic documentation)

Fires on SessionEnd. By default it does NOTHING (instant exit, zero cost).
It only runs if automatic documentation is turned ON, which avoids two problems
that used to cause complaints: blocking the session exit and silently spending
your tokens.

How to turn automatic documentation on:
  - create the file `AIOS/autodoc.enabled` in the vault, OR
  - export the env var AIOS_AUTODOC=1

When on: reads the transcript, summarizes it through headless Claude (claude -p,
60s timeout) and writes to 01 Daily/TODAY.md. If the summary fails, it exits
silently (it does not write junk).

Anti-recursion guard: the headless claude call fires the hooks again. The env var
AIOS_DOCUMENTING=1 (set on the subprocess) makes the hooks exit early.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# Never runs inside its own documentation run (avoids a loop).
if os.environ.get("AIOS_DOCUMENTING") == "1":
    sys.exit(0)

# Vault root = parent of .claude/hooks/ (no dependency on an env var)
VAULT = Path(__file__).resolve().parent.parent.parent


def autodoc_enabled():
    if os.environ.get("AIOS_AUTODOC") == "1":
        return True
    return (VAULT / "AIOS" / "autodoc.enabled").exists()


# OPT-IN: off by default. Instant exit, no claude -p.
if not autodoc_enabled():
    sys.exit(0)


def read_hook_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def extract_conversation(path, max_chars=120000):
    """Extract user + assistant text from the JSONL transcript."""
    out = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message") or obj
                role = msg.get("role") or obj.get("type") or ""
                if role not in ("user", "assistant"):
                    continue
                content = msg.get("content")
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text += block.get("text", "")
                if text.strip():
                    out.append(f"[{role}] {text.strip()}")
    except Exception:
        return ""
    convo = "\n\n".join(out)
    if len(convo) > max_chars:
        convo = "(start truncated)\n\n" + convo[-max_chars:]
    return convo


def find_claude():
    c = shutil.which("claude")
    if c:
        return c
    candidates = [
        "/opt/homebrew/bin/claude",
        os.path.expanduser("~/.claude/local/claude"),
        "/usr/local/bin/claude",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def summarize(convo):
    claude = find_claude()
    if not claude:
        return None
    prompt = (
        "Summarize this work session for an Obsidian daily note. "
        "Use exactly this format, in the language of the conversation "
        "(default English), concise and specific:\n\n"
        "**Decisions made:** (real decisions from this session, or 'none')\n"
        "**What was done:** (concrete actions carried out)\n"
        "**Learnings:** (what worked, what failed)\n"
        "**Next steps:** (pending actions)\n\n"
        "Do not invent anything. Base it only on what is in the conversation below.\n\n"
        "=== CONVERSATION ===\n" + convo
    )
    env = dict(os.environ)
    env["AIOS_DOCUMENTING"] = "1"
    try:
        result = subprocess.run(
            [claude, "-p", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def write_to_daily(summary):
    today = date.today().isoformat()
    daily_dir = VAULT / "01 Daily"
    try:
        daily_dir.mkdir(parents=True, exist_ok=True)
        daily_path = daily_dir / f"{today}.md"
        ts = datetime.now().strftime("%H:%M")
        if not daily_path.exists():
            daily_path.write_text(
                f"---\ntype: daily\ndate: {today}\nstatus: active\ntags: [daily]\n---\n",
                encoding="utf-8",
            )
        entry = f"\n\n## Session {ts}\n\n{summary}\n"
        with open(daily_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def main():
    hook = read_hook_input()
    transcript_path = hook.get("transcript_path", "")

    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    convo = extract_conversation(transcript_path)
    if not convo.strip():
        sys.exit(0)

    summary = summarize(convo)
    if not summary:
        # Failed: exit silently instead of dirtying the daily note with a placeholder.
        sys.exit(0)

    write_to_daily(summary)


if __name__ == "__main__":
    main()
