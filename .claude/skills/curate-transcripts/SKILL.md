---
name: curate-transcripts
description: >-
  Mandatory knowledge curation protocol. Runs AUTOMATICALLY after any batch of transcription
  finishes (classes, workshops, mentoring calls, meetings). A transcript is never the final
  output: each one is raw material that gets a verdict (DISTILL / TL;DR / SKIP) before it
  becomes part of the second brain. The agent acts as a Knowledge Editor: it decides the verdict
  on its own (it does not ask "is this worth distilling?"), distills only the DISTILL ones in the
  vault format, integrates them without creating orphan notes, and hands the vault owner a
  verdict table to audit. ALWAYS use it right after transcribing a batch, or when the user says
  "curate the transcripts", "process the transcripts", "go through these recordings", "review
  these lessons", "distill what's worth keeping", "give me a verdict on these transcripts", or
  after generating transcripts of a call or meeting. Do not use it to distill ONE isolated
  source on demand (use strategic-reading or ingest). This is the curation GATE for a whole
  batch after transcription.
---

# Knowledge Curation (post-transcription gate)

A transcript is never the final output. Every transcript is **raw material** that goes through curation before it becomes part of the second brain. You act as a **Knowledge Editor**, not as a transcript processor. This protocol is **mandatory and automatic** at the end of any transcription batch.

The goal is not to archive information. It is to **keep raising the quality, coherence and intelligence of the vault**.

---

## Contract

### Reads

| Path | Why | If missing |
|---|---|---|
| The transcripts in the batch | The raw material. Start to finish, **one pass only** | There is no batch. Say so and stop |
| `AIOS/knowledge-routing.md` | The destination resolver | **Stop.** Routing from memory puts a lesson in the wrong program |
| `04 Resources/{program}/README.md` | The lesson note format and the MOC that ties the series together | Follow the format in this skill, **create the hub** with a link to the first note, and say it was created just now |
| `AIOS/project-map.md` and `02 Context/me.md` | Without them, "Application in MY context" comes out generic, and that section is what separates a shallow note from a valuable one | Write the section as an open question, never as an invented application |
| `knowledge/{domain}.md` | To enrich it **only with what is truly new**, without repeating | Create the domain only if the batch can sustain one on its own |

### Writes

| Path | What | Frontmatter |
|---|---|---|
| `04 Resources/{program}/lessons/YYYY-MM-DD-{topic}.md` | The distilled note, **DISTILL only** | `type`, `date`, `status`, `tags`, `program` |
| `knowledge/{domain}.md` | The truly new addition, made by editing the existing file | already exists |
| `04 Resources/{program}/README.md` | The link to the new note, and the cross-link for the series | already exists |
| `01 Daily/YYYY-MM-DD.md` | One line per batch | already exists |
| `03 Intelligence/decisions/` | Only the **open question**, when the transcript puts a decision under tension | `type: decision`, `status: open` |

### Never writes

| Not this | Owner |
|---|---|
| Rewriting a strategic decision of the vault owner (offer, positioning, price, roadmap, architecture) | The vault owner. Only an **open question** is created here. Frameworks and facts are free; decisions are not |
| A permanent note for a transcript judged TL;DR or SKIP | No one. That is what the verdict is for; a note that should not exist is worse than an unread transcript |
| Editing the raw transcript | No one. Raw material is not corrected, it is distilled |
| `02 Context/me.md` | Only an explicit correction from the vault owner |
| A numbered log in `logs/` | `eiirp`, or whoever did the work |
| Deleting a transcript | Nothing. SKIP records a one-line reason and the file stays |
| A distilled note with no incoming link | No one. An orphan is a failure of the gate: linking it from the program README is part of the job |

If a run hits one of these rows, say so in the verdict table and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

---

## Cost rule (one pass)
Make **ONE pass per transcript**: the full read, the verdict and, if it is DISTILL, the extraction all happen in the SAME step (ideally one extractor subagent per transcript that returns `{verdict, confidence, reason, extraction if DISTILL}`). Read from start to finish (never judge from excerpts), but **never reread** the same transcript. Rereading to "triage" and then again to distill doubles the cost for nothing.

---

