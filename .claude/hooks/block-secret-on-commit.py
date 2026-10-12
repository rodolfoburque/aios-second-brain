#!/usr/bin/env python3
"""PreToolUse: blocks a `git commit` that carries a secret or a .env file.

WHY IT EXISTS
-------------
The rule "a secret never goes in a versioned file" is in CLAUDE.md. A rule in
prose does not stop a commit: this hook scans for token patterns and ABORTS
before anything is published.

WHAT IT LOOKS AT
----------------
Not the command text, which says nothing: the CONTENT THAT IS GOING IN. It reads
`git diff --cached` (and the unstaged diff too when the command has `-a`, because
`-a` stages at commit time) and examines only the ADDED lines. A context line
does not count: a secret that is already in history is a different problem, and
blocking today's commit does not solve it.

TWO GATES
---------
1. A `.env` file entering the index. There is no legitimate case: `.env.example`
   passes, the rest does not.
2. The shape of a real secret in the added lines (OpenAI, Anthropic, GitHub, AWS,
   Google, Stripe, Slack, Asaas, Meta keys, a private key block, a service_role
   JWT, and an assignment with a long value).

FALSE POSITIVES
---------------
A hook that cries wolf is a hook its owner turns off. So: only added lines, a
recognized placeholder does not count (`your-`, `xxx`, `<...>`, `changeme`,
`REDACTED`, `example`), and there is a documented way out in the block message
itself (`ALLOW_SECRET=1`), for when the finding is false and the work cannot
stop.

Hook contract: reads JSON on stdin, exit 0 allows, exit 2 BLOCKS and the stderr
text goes back to the agent. UTF-8 forced on I/O (the vault standard on Windows).

Check it:  python .claude/hooks/block-secret-on-commit.py --selftest
"""
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Secret shapes with their own prefix: they rarely match by accident.
PATTERNS = [
    (r"sk-ant-[A-Za-z0-9_-]{20,}", "Anthropic key"),
    (r"\bsk-(?!ant-)[A-Za-z0-9]{20,}", "OpenAI key"),
    (r"\bsk_live_[A-Za-z0-9]{16,}", "Stripe live key"),
    (r"\brk_live_[A-Za-z0-9]{16,}", "Stripe live restricted key"),
    (r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "Google API key"),
    (r"\$aact_[A-Za-z0-9_=+/-]{20,}", "Asaas key"),
    (r"\bEAA[A-Za-z0-9]{40,}", "Meta/WhatsApp token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", "signed JWT"),
    # Last resort: an explicit assignment with a long quoted value.
    (r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|"
     r"client[_-]?secret|service[_-]?role|senha|password)\b\s*[:=]\s*"
     r"[\"'][^\"'\s]{16,}[\"']", "credential assignment with a long value"),
]

# If the line looks like an example, it is not a leak.
PLACEHOLDER = re.compile(
    r"(?i)(your[-_]|my[-_]|xxx+|\.\.\.|<[a-z_ -]+>|\{\{|changeme|troque|"
    r"exemplo|example|placeholder|redacted|dummy|fake|sample|\*{4,}|"
    r"cole[- ]aqui|preencha)")

ENV_FORBIDDEN = re.compile(r"(^|/)\.env(\.|$)")
ENV_ALLOWED = re.compile(r"(^|/)\.env\.(example|sample|template)$")

# `git` only counts in COMMAND POSITION: the start of the string, or after a
# shell separator. Without that, a command that merely MENTIONS "git commit"
# inside quotes (documenting, testing, grepping) was blocked. It happened on
# this file's own first commit.
# Between `git` and `commit` there can be any token (`-c user.name=t`, `-C dir`),
# but no shell separator: `git status; echo commit` is not a commit. And
# `commit` has to be its own token, otherwise `git log --grep=commit` fired.
RE_GIT_COMMIT = re.compile(
    r"(?:^|[;&|]|\n)\s*(?:[a-z_][a-z0-9_]*=\S*\s+)*git\s+"
    r"(?:[^\s;&|]+\s+)*?commit(?:\s|$)")

# The emergency exit has to be IN THE COMMAND TEXT. The hook runs in a separate
# process and gets Claude Code's environment, not the shell's: an
# `ALLOW_SECRET=1 git commit ...` would never arrive here as a variable. The
# first version of this message promised exactly that and was wrong.
RE_ALLOW = re.compile(r"\bALLOW_SECRET=1\b")


