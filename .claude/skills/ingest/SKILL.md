---
name: ingest
description: Ingest a URL, pasted content, or file into the vault. Use when the user drops a reference mid-session and wants it read, distilled, and routed to the right folder with wikilinks, or says 'read this', 'process this', 'add this to the vault', 'process this into the vault', 'clear the inbox'. Do not use it to read a source against a specific problem (that is strategic-reading) or to curate a batch of transcripts (that is curate-transcripts).
type: skill
skill: ingest
status: active
date: 2026-04-24
tags: [skill, aios, ingest, knowledge, routing, portable]
---

## Skill: Ingest

When a raw source arrives (URL, article, research paper, scrape output, Gist, social post, podcast note, or unprocessed Inbox file), run this skill to convert it into structured vault knowledge.

---

### Trigger

Run when:
- The user drops a URL, pastes content, or shares a file mid-session
- The user says "read this", "process this", "add this to the vault"
- `00 Inbox/` contains unprocessed files at session start
- A scraper or research run completes and returns structured data
- A web scrape, market research result, or competitive intel arrives

---

### Contract

Every path this skill touches. Read live on every run, never from a copy.

#### Reads

| Path | Why | If missing |
|---|---|---|
| The source (URL, file, pasted content) | It is the material to ingest | There is nothing to run. Say so and stop |
| `AIOS/knowledge-routing.md` | The destination resolver | **Stop.** Routing from memory is how a note ends up in the wrong place |
| The destination file, when it already exists | To **append** instead of overwrite, and to find contradictions with what is already there | Create a new one with the schema below |
| `00 Inbox/` | The queue of unprocessed captures | Nothing pending, carry on with the current source |

#### Writes

| Path | What | Frontmatter |
|---|---|---|
| The route resolved by `knowledge-routing` (`03 Intelligence/research/`, `/decisions/`, `03 Projects/{name}/research/`, `04 Resources/`; a subfolder such as `market/` or `competitors/` is created on the spot if the routing calls for it) | The distilled content, appended if the file exists | `type`, `topic`, `status`, `date`, `tags` |
| `00 Inbox/` | Only what cannot be classified yet, with `type: inbox` and a one-line summary at the top | `type: inbox` |
| `01 Daily/YYYY-MM-DD.md` | One line: what was processed and where it landed | already exists |
| `03 Projects/{name}/README.md` (and the strategy note in `02 Context/`, if this vault has one) | **Only the reference wikilink**, so the graph can reach what came in | untouched |

#### Never writes

| Not this | Owner |
|---|---|
| Overwriting a file that already exists | No one. The operation is append, always |
| New content inside `02 Context/` | The vault owner. Ingest only adds the wikilink, it never rewrites context |
| `02 Context/me.md` | Only an explicit correction from the vault owner, at the moment they give it |
| A rule, map or guardrail in `AIOS/` | The vault owner; a skill correction goes IN the skill (rule 5 of [[operating-rules]]) |
| A numbered log in `logs/` | `eiirp`, or whoever did the substantive work |
| A skill reference card in `04 Resources/tools/` | The install flow and `check-skills.py` |
| Deleting a vault note | Nothing. Only a `00 Inbox/` file that has already been routed leaves the Inbox |
| Overwriting a note that **contradicts** the new source | No one. A contradiction is flagged explicitly, never resolved silently |

If a run hits one of these rows, say so in the response and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

---

### Step 1: Classify the Source

| Source type | Signals |
|---|---|
| Market research / industry data | Stats, percentages, trends, named studies |
| Competitive intel | Competitor product, pricing, strategy, positioning |
| Tool or framework reference | GitHub repo, Gist, docs site, library README |
| Personal brand insight | Content strategy, platform algorithm, engagement data |
| Project-relevant research | Directly about a client, product, or active project |
| Raw capture (unclassified) | Anything in `00 Inbox/` without clear type |

---

### Step 2: Extract

Pull only what has lasting value. Skip summaries, recaps, and filler.

**Always extract:**
- Key claims with numbers (stat, source name, year)
- Strategic implications: what this means for the user's work specifically
- Contradictions with existing vault knowledge (flag these explicitly)

**Source quality check before extracting:**
- Name the source. Never "a study found" or "experts say"
- Note the date the data was collected (not just published)
- Flag data older than 18 months as potentially stale

---

### Step 3: Route

Use `AIOS/knowledge-routing.md` to decide the file. Common routes:

| Source content | Route |
|---|---|
| Industry trend, platform data, market stat | `03 Intelligence/market/{topic}.md` (create the folder the first time) |
| Competitor product or strategy update | `03 Intelligence/competitors/{name}.md` (create the folder the first time) |
| Decision trigger (forces a choice) | `03 Intelligence/decisions/YYYY-MM-DD-{title}.md` |
| Tool or framework directly used in a project | `03 Projects/{name}/research/{topic}.md` |
| Personal brand / content strategy data | The relevant skill or project file |
| Reusable prompt, template, or framework | `04 Resources/{topic}.md` |
| Cannot be classified yet | Leave in `00 Inbox/` with a `type: inbox` frontmatter tag and a one-line summary at the top |

---

### Step 4: Write

Write to the target file. If the file exists, append. Never overwrite.

**New file schema:**

```markdown
---
type: {market-research | reference | competitive-intel | resource}
topic: {Topic Name}
status: active
date: YYYY-MM-DD
tags: [{relevant}, {tags}]
---

> Related: [[linked-project]] · [[linked-context]]

## {Topic}

**What this covers:** One sentence.

**Last updated:** YYYY-MM-DD

---

## Key Findings

| Finding | Source | Year | Relevance |
|---|---|---|---|

## Strategic Implications

What this means for the user's active projects. Specific, not generic.

## Sources

- [Source Name](URL): what it covers, date accessed
```

**Appending to existing file:**
- Add new findings to the Key Findings table
- Add new implications below the existing ones with a date stamp
- Update the `Last updated` field in frontmatter

---

### Step 5: Integrate

After writing, link the new content into the graph:

1. If it relates to an active project, add a reference in `03 Projects/{name}/README.md`
2. If it's significant market or competitive data, link it from the sibling note it belongs next to in `03 Intelligence/market/` or `03 Intelligence/competitors/`. There is no hub note in this vault: the graph is the hub
3. If it changes a decision or strategy, link from `02 Context/strategy.md` when that note exists; otherwise from the project README
4. If it's a new resource, link it from `AIOS/index.md` (or from the note of the skill that will use it)

---

### Inbox Processing

When processing `00 Inbox/`:

1. List all files: `ls "00 Inbox/"`
2. For each file: classify → extract → route → delete or keep stub
3. Never leave a file in Inbox permanently
4. If a file cannot be routed yet, add a one-line summary to its frontmatter and note it in the daily note with an action item

---

### Rules

- Every stat needs: the number, the source name, the year
- Never create a new market or research file if one already exists on the same topic. Append
- Contradictions with existing vault notes get flagged explicitly, not silently overwritten
- Route immediately. Never pile content back into Inbox as a holding pattern
- After ingesting, update `01 Daily/YYYY-MM-DD.md` with what was processed and where it landed
