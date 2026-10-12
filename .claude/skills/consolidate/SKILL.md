---
name: consolidate
description: >-
  The vault's memory consolidation cycle: promotes a dated episode (daily note, log, decision,
  research, lesson) into a TIMELESS STATEMENT in the cortex, and puts cold knowledge on the hot
  path the agent loads by itself. It is the hippocampus→neocortex replay of the second brain:
  the vault does not get smarter by capturing more, it gets smarter by consolidating and pruning
  what it already captured. Use when the user says "consolidate", "run consolidate", "promote
  this to knowledge", "turn these daily notes into knowledge", "the vault is turning into a
  dumping ground", "run the consolidation cycle", "prune the vault", "this isn't an episode
  anymore, it's a rule", or when the vault intelligence notice at session start shows a low hot
  path or a rising consolidation ratio. It is NOT curation of a transcription batch (that is
  curate-transcripts, which runs BEFORE this and feeds it), nor a health check for broken links
  and frontmatter (that is vault-lint), nor filing of session output (that is eiirp).
---

# Memory consolidation (hippocampus → cortex replay)

The brain does not keep episodes forever. It records fast and cheap in the hippocampus and, during replay, transfers **the pattern** to the neocortex and discards the detail. Someone with a large hippocampus and a small cortex keeps recalling events without ever extracting the rule.

This vault has both organs: `01 Daily/`, `logs/`, `transcripts/`, `research/` and `decisions/` are hippocampus (dated, they report). `knowledge/`, `04 Resources/frameworks/` and `02 Context/` are cortex (timeless, they state). Your job here is to be the **replay**, not the capturer. You do not create any new note of raw material in this skill. None.

**Always start by measuring, with both:**
```
python "04 Resources/tools/vault-metrics.py"
python "04 Resources/tools/vault-usage.py" --days 30
```

The first measures **anatomy** (how many notes, how much of the cortex is within reach of a cue, how much crosses clusters, what is prunable). The second measures **firing**: which notes were actually opened, read from Claude Code's session transcripts. Use both together, because anatomy without firing is the mistake this skill exists to find: a well-linked note that nobody opens is dead weight no matter how good it looks in the graph.

`vault-usage.py` **does not ship with the vault** (it reads Claude Code's session transcripts and depends on the machine's layout). If it is not in `04 Resources/tools/`, run only the first, say in the deliverable that the round measured anatomy and not firing, and claim nothing about usage. When installed, it takes ~7s on a 30-day window, which is why it does **not** run in `session-start`; it belongs to this skill. Work in the order of whichever ratios are worst, and at the end run both again and paste the before/after (rule from `AIOS/verification.md`: config state does not prove that something works).

**One reading that only shows up when you cross the two:** cortex within reach and cortex used diverge, and the divergence is informative. High reach with low use is a pointer written for a question nobody asks. High use with low reach means the note is being found by brute force every time, and deserves a pointer. In the vault this skill was built in, at one measurement: 36% reach against **81% use**, meaning the vault was used far beyond what the hot path suggested, and most of the hits came from search, not from a cue.

---

## Phase 1: Promotion (an episode becomes a statement)

