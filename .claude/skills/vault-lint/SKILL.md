---
name: vault-lint
description: Vault health check. Use when the user says 'lint the vault', 'vault health check', 'find gaps', 'what's broken', 'find orphan notes', 'check for broken links' - finds orphan notes, missing frontmatter, broken wikilinks and stale notes, and produces a prioritized fix report. Do not use it to file session output (that is eiirp) or to promote daily notes into permanent knowledge (that is consolidate).
type: skill
status: active
date: 2026-04-24
tags: [skill, linting, health-check, vault, automation]
---

# Skill: Vault Lint

Run this skill when the user says "lint the vault", "vault health check", "find gaps", "what's broken", or any equivalent.

**There is no lint script.** The agent does the audit by reading the files.

These tools do exist and cover neighboring pieces. Use them before redoing the work by hand:

| Tool | What it covers |
|---|---|
| `04 Resources/tools/check-skills.py` | the skill pack: the reference-card/executable contract and internal integrity |
| `04 Resources/tools/check-note.py` | frontmatter and structure of a single note |
| `04 Resources/tools/check-content.py` | published content (optional: it does not ship with the vault; if it is not installed, skip it) |
| `04 Resources/tools/check-wikilinks.py` | broken `[[links]]` across the whole vault, with the "memory slug" class separated out (`--memory-slugs`) |

---

## Contract

This skill reads the whole vault and is allowed to **fix structure**, never content. That distinction is the axis of the contract.

### Reads

| Path | Why | If missing |
|---|---|---|
| Every `.md` in the vault | It is the audited surface | Nothing to audit |
| The checkers in `04 Resources/tools/` (three ship with the vault; the content one is optional) | They cover neighboring pieces: run them before redoing the work by hand | Say which one does not exist and audit that piece by reading the files |
| `CLAUDE.md`, `knowledge/`, `02 Context/me.md` | The auto-loaded material, measured by check 9 | Skip check 9 and say you skipped it |
| `AIOS/knowledge-routing.md` | To judge whether a fact is misrouted | Skip the routing part of check 9 |

### Writes

| Path | What | Frontmatter |
|---|---|---|
| `03 Intelligence/vault-lint-YYYY-MM-DD.md` | The prioritized report | `type: report`, `status`, `date`, `tags` |
| Any note, **structure only** | A broken wikilink pointed at the right target, a missing frontmatter field, an incoming link for an orphan | preserves what is already there |
| `05 Archives/` | The abandoned draft, **moved** | preserves the original |

### Never writes

| Not this | Owner |
|---|---|
| A new note created just to silence a broken wikilink | No one. A knowledge gap becomes a **report item**; the note is created when there is real content. An empty stub trades a broken link for a lie |
| Prose, argument or conclusion inside someone else's note | The note's author. Lint fixes structure, it does not rewrite text |
| A decision in `03 Intelligence/decisions/` | Whoever made the decision |
| `02 Context/me.md` and rules in `AIOS/` | The vault owner |
| Deleting anything | Nothing. Redundant and abandoned files **move** to `05 Archives/` |
| Translating content written in the owner's language | No one. The owner's language is the vault's rule, not a defect (see check 5) |
| A numbered log in `logs/` | `eiirp`, or whoever did the work |

If a run hits one of these rows, say so in the response and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

---

## What This Skill Does

Audits the entire vault for health issues and produces a prioritized report with actionable fixes.

---

## Checks to Run

### 1. Orphan Notes
Find notes with zero incoming wikilinks: no other note links to them.

```
For each .md file: count how many other files contain [[filename]] or [[path/filename]]
Flag any file with count = 0 (except index files and maps)
```

### 2. Missing Frontmatter Fields
Every note should have: `type`, `status`, `date`, `tags`.
Flag notes missing any of these.

### 3. Stale Notes
Notes with `status: draft` older than 14 days, likely abandoned.
Notes with `status: active` that haven't been modified in 90+ days.

### 4. Broken Wikilinks
**Run `python "04 Resources/tools/check-wikilinks.py"`, do not sweep by hand.** It excludes code blocks and backticks (quoted syntax is not a broken link), resolves both basename and relative path, and exits with code 1 if it finds anything. Broken links are listed under "TARGET DOES NOT EXIST".

