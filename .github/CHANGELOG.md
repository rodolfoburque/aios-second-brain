# Changelog

## 1.1.1 (2026-11-20)

Corrections reach every session again. **If you installed 1.1.0 or earlier, apply this fix: see [UPDATE.md](../UPDATE.md).**

- Corrections were saved at the end of `02 Context/me.md`, and the session-start hook loads only the first 4,000 characters of that file. Once `me.md` grew past that, saved corrections stopped reaching new sessions, with no warning.
- New `AIOS/conduct.md`: one line per correction, imported whole by `CLAUDE.md` (`@AIOS/conduct.md`). The correction rule in `CLAUDE.md`, rule 5 of `operating-rules.md`, `/assistant`, `/organize`, `/setup`, the `ingest` skill and the routing table now point to it.
- `test-hooks.py` has one more case (20 in total): it fails if `CLAUDE.md` does not import `conduct.md` or the file is missing.
- New `UPDATE.md`: one sentence to paste into Claude Code brings fixes into a vault that is already installed.

## 1.1.0 (2026-10-12)

The base vault is now only what the second brain needs to run: session memory, routing, safety hooks, setup, the daily assistant, context import, organize, ingest and the note and link checkers.

- Moved to the paid AIOS Tools packs: the skills `consolidate`, `curate-transcripts`, `strategic-reading`, `vault-lint`, `eiirp`, `integration-review`, `roundtable`, `grilling`, `prompt-auditor-4d`, the five agents, the `/audit-skills` command and `check-skills.py`. Version 1.0.1 remains available under its tag.
- `AIOS/index.md` lists what the packs add.
- The session-start metrics stay, and now point to the pack that acts on them.

## 1.0.0

First public release.

- Vault structure, `CLAUDE.md` and the `AIOS/` maps.
- 5 commands, 10 skills, 5 agents.
- Session hooks (start, capture, end), secret blocking on commit, and `test-hooks.py`.
- Checker scripts for notes, wikilinks, skills and vault metrics.
- Install by pasting one sentence into Claude Code.
