---
name: eiirp
description: Post-session organizer (Everything In Its Right Place). Use at the end of a substantive work session or when the user says 'eiirp', 'file all of this', 'organize this session', 'make this permanent', 'put this in the brain' - audits everything the session produced and files each piece in its correct vault location per knowledge-routing. Do not use it for a vault-wide health check (that is vault-lint) or to promote old daily notes into permanent knowledge (that is consolidate).
type: skill
skill: eiirp
status: active
date: 2026-06-11
tags: [skill, aios, eiirp, knowledge, routing, organize, portable]
---

## Skill: EIIRP (Everything In Its Right Place)

The universal post-work organizer, adapted from Garry Tan's GBrain. After any significant work session, nothing that was produced should live only in chat. This skill audits every output of the session, decides where each piece belongs, files it, and reports. Knowledge becomes permanent. Patterns become reusable.

---

### When To Use This Skill

Run when:
- The user says "eiirp", "everything in its right place", "file all of this", "organize all of this", "put this in the brain", "make this permanent", "DRY this up", or "brain this".
- A substantial session just produced research, decisions, drafts, specs, or new facts that are still sitting only in the conversation.
- At the natural end of a working block, before context is lost.

Do not run it for trivial exchanges. EIIRP earns its keep after real work, not after a one-line answer.

---

### What This Skill Does

Walks a 7-phase audit over everything the session produced and lands each item in its correct vault home per `AIOS/knowledge-routing.md`. The user ends with: every output filed in one place (no duplicates, no chat-only knowledge), living pages updated to Compiled Truth + Timeline shape, and a short report of what moved where.

---

### Contract

Every path this skill touches, and what it does with each one. Nothing here is a copy: it is read live, on every run.

#### Reads

| Path | Why | If missing |
|---|---|---|
| The current conversation | It is the source of the outputs to file. Without it there is no inventory | There is nothing to run. Say so and stop |
| `AIOS/knowledge-routing.md` | The routing table, loaded as the resolver | **Stop.** Routing from memory is how a note ends up in the wrong place |
| `AIOS/Vault-Map.md` | The sitemap, to confirm the exact path before writing | Go by the routing alone and say the path was not confirmed |
| Today's `01 Daily/YYYY-MM-DD.md` | Destination of the Phase 7 summary line | Create the daily note with the standard frontmatter |
| The `logs/` folder for the area, when Phase 6 fires | Read the count first to get the next `NNN` | Create the folder and start at `001` |

#### Writes

| Path | What | Frontmatter |
|---|---|---|
| The destination of each item, resolved by the routing | The filed output. Editing an existing page beats creating a new one | `type`, `date`, `status`, `tags`, `project` when applicable |
| `00 Inbox/` | Only the item that fit no row of the routing, flagged as a gap in the table | same |
| `05 Archives/` | The redundant or superseded file, **moved**, never deleted | preserves the original |
| `03 Projects/<Project>/logs/NNN-slug.md` or `AIOS/logs/NNN-slug.md` | The Phase 6 numbered log, when there was substantive work | `log`, `title`, `date`, `area`, `tags` |
| `01 Daily/YYYY-MM-DD.md` | One summary line, appended. Never rewrites what is already there | already exists |

#### Never writes

| Not this | Owner |
|---|---|
| A rule, map or guardrail in `AIOS/` | The vault owner decides; a skill correction goes IN the skill (rule 5 of [[operating-rules]]) |
| `02 Context/me.md` | Only an explicit correction from the vault owner becomes a line there, at the moment they give it |
| A new skill created on its own | Phase 5 **asks**, it does not create. A skill built from one-off work is junk |
| The `## Changelog` line of a project with real traffic | Whoever made the change. eiirp only points to `log NNN` |
| A skill reference card in `04 Resources/tools/` | The install flow and `check-skills.py` |
| Code, config or any file in a project repo | The project's implementation skill |
| Any deletion | Nothing. Redundant files **move** to `05 Archives/` |

If a run hits something that belongs to one of these rows, say so in the response and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

---

### The Process

**Phase 1, Inventory.** List every distinct output of the session: facts learned, decisions made, drafts written, research gathered, new entities (people, companies, projects) mentioned, corrections the user gave, and reusable patterns or prompts. One line each. Show this list before filing anything.