Sweep the hippocampus since the last consolidation (this skill's previous log gives the date; if there is none, use the last 30 days) and look for **one pattern only**: the fact that showed up in 2+ distinct episodes, or that broke one of your expectations.

The promotion test, applied to each candidate:

| Question | If yes |
|---|---|
| Will this still be true 6 months from now? | cortex candidate |
| Does it only make sense with the date attached? | stays in the hippocampus, it is an episode |
| Is it already written in another cortex note? | **enrich the existing one**, do not create a new one |
| Is it a strategic decision of the vault owner? | it becomes an open question, you do not rewrite it yourself |

**The shape of the promoted note.** A timeless statement does not report, it declares, and it carries the prediction error that produced it. That field is not decoration: the brain only encodes where an expectation breaks, and it is what separates learning from note-taking.

```markdown
---
type: knowledge          # or framework, if it is a method
date: <today>
status: active
tags: [...]
---

# <The statement, written as a statement, not as a topic title>

**What I believed before:** <the expectation that broke>
**What is true:** <the rule, with no date>
**How this showed up:** [[episode-1]] · [[episode-2]]
```

**Never delete the episode.** The episode becomes a footnote citation for the statement, and gets a wikilink back. Hippocampus and cortex coexist in the brain; what changes is which of the two answers the question.

**Cap per round: 5 promotions.** Consolidating in large batches turns into shallow-note production, which is exactly the problem this skill exists to solve. If candidates are left over, say how many stayed in the queue.

---

## Phase 2: Hot path (the cortex the agent loads by itself)

Knowledge nobody loads is knowledge nobody uses. `session-start.py` injects `02 Context/me.md`, `knowledge/index.md` and the daily note; **all the rest of the cortex depends on someone remembering to go get it**. In the vault this skill was built in, at one measurement, that was 15.5%: a note about the machine's gotchas was cited by 22 notes and loaded by zero.

The metrics tool's `--json` output returns `cold_most_pulled`, the cold cortex sorted by how many notes cite it. A note that is cited a lot and never loaded is the cheapest fix in the whole vault.

**The fix is NOT to move the file.** The hook has a ceiling of 9,000 characters and `knowledge/` is loaded whole; filling the folder blows the context budget and makes everything worse. The fix is a **one-line pointer** in `knowledge/index.md`:

```markdown
| [[04 Resources/tools/{most-cited-cold-note}]] | {the situation in which I need it} |
```

The pointer carries the cue (when I need this), not the content. It is cue-based retrieval, which is how the brain retrieves: you do not search for the memory, you run into its trigger.

**Guardrail:** if you add a pointer, run the hook for real (`echo '{}' | python .claude/hooks/session-start.py | wc -c`) and confirm it stays below 9,000. A pointer that blows the ceiling knocks out the identity block, which is worse than the original problem.

---

## Phase 3: Long edge (connect distant clusters)

A link inside the same folder is a local cluster and is already dense by construction. What makes the graph think is the rare connection between areas that normally do not talk to each other: a lesson from a course that solves a problem in a client project, a billing playbook that changes the pricing page.

Add **at least one** long edge per round, and write in the note **why** the two touch. A link with no written reason is anatomy; nobody walks it later.

Do not force the rate up: above ~60% (the value in the vault this skill was built in) the return drops and you start inventing kinship. The goal is the right edge, not the rate.

---

## Phase 4: Pruning (removing is what makes it fast)

From birth to the end of adolescence the brain loses about half its synapses, and that is when it gets fast. An unused note is not an asset, it is a retrieval cost charged to all the others.

```
python "04 Resources/tools/vault-metrics.py" --triage
```

A binary decision per note, with only two outcomes:

- **Promote**: it gets a `type`, gets at least one incoming link, and stays.
- **Archive**: it goes to `05 Archives/`, with one line saying why it left.

**Archiving is not deleting.** You move; you never delete. And three classes are never pruned, even when isolated: a legal or financial document (`02 Context/documents/`), a decision record, and a note created in the last 30 days (it has not had time to be linked yet).

When in doubt between promoting and archiving, **archive**: reverting is one `git mv`, and a shallow note kept alive costs you in every future search.

---

## Deliverable

1. **The promotion table first**, for the vault owner to audit and override: `episode → statement → destination note → what broke the expectation`.
2. Pointers added to `knowledge/index.md`, with the hook size before and after.
3. Long edges created, with the reason for each one.
4. Pruning table: `note → promote/archive → reason`.
5. **The before/after of the four ratios**, pasted from the metrics tool's real output. Without this the round is not closed.
6. A numbered log in `AIOS/logs/NNN-consolidation-<date>.md` (it is work on the system itself) and one line in the daily note.

## Contract

This skill is **replay, not capture**. It moves a pattern from one organ to the other and produces no raw material at all.

### Reads

| Path | Why | If missing |
|---|---|---|
| `04 Resources/tools/vault-metrics.py` | Anatomy. The firing meter is optional and does not ship with the vault (see the start of this skill): without it, go on with anatomy alone and say in the deliverable that firing was not measured | **Stop.** Consolidating without measuring is reorganizing by taste |
| The hippocampus: `01 Daily/`, `logs/`, `03 Intelligence/research/` and `/decisions/`, `transcripts/` | Where the pattern shows up in 2+ episodes | There is nothing to promote in this window. Say so |
| This skill's previous log in `AIOS/logs/` | The date of the last consolidation, which defines the window | Use the last 30 days |
| `knowledge/index.md` | The hot path and the hook's 9,000-character ceiling | **Stop.** Without the measured ceiling, adding a pointer can make everything worse |

### Writes

| Path | What | Frontmatter |
|---|---|---|
| `knowledge/{domain}.md` and `04 Resources/frameworks/` | The promoted timeless statement, written as a statement | `type`, `status`, `date`, `tags` |
| `knowledge/index.md` | The **one-line pointer**, with the hook size before and after | already exists |
| `05 Archives/` | The pruned note, **moved**, with one line saying why it left | preserves the original |
| Cortex notes | The long edge: a wikilink that connects distant clusters, with the reason | already exists |
| `AIOS/logs/NNN-consolidation-<date>.md` and `01 Daily/` | The log of the round, with the before/after pasted from the real output | `log`, `title`, `date`, `area`, `tags` |
| `03 Intelligence/decisions/` | Only the **open question**, when the pattern puts a decision under tension | `status: open` |

### Never writes

| Not this | Owner |
|---|---|
| A new note of raw material | `ingest` and `curate-transcripts`. The urge to capture here is a sign you have left the scope |
| Rewriting a strategic decision of the vault owner | The vault owner. Only an open question is created here |
| **Moving a file into `knowledge/`** | No one. The hook loads the whole folder under a 9,000-character ceiling: the fix is a one-line pointer, never a change of location |
| Deleting anything | Nothing. Pruning **moves** to `05 Archives/`, and reverting is one `git mv` |
| Pruning a legal or financial document, a decision record, or a note less than 30 days old | No one. The three classes stay even when isolated |
| `02 Context/me.md` and rules in `AIOS/` | The vault owner |
| Claiming what the owner reads in Obsidian | No one. The meter only sees what went through an agent session: a note they open and never cite here shows up as cold **and is not** |

If a run hits one of these rows, say so in the promotion table and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

## Related

Runs **after** [[curate-transcripts]] (which handles a transcription batch and feeds the hippocampus) and **alongside** [[vault-lint]] (integrity: broken links, frontmatter). [[eiirp]] files the session's output; this skill promotes the knowledge in it.
