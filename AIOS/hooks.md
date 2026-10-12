---
type: map
status: active
date: 2026-08-05
tags: [aios, hooks, claude-code, portable]
---

## Hooks in this install

Configured in `.claude/settings.json` (project); they require `python3` on the PATH. On native Windows the command is usually `python`: copy `.claude/settings-windows.json` over `.claude/settings.json`, which is the same file with `python`. A user-level hook, in `~/.claude/settings.json`, is optional and this vault does not install any.

### Project hooks

- **`SessionStart`** → `.claude/hooks/session-start.py`: injects identity (`me.md`) + the latest daily note into the context at the start of the session. **`SessionStart` stdout enters the model's context.** The `PreToolUse` event, used before, does NOT inject stdout into the context, and that was why the agent looked disconnected. Output ceiling of 9,000 chars; anti-recursion guard through `AIOS_DOCUMENTING=1`; forces UTF-8 on stdout (Windows broke with UnicodeEncodeError on cp1252).
- ~~**`SessionEnd`**~~ → **removed from `settings.json`** (a minor finding from a harness audit: a registered hook that fires and exits without doing anything on every session is drift, and a rule that never acts is what the ratchet cuts). The underlying reason: session documentation here is done by hand and is better than what autodoc would deliver, so turning it on would cost tokens for no gain. **The script is still at `.claude/hooks/session-end.py`.** To reactivate it, two steps: put the `SessionEnd` block back in `settings.json` (same one-liner format as `SessionStart`, changing the file name) **and** create `AIOS/autodoc.enabled` or export `AIOS_AUTODOC=1`. Without the second step the hook goes back to being inert.
- **`Stop`** → `.claude/hooks/session-capture.py`: asks for the session to be persisted in the daily note **at the end of the turn**, through `{"decision": "block", "reason": ...}` (the only lifecycle channel that goes back to the AI). **It used to sit on `PreCompact` with `print()`, and the reminder was written and read ZERO times**: per the spec, only SessionStart/UserPromptSubmit/UserPromptExpansion inject stdout into the context; PreCompact sends it to the transcript and nobody reads it. It is the same defect as `session-start.py` on PreToolUse, made again on another event. Three guards: `stop_hook_active` (anti-loop), daily note freshness (20 min, anti-noise) and `AIOS_DOCUMENTING` (anti-recursion).

Without Python, the vault and the commands keep working. Only the automatic injection and summary are off, and the AI reads the Session Startup files manually (the fallback instructed in CLAUDE.md).

### Hook self-test

`python .claude/hooks/test-hooks.py`: 19 cases that **execute** the hooks and measure what comes back, instead of reading code. The central case ("channel ok") runs every hook in `settings.json` and fails any one that writes stdout on an event that does not deliver stdout to the AI, exactly the class of defect that has already happened twice. Exit 0 = everything passed; the proof is the exit code, not the "passed" on screen. Two things specific to this vault: `PreToolUse` is a valid event here (the locks speak through exit 2 + stderr) and `settings-windows.json` is optional for the test (the wiring is the shell-agnostic one-liner; when the Windows file exists, the test validates it too, which is 2 of the 19 cases). Run it after any change to a hook or to `settings.json`.

- **`PreToolUse`** (matcher `Bash|PowerShell`) → `.claude/hooks/block-kill-by-name.py`:
  **stops killing a process by NAME** (`Stop-Process -Name`, `taskkill /IM`,
  `pkill`/`killall`, `Get-Process | Stop-Process`) when it targets `node`, `python`, `claude` and
  the like. It allows killing by **PID** (surgical) and `Stop-ScheduledTask`. Exit 2 blocks and
  stderr goes back to the agent with the alternatives. **Origin:** while testing an agent's
  keep-alive, a `Stop-Process -Name node` took down three MCP servers with it (one of them needed
  `/mcp` to come back). `node` is the runtime of the agents, the MCPs and Claude Code itself.
  The services on your machine, with the right command to stop each one, go in the `SERVICES` list
  at the top of the script: it only changes the help message, never what is blocked. It is a **hard lock**, not a reinforcement in prose, following the rule that a hook is what holds
  when CLAUDE.md is bypassed. 9/9 test cases. **Known false positive:** a
  command that merely *mentions* the string (documenting, grepping) is blocked too.