Also surface the session's **open loops**: assumptions made without confirmation, questions left unresolved, and blockers or dependencies for whoever picks this up next. These don't get filed anywhere. They get named, so nothing silently evaporates.

**Phase 2, Route.** For each item, walk `AIOS/knowledge-routing.md` and name its primary home. Every item lands in exactly one place. If two homes seem to fit, pick the primary one and cross-link the rest with `[[wikilinks]]`. If nothing fits, the item goes to `00 Inbox/` and is flagged as a signal the routing table may need a new row.

**Phase 3, Living-page check.** For any item about a person, company, client, project, or ongoing thread, apply the Living Page Structure from `AIOS/knowledge-routing.md`: rewrite the Compiled Truth above the line, append one Timeline entry below it. Never let the two drift.

**Phase 4, File.** Write or update each destination. Edit existing pages over creating new ones. Use frontmatter (`type`, `date`, `status`, `tags`, `project`). Link every new note from at least one existing note (no orphans). Redundant or superseded files MOVE to `05 Archives/` with a note, never get deleted.

**Phase 5, Reusability check.** If the session produced a repeatable process, ask whether it should become a skill in `.claude/skills/`. If it produced a reusable prompt or framework, route it to `04 Resources/`. Do not auto-create a skill for a one-off.

**Phase 6, Numbered log.** If the session did substantive work on a project or on the system itself, write the log for that area:

- Project → `03 Projects/<Project>/logs/NNN-slug.md` · System, skill, command, guardrail, hook → `AIOS/logs/NNN-slug.md`
- **Read the folder count first** to get the next `NNN` (3 digits, zero-padded). If the folder does not exist, create it and start at `001`.
- Frontmatter: `log`, `title`, `date`, `area`, `tags`. Body in `## [HH:MM] Action. Context`, with a **real timestamp** (the file's mtime or `date`), never an estimate.
- **Division of labor, to avoid duplication:** the daily note holds the narrative and the decision, the log holds the reproducible detail (ID, exact command, config, what broke and the fix, what was left out and why). If the change touches real traffic, the `## Changelog` line in the README points to `log NNN`.
- A conversation session, research with no product, or a trivial tweak does **not** produce a log. An empty log pollutes the sequence.

The vault ships with no model log: the first log this skill writes in `AIOS/logs/` becomes the format reference.

**Phase 7, Report.** Output the filing report (format below) and append a one-line summary to today's `01 Daily/` note.

---

### Output Format

```markdown
## EIIRP Report, YYYY-MM-DD

| Output | Routed to | Action |
|---|---|---|
| {what it was} | `path/to/file.md` | created / updated / archived |

**Inbox (needs a home):** {items that did not fit, or "none"}
**New skill candidate:** {process worth systematizing, or "none"}
**Routing gap:** {missing row in knowledge-routing.md, or "none"}
**Open loops (assumptions / unresolved / blockers):** {list, or "none"}
```

---

### Examples

Run: end of a research session on a competitor.
Input: 4 stats, 1 decision, 1 new person mentioned, 1 reusable prompt.
Output: stats to `03 Intelligence/competitors/{name}.md` (living page, Timeline appended), decision to `03 Intelligence/decisions/2026-06-11-{title}.md`, person to a new living page cross-linked, prompt to `04 Resources/`, and a report table plus a one-line daily-note entry.

---

### Anti-Patterns

- Do not file silently. Always show the inventory and the report so the user can correct routing.
- Do not delete anything. Redundant files MOVE to `05 Archives/`.
- Do not duplicate. One primary home per item; everything else is a `[[wikilink]]`.
- Do not invent skills from one-off work. A skill needs a repeatable process with consistent output.
- Do not leave items in chat. If it was worth producing, it gets a home or it goes to `00 Inbox/`.

---

## Meta

Created: 2026-06-11 (adapted from GBrain `eiirp` skill)
Last revised: 2026-07-16 (added open-loops capture to Phase 1 / Output Format, after judging an imported "Session Health Check" mega-prompt against this skill + `vault-lint` and finding that was the one real gap)
