---
type: map
status: active
date: 2026-05-26
tags: [aios, routing, knowledge, portable]
---

## Knowledge Routing

Every piece of information has a home. Route it here, never to a catch-all.

---

### Routing Table

| Type of content | Goes to |
|---|---|
| Personal preferences, style, habits | `02 Context/me.md` |
| Strategy and goals | `02 Context/strategy.md` |
| Brand voice and tone | `02 Context/brand.md` |
| About you and your work | `02 Context/me.md`, section "Me and my work" |
| About the people you work with | `02 Context/me.md`, section "Me and my work" |
| Decision with reasoning | `03 Intelligence/decisions/YYYY-MM-DD-{slug}.md` |
| Meeting notes | `03 Intelligence/meetings/{type}/YYYY-MM-DD-{slug}.md` |
| Competitor insight | `03 Intelligence/competitors/{name}.md` |
| Market insight | `03 Intelligence/market/{topic}.md` |
| Deep research result | `03 Intelligence/research/YYYY-MM-DD-{slug}.md` |
| Info about an active project | `03 Projects/{name}/README.md` or a subfolder |
| Research related to a project | `03 Projects/{name}/research/{topic}.md` |
| Project spec or requirement | `03 Projects/{name}/specs/{name}.md` |
| Project content draft | `03 Projects/{name}/drafts/{name}.md` |
| Written piece (post, email, etc.) | `04 Resources/writing/{channel}/YYYY-MM-DD-{slug}.md` |
| Landing page brief | `04 Resources/landing-pages/{slug}.md` |
| Case study | `04 Resources/cases/{client}.md` |
| SEO audit | `04 Resources/seo/audits/YYYY-MM-DD-{site}.md` |
| Google Ads output | `04 Resources/ads/google/YYYY-MM-DD-{mode}-{slug}.md` |
| Meta Ads output | `04 Resources/ads/meta/YYYY-MM-DD-{mode}-{slug}.md` |
| Reusable resources (prompts, frameworks) | `04 Resources/` |
| Tool or platform card (setup, credential, cost, pitfall) | `04 Resources/tools/{tool}.md`, a living page (Compiled Truth + Timeline) |
| Session record (narrative, decision of the day) | `01 Daily/YYYY-MM-DD.md` |
| Numbered log of substantive work | `03 Projects/{name}/logs/NNN-slug.md`, or `AIOS/logs/NNN-slug.md` when the work is on the system itself |
| Unprocessed quick capture | `00 Inbox/` |
| Finished or archived content | `05 Archives/` |
| Knowledge domain (auto-loaded) | `knowledge/{domain}.md` |
| Rules for the AI's behavior | `02 Context/me.md` (section "Permanent corrections") |

---

### Project Sub-routing

When information about a project shows up, analyze it and route it to the right subfolder:

| Type of content | Subfolder |
|---|---|
| Status, deadline, overview | `03 Projects/{name}/README.md` |
| Research, competitor analysis | `03 Projects/{name}/research/{topic}.md` |
| Spec, requirement, brief | `03 Projects/{name}/specs/{name}.md` |
| Draft, script, written content | `03 Projects/{name}/drafts/{name}.md` |
| Idea, brainstorm | `03 Projects/{name}/ideas/{name}.md` |
| Working notes | `03 Projects/{name}/notes/{name}.md` |
| Feedback, review | `03 Projects/{name}/feedback/{name}.md` |

**Subfolders on the fly:** do not create empty folders ahead of time. When content arrives that needs a subfolder, create it at that moment.

**README as index:** README.md is the entry point with overview + status + next steps + links to the subfolders. Do not duplicate subfolder content in the README.

**Lifecycle:** New project = only README.md → subfolders appear as types of content emerge → a finished project migrates to `05 Archives/projects/{name}/`.

---

### Meeting Sub-routing

When processing a meeting transcript or notes, route by type:

| Type | Folder |
|---|---|
| Client call | `03 Intelligence/meetings/client-calls/` |
| 1:1 with a collaborator | `03 Intelligence/meetings/one-on-ones/` |
| Team standup | `03 Intelligence/meetings/team-standups/` |
| One-off meeting | `03 Intelligence/meetings/general/` |

File name format: `YYYY-MM-DD-{meeting-slug}.md`.

---

### Command Output Sub-routing

Each command saves to a consistent folder.

| Command | Saves to |
|---|---|
| `/assistant` | `01 Daily/YYYY-MM-DD.md` |
| `/import-context` | `02 Context/me.md` |

---

### Golden rule

**Before saving anything, ask:**
1. Is this about the user or about their work? → `02 Context/`
2. Is this a decision, a meeting, or an insight about the outside world? → `03 Intelligence/`
3. Is this about a specific project? → `03 Projects/{name}/`
4. Is this the output of a command? → `04 Resources/` (the command's subfolder)
5. Is this permanent knowledge the AI should always know? → `knowledge/`
6. Not sure yet? → `00 Inbox/`

When in doubt, pick the most specific place possible. `00 Inbox/` is the last resort, not the first.

---

## Connected to

[[Home]] · [[AIOS/index|index]] · [[Vault-Map]] · [[operating-rules]] · [[project-map]]