def allowed(command):
    return bool(RE_ALLOW.search(command)) or os.environ.get("ALLOW_SECRET") == "1"


def _git(args, cwd):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=30)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def findings(cwd, include_unstaged=False):
    """Return (leaks, envs). Only ADDED lines are considered."""
    scopes = [["diff", "--cached", "-U0"]]
    if include_unstaged:
        scopes.append(["diff", "-U0"])

    leaks, envs, filename = [], [], "?"
    for scope in scopes:
        for line in _git(scope, cwd).splitlines():
            if line.startswith("+++ b/"):
                filename = line[6:].strip()
                if ENV_FORBIDDEN.search(filename) and not ENV_ALLOWED.search(filename):
                    if filename not in envs:
                        envs.append(filename)
                continue
            if not line.startswith("+") or line.startswith("+++"):
                continue
            body = line[1:]
            for i, (pattern, label) in enumerate(PATTERNS):
                m = re.search(pattern, body)
                if not m:
                    continue
                snippet = m.group(0)
                # A placeholder INSIDE the token itself is always an example
                # (`sk-your-key-here`, `AKIAIOSFODNN7EXAMPLE`).
                if PLACEHOLDER.search(snippet):
                    break
                # A placeholder anywhere else on the line only clears the last
                # pattern, which is the generic one. A key with its own prefix
                # gets no pardon for having the word "example" in the comment
                # next to it: that was the hole the self test opened.
                if i == len(PATTERNS) - 1 and PLACEHOLDER.search(body):
                    break
                if len(snippet) > 24:
                    snippet = snippet[:12] + "..." + snippet[-4:]
                leaks.append((filename, label, snippet))
                break
    return leaks, envs


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # an unreadable payload is no reason to block the work

    command = str((payload.get("tool_input") or {}).get("command") or "")
    lowered = command.lower()
    # Fast exit: this hook runs on EVERY Bash/PowerShell call.
    if "git" not in lowered or "commit" not in lowered:
        sys.exit(0)
    if not RE_GIT_COMMIT.search(lowered):
        sys.exit(0)
    if allowed(command):
        sys.exit(0)

    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
    has_a = bool(re.search(r"\bcommit\b[^|;&\r\n]*\s-(?:a|[a-z]*a[a-z]*)\b|--all\b", lowered))
    leaks, envs = findings(cwd, include_unstaged=has_a)

    if not leaks and not envs:
        sys.exit(0)

    out = ["BLOCKED by the vault hook: this commit carries a secret into the repo.\n"]
    if envs:
        out.append(".env file entering the index:")
        for a in envs:
            out.append("  - %s" % a)
        out.append("")
    if leaks:
        out.append("Credential shape on an ADDED line:")
        for fname, label, snippet in leaks[:12]:
            out.append("  - %s  ->  %s  (`%s`)" % (fname, label, snippet))
        if len(leaks) > 12:
            out.append("  ... and %d more" % (len(leaks) - 12))
        out.append("")
    out.append("How to fix it, in this order:")
    out.append("  1. take it out of the index:   git restore --staged <file>")
    out.append("  2. move the value to .env (which is in .gitignore) and read it from an env var")
    out.append("  3. if the key has already leaked anywhere, ROTATE it before moving on")
    out.append("")
    out.append("If the finding is false, write ALLOW_SECRET=1 inside the command")
    out.append("itself (the hook reads the text, not the shell environment):")
    out.append('  ALLOW_SECRET=1 git commit -m "..."')
    sys.stderr.write("\n".join(out) + "\n")
    sys.exit(2)


