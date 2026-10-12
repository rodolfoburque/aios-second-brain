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
| "what do I do with this" + an article, book or video | Pulls out only what applies to the active project and turns it into next actions | skill `strategic-reading` |
| "curate these transcripts" | Gives a verdict per transcript (distill, summarize, discard) and distills only what is worth it | skill `curate-transcripts` |
| "consolidate" | Promotes dated accounts to permanent knowledge | skill `consolidate` |
| "run the vault lint" | Finds broken links, notes without frontmatter and orphan notes | skill `vault-lint` |
| "eiirp" or "organize this session" | Files everything the session produced in the right place | skill `eiirp` |
| "review this resource" + a repository or tool | Evaluates an external resource and closes with an integration decision | skill `integration-review` |
| `/organize` | Routes loose notes and connects them with links | command |
| `/setup` | Fills in your context through short questions | command |
| `/import-context` | Brings your history from another AI into the vault | command |
| `/assistant` | Daily review and triage of what came in | command |
| `/audit-skills` | Checks the skills from the inside | command |

## Agents with a defined role

| Agent | Role | Where it lives |
|---|---|---|
| Vault assistant | Answers questions about projects, people and decisions, citing the note | agent `team-assistant` |
| Research | Researches a topic, synthesizes it with sources and saves it as a note | agent `team-research` |
| Meetings | Documents a meeting transcript and gathers the action items | agent `team-meetings` |
| Prospecting | Finds businesses in a niche and points out each one's pain with proof | agent `team-prospecting` |
| Persona reviewer | Reads a page or message the way the buyer would | agent `persona-reviewer` |
| Expert council | Puts different points of view to debate a decision | skill `roundtable` |
| Stress interview | Asks the hard questions before you execute a plan | skill `grilling` |
| Prompt auditor | Scores a prompt or conversation and returns the corrected version | skill `prompt-auditor-4d` |

## Checkers

| Command | What it checks |
|---|---|
| `python "04 Resources/tools/check-note.py" <file>` | Frontmatter, links and orphan note |
| `python "04 Resources/tools/check-wikilinks.py"` | Links across the whole vault |
| `python "04 Resources/tools/check-skills.py"` | The skills from the inside |
| `python .claude/hooks/test-hooks.py` | Whether the hooks actually run |