- **`PreToolUse`** (same matcher) → `.claude/hooks/block-secret-on-commit.py`:
  **stops a `git commit` that carries a secret into the repo.** The rule "a secret never goes in
  a versioned file" already existed in CLAUDE.md, after an audit found a token in plain text,
  but a rule in prose does not stop a commit. The pattern came from a third-party skill
  publishing script, which scans and **aborts before publishing**.

  **It does not look at the command, it looks at the content going in:** it reads `git diff --cached` (and the
  unstaged diff too when the command has `-a`, because `-a` stages at commit time) and examines only the
  **added** lines. A context line does not count, otherwise a secret already in history
  would block every future commit without solving anything.

  Two gates: a **`.env` file** entering the index (`.env.example` passes) and the **shape of a real
  secret** (OpenAI, Anthropic, GitHub, AWS, Google, Stripe, Slack, Asaas, Meta, a private key
  block, a signed JWT, and a credential assignment with a long value).

  **Against false positives**, because a hook that cries wolf is a hook turned off: a placeholder inside the
  token itself clears it (`sk-your-key-here`, `AKIAIOSFODNN7EXAMPLE`), but a loose placeholder on the
  line only clears the generic pattern. A key with its own prefix does **not** get a pardon for having the
  word "example" in the comment next to it, and that hole only showed up because the self test opened it.

  The trigger requires `git commit` in **command position** (start of the line or after `;`, `&&`,
  `|`). A command that only *mentions* the string passes: `echo "run git commit"`, `git log --grep=commit`
  and a test payload with `git commit` inside quotes. That is the difference between this lock and
  `block-kill-by-name`, which still blocks a mention.

  **Emergency exit:** write `ALLOW_SECRET=1` **inside the command itself**
  (`ALLOW_SECRET=1 git commit -m "..."`). The first version promised that the variable in the shell
  was enough, and it was **wrong**: the hook runs in a separate process and gets Claude Code's
  environment, not the shell's, so it would never see it. The irony is recorded on purpose: it was a
  guarantee that does not execute, written in the same session in which three others were removed.

  **Verification:** `python .claude/hooks/block-secret-on-commit.py --selftest` builds real git
  repos (12 gates + 12 trigger cases). And the test that matters most was end to end,
  firing the **literal command from `settings.json`** with a real payload: registering a hook is config
  state and does not prove execution. The final proof was the hook **blocking its own commit**, because the
  test file had keys written out in full; that is why the fixtures are built by
  concatenation, so the file can be committed by anyone without knowing the trick.

### User-level hook (optional, not included)

A hook that applies to ALL projects on the machine is worth considering. This vault does not install it; the design is recorded here for anyone who wants an audit trail:

- **`PostToolUse`** (Edit/Write/MultiEdit/NotebookEdit) → `~/.claude/hooks/activity-ledger.js`: appends 1 line per edit to the **project's** ledger:
  - **One file per project** at `~/.claude/ledgers/<slug>.md`, with the project taken from the payload's `cwd` and `CLAUDE_PROJECT_DIR` as the fallback. It stays outside the repos on purpose: an audit trail does not go into a commit or ship in a deploy.
  - **Rotation by size** (2 MB → `.1` → `.2`, keeps 2 old ones). Before that it was an endless append.
  - **Errors no longer disappear:** they go to stderr and to `~/.claude/ledgers/ledger-errors.log`. The hook still exits with 0 so it never takes the tool down, but a silent failure became a visible failure.

### History of the failures that shaped the hooks

- A hook on `PreToolUse` did not inject context → agent "disconnected" → moved to `SessionStart`.
- `UnicodeEncodeError` on Windows (cp1252) → `sys.stdout.reconfigure(encoding="utf-8")` in every hook.
- Hooks broke between shells → rewritten shell-agnostic through `python -c "runpy..."`.

## Connected to

[[index]] · [[operating-rules]] · [[verification]] · [[Home]]