# --------------------------------------------------------------------------- #
def selftest():
    """Build real temporary repos and check both blocking and allowing."""
    import shutil
    import tempfile
    failures = []

    def expect(cond, what):
        print(("  OK     " if cond else "  FAILED ") + what)
        if not cond:
            failures.append(what)

    def repo_with(files):
        d = tempfile.mkdtemp(prefix="secret-test-")
        subprocess.run(["git", "init", "-q"], cwd=d, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=d, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=d, capture_output=True)
        for name, content in files.items():
            p = os.path.join(d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True) if "/" in name else None
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(content)
        subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
        return d

    # The test keys are built by CONCATENATION on purpose. Written out whole,
    # this file would match its own patterns and the hook would block the commit
    # of itself (it happened, on the first attempt). Do not join the pieces: the
    # value in memory is identical, it is the text on disk that is not.
    cases = [
        ("OpenAI key in code", True,
         {"app.py": 'KEY = "sk-' + 'proj0000111122223333444455556666"\n'}),
        ("GitHub token in a note", True,
         {"note.md": "the token is ghp_" + "0123456789abcdefghijABCDEFGHIJ0123\n"}),
        ("AWS access key", True, {"cfg.txt": "AKIA" + "3QK7ZB2XW9MTLDVR\n"}),
        ("real key with 'example' in the comment", True,
         {"note.md": "sk-ant-" + "api03abcdefghijklmnop0123456789  # example of use\n"}),
        ("AWS docs key does not block", False,
         {"doc.md": "use the format AKIAIOSFODNN7EXAMPLE\n"}),
        ("private key block", True,
         {"id.pem": "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIE\n"}),
        (".env file entering", True, {".env": "PORT=3000\n"}),
        (".env nested in site/", True, {"site/.env": "PORT=3000\n"}),
        ("Asaas key", True,
         {"pay.js": "const k = '$aact_" + "YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5'\n"}),
        ("placeholder does not block", False,
         {".env.example": 'OPENAI_KEY="sk-your-key-here-xxxxxxxxxxxx"\n'}),
        ("ordinary note does not block", False,
         {"journal.md": "today I touched the project's API key and rotated it\n"}),
        ("code reading an env var does not block", False,
         {"app.py": 'KEY = os.environ["OPENAI_API_KEY"]\n'}),
    ]

    print("gates (a real git repo, a real commit stopped before it happens)")
    for name, should_block, files in cases:
        d = repo_with(files)
        try:
            leaks, envs = findings(d)
            blocked = bool(leaks or envs)
            expect(blocked == should_block,
                   "%-38s %s" % (name, "blocked" if blocked else "passed"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    print("\na CONTEXT line does not fire (an old secret does not block today's commit)")
    d = repo_with({"app.py": 'K = "sk-' + 'proj0000111122223333444455556666"\nx = 1\n'})
    try:
        subprocess.run(["git", "commit", "-q", "-m", "base", "--no-verify"],
                       cwd=d, capture_output=True)
        with open(os.path.join(d, "app.py"), "a", encoding="utf-8") as fh:
            fh.write("y = 2\n")
        subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
        leaks, envs = findings(d)
        expect(not leaks and not envs, "only the new line went in, the old secret is context")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("\ntrigger: only `git commit` in COMMAND POSITION fires")
    for cmd, should_fire in [
        ("ls -la", False),
        ("npm run build", False),
        ("git status", False),
        ("git add -A", False),
        ('echo "run git commit -m x"', False),          # only mentions it
        ('python h.py <<< \'{"cmd":"git commit -m t"}\'', False),  # test payload
        ("git commit -m 'x'", True),
        ("git add -A && git commit -m 'x'", True),
        ("git -c user.name=t commit -m 'x'", True),
        ("git log --grep=commit", False),
        ("git status; echo commit", False),
        ("ALLOW_SECRET=1 git commit -m 'x'", True),   # fires, and the exit allows it afterwards
    ]:
        fired = bool(RE_GIT_COMMIT.search(cmd.lower()))
        expect(fired == should_fire,
               "%-46s %s" % ("`%s`" % cmd, "fires" if fired else "ignores"))

    print("\nemergency exit (reads the command TEXT, not the environment)")
    expect(allowed("ALLOW_SECRET=1 git commit -m 'x'"), "prefix in the command allows")
    expect(not allowed("git commit -m 'x'"), "a normal commit does not allow")

    n_block = sum(1 for _, b, _ in cases if b)
    n_free = len(cases) - n_block
    print("\n%s" % ("PASSED: blocks the %d real cases and allows the %d legitimate ones."
                    % (n_block, n_free) if not failures
                    else "FAILED on %d: %s" % (len(failures), "; ".join(failures))))
    return 1 if failures else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