Four causes, and the fix differs for each:
- **A memory slug turned into a wikilink** (usually the largest class; the vault this template came from had 230 occurrences at one point). The vault and the agent's memory use the SAME `[[name]]` syntax, so a memory slug ends up inside a vault note and never resolves. Fix: point to the vault note that already holds the fact, or create the note. See the precedence rule in [[me]].
- **A project folder name** (`[[{project}]]`): the file is `README.md`. The right target is the full path, `[[03 Projects/{project}/README|{project}]]`, because every project has a `README.md` and the bare name does not tell one from another.
- **A typo or a renamed file.**
- **A note that should exist and does not** (it becomes a knowledge gap, check 8).

### 5. Language Conformity
> The vault has one prose language: the one its owner writes in (default English). This check never asks for content to be translated into another language.

Flag: prose content (headings, body) written in a different language from the rest of the vault (exceptions: technical skills and commands, code, quotes from a source); frontmatter KEYS that are not in English (`tipo:` instead of `type:`).

### 6. Missing Project Links
Find notes with `project:` in frontmatter but no `[[wikilink]]` back to the project README.

### 7. Connection Opportunities
Find notes that mention the same concepts, people, or projects but don't link to each other.
Suggest specific wikilinks to add.

### 8. Knowledge Gaps
Find `[[wikilinks]]` to non-existent notes that appear in 3+ places. These are notes that should be created.

### 9. Context Quality (os-optimizer layer, adapted from benai-skills)
Structure checks (1-8) find what's broken; these find what's **bloating or misrouting the context** the agent loads:

- **Auto-loaded bloat:** files loaded every session (`CLAUDE.md`, `knowledge/*.md`, `02 Context/me.md`) above ~300 lines. Candidates to split into load-on-demand references (progressive disclosure).
- **Skill bloat:** SKILL.md above ~150 lines without a `references/` folder. Trigger, steps and routing belong in the SKILL, detail belongs in references.
- **Misrouted memory:** durable facts living only in `01 Daily/` (decisions, tool gotchas, preferences repeated across 2+ daily notes) that never got promoted to `knowledge/`, `03 Intelligence/decisions/` or `02 Context/`.
- **Duplicated knowledge:** the same fact or framework maintained in 2+ notes with drift risk. Keep one canonical, wikilink the rest.
- **Stale context:** auto-loaded content referencing things that no longer exist (dead projects, replaced tools). It actively misleads every session.

---

## Output Format

Produce a lint report as a vault note at `03 Intelligence/vault-lint-YYYY-MM-DD.md`:

```markdown
---
type: report
status: active
date: YYYY-MM-DD
tags: [vault, lint, health-check]
---

## Vault Lint Report, YYYY-MM-DD

### Summary
- X orphan notes
- X broken wikilinks
- X notes missing frontmatter
- X stale drafts
- X connection opportunities
- X knowledge gaps (missing notes to create)
- X context-quality issues (bloat / misrouted memory / duplicates)

### Orphan Notes (fix: link from somewhere)
- [[note-name]], suggested parent: [[suggested-note]]

### Broken Wikilinks (fix: rename or create target)
- In [[source-note]]: [[broken-link]] → does not exist

### Knowledge Gaps (fix: create these notes)
- [[concept-name]], referenced in X notes, doesn't exist

### Connection Opportunities (fix: add wikilinks)
- [[note-a]] and [[note-b]] both discuss [topic]: link them

### Stale Drafts (fix: complete or archive)
- [[draft-note]], status: draft since YYYY-MM-DD

### Language Drift (fix: realign with CLAUDE.md)
- [[note]], prose in a different language from the rest of the vault, or a frontmatter key that is not in English (`tipo:` instead of `type:`)
```

> The drift to report is content that departs from the vault's language, or frontmatter keys that are not in English. The fix is never to translate the owner's content or rename the file.

---

## After Reporting

Fix issues in priority order:
1. Broken wikilinks (highest impact: broken graph)
2. Knowledge gaps (create missing notes)
3. Orphan notes (add incoming links)
4. Stale drafts (complete or move to `05 Archives/`)
5. Missing frontmatter (add fields)
6. Language drift (prose in a different language from the rest of the vault, frontmatter key that is not in English)
