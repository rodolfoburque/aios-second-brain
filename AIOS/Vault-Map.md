---
type: reference
date: 2026-05-26
status: active
tags: [navigation, vault-map, ai-os]
updated: 2026-05-26
---

# Vault Map: AIOS

Complete sitemap of your vault. Check it whenever you need to know where something lives, where to route new information, or when the AI asks about a project.

This file answers **where things go**. `02 Context/me.md` answers **who operates** this vault. `CLAUDE.md` answers **how to use it**. `AIOS/index.md` answers **what you can do**.

---

## Root structure

```
CLAUDE.md                      : Main pointer + project map
AIOS/Vault-Map.md              : This file: complete sitemap + routing
00 Inbox/                      : Capture zone: raw notes that need processing
01 Daily/                      : Daily session notes (YYYY-MM-DD.md)
02 Context/                    : Identity layer (me.md, strategy.md, brand.md)
03 Intelligence/               : Meetings, decisions, competitors, market, research
03 Projects/                   : All active projects
04 Resources/                  : Prompts, frameworks, swipe files, templates
05 Archives/                   : Completed and historical content
AIOS/                          : Portable operating layer: skills, maps, rules
knowledge/                     : Knowledge hub auto-loaded in every session
.claude/                       : Claude Code configuration and hooks
prompts/                       : Reusable prompts (starts empty)
```

---

## Folders in detail

### `00 Inbox/`
Capture zone. Everything that lands here needs to be processed and moved.

**How to use:** When the user says "note this", "capture this", "save this for now" → it lands here. It is not a final destination.

**When to process:** During the daily or weekly review, run `/assistant` in "tasks" mode to move each item to the right place.

---

### `01 Daily/`
Daily session notes. One per day, format `YYYY-MM-DD.md`.

**What is inside:**
- Focus of the day
- What was done
- Decisions made
- Lessons learned
- Next steps for tomorrow
- Open tasks

**Auto-read:** The most recent note is loaded at the start of every session by the `session-start.py` hook.

---

### `02 Context/`
Permanent identity layer. Read at the start of every session.

**Files:**
- `me.md`: who you are and how you work
- `brand.md`: voice, tone, brand keywords (created if relevant)
- `strategy.md`: vision, 90-day / 1-year / 3-5-year goals (created if relevant)
- Others that get created as context shows up

---

### `03 Intelligence/`
Knowledge about the outside world + internal decisions.

**Structure:**
```
03 Intelligence/
├── meetings/              : Meeting notes by type
│   ├── client-calls/      : Calls with clients
│   ├── one-on-ones/       : 1:1s with collaborators
│   ├── team-standups/     : Team standups
│   └── general/           : One-off meetings
├── decisions/             : Important decisions with reasoning (YYYY-MM-DD-{slug}.md)
├── competitors/           : Competitor analysis (1 file per competitor)
├── market/                : Market insights by topic
├── research/              : Research
└── archive/               : Archive for this folder's content
```

---

### `03 Projects/`
Each active project has a subfolder. Each project has a `README.md` as its entry point.

**Typical structure:**
```
03 Projects/{project-name}/
├── README.md              : Overview, status, next steps
├── research/              : Related research
├── specs/                 : Specs and requirements
├── drafts/                : Content drafts
└── ideas/                 : Free brainstorm
```

**When to create:** When the user mentions something that will take more than 1 week of work, it becomes a project. One-off items stay in `00 Inbox/` or `01 Daily/`.

---

### `04 Resources/`
Reusable personal library. Prompts, frameworks, references, templates.

**Structure emerges with use:**
```
04 Resources/
├── writing/               : Written pieces
│   ├── linkedin/
│   ├── newsletter/
│   └── email-sequences/
├── landing-pages/         : Landing page briefs
├── cases/                 : Client cases
├── seo/audits/            : SEO audits
├── attachments/           : Images, PDFs, attachments
└── (others you create)
```

---

### `05 Archives/`
Finished, historical content. Things that will not disappear but are no longer active.

**When to use:**
- Finished project → move from `03 Projects/{name}/` to `05 Archives/projects/{name}/`
- Newsletter issue already published → optional, move from `04 Resources/writing/newsletter/` to `05 Archives/newsletter/`
- Client that left → move the specific daily notes, briefs, etc.

---

### `AIOS/`
Portable layer. This folder is the operating brain that does not depend on any tool.

**Files:**
- `index.md`: Catalog of skills and maps
- `Vault-Map.md`: This file
- `operating-rules.md`: How the AI should behave
- `knowledge-routing.md`: Where to route each type of information
- `project-map.md`: Map of active projects
- `open-loops.md`: What is waiting on a decision or a trigger
- `verification.md`: How to prove the work came out right
- `guardrails.md`: What the AI never does
- `hooks.md`: Details of the hooks in this install
- `tools.md`: Tools the AI can reach, each proven with a real read
- `logs/`: Numbered logs of work on the system itself

---

### `knowledge/`
Knowledge hub auto-loaded in every session.

**What goes here:**
- `index.md`: Navigation for the knowledge files (auto-loaded first)
- Domains of expertise you want the AI to always have (e.g. `copywriting.md`, `seo-fundamentals.md`, `linkedin-strategy.md`)

**Difference from `04 Resources/`:**
- `knowledge/` is loaded automatically in every session (the AI always "remembers")
- `04 Resources/` is reference the AI looks up when it needs it (not loaded by default)

---

## Hub Notes (connection nodes)

Use wikilinks to these files whenever you mention the subject:

| Hub | Purpose |
|---|---|
| `[[02 Context/me]]` | You: core identity |
| `[[AIOS/index]]` | Available commands and skills |
| `[[03 Projects/{name}/README]]` | Each active project |

Connecting with wikilinks makes the Obsidian graph grow: you see the connections visually.

---

## Quick routing

To find out where a new piece of information goes, check [[AIOS/knowledge-routing]].

---

## Connected to

[[Home]] · [[AIOS/index|index]] · [[knowledge-routing]] · [[operating-rules]] · [[project-map]]