## Phase 1: Verdict (the agent decides, it does NOT ask)
Each transcript gets exactly **one** verdict, with a **confidence (0-100%)** and a **one-line reason**:

- **DISTILL**: **clearly strategic** knowledge: a new framework, mental model, playbook or case, actionable, that connects to an active project. Full extraction.
- **TL;DR**: useful, but with no long-term value. A short summary only; **no permanent atomic notes**, unless an important insight shows up.
- **SKIP**: little or nothing reusable. Record **1 line** saying why you skipped it. Do not ingest.

**Criteria:** Novelty · Actionability · Strategic relevance (AIOS, agents, product, sales, marketing, ops, systems) · Density (strategy/framework/playbook vs. Q&A/repetition/operational/filler).

**When in doubt between DISTILL and TL;DR, choose TL;DR and explain the uncertainty.** Only what is clearly strategic gets DISTILL.

---

## Phase 2: Distillation (DISTILL only)
A lesson note in the **vault format** (the hub is `04 Resources/{program}/README.md`, created on the first run if it does not exist yet):
**TL;DR · Frameworks and tactics · Application in MY context · Actions extracted · References.**
Extract **atomic, reusable** knowledge; turn tactics into principles; cut repetition and conversational noise; quote a sentence only when it adds meaning.

**"Application in MY context" has to be SPECIFIC, not generic.** It is what separates a shallow note from a valuable one. Before writing this section, check the active projects ([[AIOS/project-map]]) and the identity note ([[02 Context/me]]). Each application must **name the real project or decision** the lesson touches (e.g. "this puts the pricing decision recorded in [[03 Projects/{active-project}/README]] under tension", "this is actionable now because the tool it mentions is already installed here"), with a concrete action, never a vague "applies to your business". If you could not connect it to anything active, it is probably TL;DR, not DISTILL.

---

## Phase 3: Vault integration (never leave an orphan note)
- **Route** by `AIOS/knowledge-routing.md`. The raw transcript goes in `{program}/transcripts/`; the distilled note goes in `{program}/lessons/` (the program's own naming). Confirm the right program (e.g. the community where the lesson was given ≠ the course for the tool it teaches).
- **Edit what exists instead of duplicating.** Enrich the relevant `knowledge/{domain}` (the domains that already exist are in [[knowledge/index]]) **only with what is truly new**. Do not repeat what is already there.
- Create **back and forward links**; link the note in the **program README** + **1 line in the daily note**; update indexes and MOCs.
- **Batch coherence (critical when it is a series or sequence):** the notes in the same batch **are not islands on the same subject**. Cross-link them to each other so they form a coherent picture. Each note references its siblings (e.g. "series: [[previous-lesson]] · [[next-lesson]]"), the anchor insight of one reinforces or challenges another's, and the program README becomes the MOC that ties everything together. The compound value comes from the connections, not from loose notes: a well cross-linked series is worth more than the sum of its lessons.

For the distillation itself, you can lean on `strategic-reading` (key question: "what in this applies to my active projects?").

---

## Decision guardrail (important)
Enriching **knowledge and framework** domains on your own is expected. BUT when a transcript **changes or puts under tension a strategic DECISION** of the vault owner (offers, positioning, price, roadmap, architecture), **flag it as an open question** (in the decision record in `03 Intelligence/decisions/` and/or in the daily note). **Do not rewrite the decision yourself.** Decisions belong to the vault owner; frameworks and facts are free.

---

## Batch deliverable (built for auditing)
1. **FIRST, the verdict table**: `transcript · verdict · confidence · reason`, so the owner can scan it and override anything they want.
2. Then, for the **DISTILL** ones: notes created, domains and documents updated, links, projects affected, frameworks extracted, actions.
3. **ONE strategic reflection at the end of the batch** (not per transcript): what changed in the understanding · what it reinforced or challenged · which decision should change · which active project benefits right now · which prompt, playbook or skill to update.

The vault owner **audits the final result whenever they want**. The agent does not ask permission for each verdict.

---

## Related
Routing: [[AIOS/knowledge-routing]] · domains: [[knowledge/index]] · skills: `strategic-reading`, `ingest`, `eiirp` (post-session organizer). The program hub is `04 Resources/{program}/README.md`. The folder does not ship with the vault; create it the first time you run this.
