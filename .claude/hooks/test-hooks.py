#!/usr/bin/env python3
"""
AIOS Hook Self Test

Runs the hooks for real and checks what they return. It does not read the code
and guess, it executes and measures.

Two things to know about how this vault is wired:
  1. PreToolUse is in ALLOWED_EVENTS: this vault has its own locks
     (block-kill-by-name, block-secret-on-commit) that speak through
     exit 2 + stderr, the documented blocking channel of PreToolUse. They must
     stay SILENT on stdout, and case 3 checks exactly that.
  2. settings.json is the default (`python3 -c` one-liners, shell-agnostic) and
     settings-windows.json is the same file with `python`. The Windows file is
     optional for this test: when it exists, the test covers it automatically.

How to run:
    python .claude/hooks/test-hooks.py       (Windows)
    python3 .claude/hooks/test-hooks.py      (Mac and Linux)

Exits with code 0 if everything passed, 1 if any case failed. That exit code is
the proof: "passed" printed on screen is worth nothing if the exit is 1.

CASE 3 IS THE REASON THIS FILE EXISTS
-------------------------------------
Only four paths talk to the AI:
  - SessionStart, UserPromptSubmit, UserPromptExpansion: the hook's stdout
    enters the model's context.
  - Stop: it is not stdout. It returns {"decision": "block", "reason": "..."}
    and the reason becomes an instruction.
On any other event the print() goes to the transcript and nobody reads it. The
hook runs, exits with code 0, looks healthy, and does nothing. This mistake has
already been made twice in this codebase (session-start.py on PreToolUse,
session-capture.py on PreCompact). Case 3 runs every configured hook and fails
any one that writes to stdout on an event that delivers stdout to nobody.

Output is ASCII only on purpose: on Windows the console uses cp1252 and a raw
non-ASCII character breaks the write.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
VAULT = HOOKS_DIR.parent.parent
SETTINGS = HOOKS_DIR.parent / "settings.json"
SETTINGS_WIN = HOOKS_DIR.parent / "settings-windows.json"

# Events whose stdout the model actually reads.
STDOUT_CHANNELS = {"SessionStart", "UserPromptSubmit", "UserPromptExpansion"}
# Stop speaks through the decision key, not loose stdout.
DECISION_CHANNEL = "Stop"
# PreToolUse speaks through exit 2 + stderr (a block), never stdout.
ALLOWED_EVENTS = STDOUT_CHANNELS | {DECISION_CHANNEL, "SessionEnd", "PreToolUse"}

results = []


def check(name, passed, evidence):
    results.append((name, passed, evidence))
    print(("PASS  " if passed else "FAIL  ") + name)
    print("      " + evidence)


def run_hook(script, payload, env_extra=None):
    """Run a hook and return (exit_code, stdout, stderr)."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


