# Changelog

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
