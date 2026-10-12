---
type: index
date: {YYYY-MM-DD}
status: active
tags: [aios, index, skills]
---

# What this vault can do

The list of what comes installed. A skill nobody knows exists does not get used: when you install a new one, add a line here.

## Knowledge and second brain

| Ask like this | What it does | Where it lives |
|---|---|---|
| "process this into the vault" + a link, file or text | Reads it, distills it and files it in the right folder, linked to the notes that exist | skill `ingest` |
| `/organize` | Routes loose notes and connects them with links | command |
| `/setup` | Fills in your context through short questions | command |
| `/import-context` | Brings your history from another AI into the vault | command |
| `/assistant` | Daily review and triage of what came in | command |

## What the packs add

This vault is the base: memory between sessions, routing, and the checks that keep notes healthy. The AIOS Tools packs run on top of it and are sold separately at [https://vaultbubbles.org/aios-tools](https://vaultbubbles.org/aios-tools).

| Pack | What it adds |
|---|---|
| Second Brain Pro | The skills that make the vault improve on its own: consolidation of dated notes into permanent knowledge, transcript curation, strategic reading, vault lint, session filing, review of external resources, and the skill auditor |
| AI Team | Agents with a defined role (assistant, research, meetings, prospecting, persona reviewer), an expert council, a stress interview and a prompt auditor |
| Offer and Copy, Pages, Content, Prospecting | Working skills for the commercial side of an operation |

## Checkers

| Command | What it checks |
|---|---|
| `python "04 Resources/tools/check-note.py" <file>` | Frontmatter, links and orphan note |
| `python "04 Resources/tools/check-wikilinks.py"` | Links across the whole vault |
| `python .claude/hooks/test-hooks.py` | Whether the hooks actually run |