def load_events(path):
    """Return [(event, script_path)] from a settings.json."""
    out = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for event, groups in data.get("hooks", {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                for candidate in HOOKS_DIR.glob("*.py"):
                    if candidate.name in cmd:
                        out.append((event, candidate))
    return out


class DailyNote:
    """Saves and restores the state of today's note, so the test does not dirty the vault."""

    def __init__(self):
        self.path = VAULT / "01 Daily" / f"{date.today().isoformat()}.md"
        self.existed = self.path.exists()
        self.backup = None
        self.mtime = None
        if self.existed:
            self.backup = self.path.read_bytes()
            self.mtime = self.path.stat().st_mtime

    def write_with_age(self, minutes_old):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("test\n", encoding="utf-8")
        stamp = time.time() - minutes_old * 60
        os.utime(self.path, (stamp, stamp))

    def remove(self):
        if self.path.exists():
            self.path.unlink()

    def restore(self):
        if self.existed:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_bytes(self.backup)
            os.utime(self.path, (self.mtime, self.mtime))
        else:
            self.remove()


def main():
    print("AIOS Hook Self Test")
    print("vault: " + str(VAULT))
    print("")

    # ---- 1. settings valid, events known, scripts exist ------------------
    settings_files = [SETTINGS]
    if SETTINGS_WIN.exists():
        settings_files.append(SETTINGS_WIN)
    for path in settings_files:
        if not path.exists():
            check("settings exists: " + path.name, False, "file not found")
            continue
        try:
            events = load_events(path)
        except json.JSONDecodeError as exc:
            check("settings is valid JSON: " + path.name, False, str(exc))
            continue
        check(
            "settings is valid JSON: " + path.name,
            True,
            str(len(events)) + " hook(s): " + ", ".join(e for e, _ in events),
        )
        unknown = [e for e, _ in events if e not in ALLOWED_EVENTS]
        check(
            "known events: " + path.name,
            not unknown,
            "all expected" if not unknown else "unexpected event: " + str(unknown),
        )

    events = load_events(SETTINGS)

    # ---- 2. every configured hook compiles -------------------------------
    for event, script in events:
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        check(
            "compiles: " + script.name,
            proc.returncode == 0,
            "py_compile exit=" + str(proc.returncode)
            + (" " + proc.stderr.strip()[:120] if proc.returncode else ""),
        )

    # ---- 3. the channel really exists (the case that catches the dead hook)
    note = DailyNote()
    try:
        for event, script in events:
            # Reset BEFORE EACH hook, not once for the whole loop.
            # session-start.py recreates today's note when it runs, so a single
            # reset would let session-capture see a fresh daily note, stay
            # silent, and PASS for having nothing to say. That is a false PASS:
            # the case never gets to test the channel.
            note.remove()
            code, out, _ = run_hook(script, {})
            spoke = bool(out.strip())

            if not spoke:
                check(
                    "channel ok: " + script.name + " on " + event,
                    True,
                    "does not write to stdout, delivers by file or has nothing to say",
                )
            elif event in STDOUT_CHANNELS:
                check(
                    "channel ok: " + script.name + " on " + event,
                    True,
                    str(len(out)) + " chars on stdout, and " + event + " injects stdout into the context",
                )
            elif event == DECISION_CHANNEL:
                try:
                    payload = json.loads(out)
                    ok = payload.get("decision") == "block" and bool(payload.get("reason"))
                    detail = "decision=" + str(payload.get("decision")) + ", reason=" + str(len(payload.get("reason", ""))) + " chars"
                except json.JSONDecodeError as exc:
                    ok, detail = False, "stdout is not decision JSON: " + str(exc)
                check("channel ok: " + script.name + " on " + event, ok, detail)
            else:
                check(
                    "channel ok: " + script.name + " on " + event,
                    False,
                    "DEAD HOOK: writes " + str(len(out)) + " chars to stdout, but "
                    + event + " does not deliver stdout to the AI. It runs, exits with 0, and nobody reads it.",
                )
    finally:
        note.restore()

    # ---- 4. session-start fits within the context limit ------------------
    start = HOOKS_DIR / "session-start.py"
    if start.exists():
        note = DailyNote()
        try:
            code, out, err = run_hook(start, {})
            check(
                "session-start injects context",
                code == 0 and 0 < len(out) < 10000,
                "exit=" + str(code) + ", " + str(len(out)) + " chars (Claude Code limit = 10000)",
            )
        finally:
            note.restore()

    # ---- 5. session-capture guards ---------------------------------------
    capture = HOOKS_DIR / "session-capture.py"
    if capture.exists():
        note = DailyNote()
        try:
            code, out, _ = run_hook(capture, {"stop_hook_active": True})
            check(
                "guard 1: stop_hook_active cuts the loop",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (expected 0)",
            )

            note.write_with_age(0)
            code, out, _ = run_hook(capture, {})
            check(
                "guard 2: fresh daily note, hook stays silent",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (expected 0)",
            )

            note.write_with_age(60)
            code, out, _ = run_hook(capture, {})
            try:
                payload = json.loads(out)
                ok = payload.get("decision") == "block"
                detail = "daily note 60 min old, decision=" + str(payload.get("decision"))
            except json.JSONDecodeError:
                ok, detail = False, "stale daily note but stdout is not JSON: " + repr(out[:80])
            check("guard 2 reversed: stale daily note, hook asks", ok and code == 0, detail)

            code, out, _ = run_hook(capture, {}, {"AIOS_DOCUMENTING": "1"})
            check(
                "guard 3: AIOS_DOCUMENTING cuts the recursion",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (expected 0)",
            )

            proc = subprocess.run(
                [sys.executable, str(capture)],
                input="this is not json",
                capture_output=True,
                text=True,
                timeout=30,
            )
            check(
                "invalid stdin does not take the session down",
                proc.returncode == 0 and not proc.stdout.strip(),
                "exit=" + str(proc.returncode) + ", stdout=" + str(len(proc.stdout)) + " chars",
            )

            note.write_with_age(60)
            _, out, _ = run_hook(capture, {})
            non_ascii = [c for c in out if ord(c) > 127]
            check(
                "ASCII output, survives cp1252 on Windows",
                not non_ascii,
                "no non-ASCII in the output" if not non_ascii else "characters that break: " + str(non_ascii[:10]),
            )
        finally:
            note.restore()

    # ---- scoreboard --------------------------------------------------------
    print("")
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print("=" * 60)
    print("RESULT: " + str(passed) + "/" + str(total) + " cases passed")
    if passed != total:
        print("")
        print("Failed:")
        for name, ok, evidence in results:
            if not ok:
                print("  - " + name + ": " + evidence)
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    if shutil.which(sys.executable) is None and not Path(sys.executable).exists():
        print("python not found")
        sys.exit(1)
    sys.exit(main())
