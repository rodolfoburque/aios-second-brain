---
description: Organizes the vault. Finds orphan notes, routes them into the right structure, connects them with wikilinks and archives redundancy, without touching the system folders. Asks when in doubt.
---

# Organize: Vault Cleanup and Routing

Use it when the graph turns into soup: loose notes, no links, dropped at the root or in the Inbox. This command routes everything into the structure the vault already has, connects it with wikilinks and archives what is redundant. It never restructures the vault and never deletes anything.

---

## Language

Detect the language of the message that invoked this command and use it in every question and message.
Default English. Any other language if the user wrote in it.
File contents, paths and frontmatter keys stay intact. Do not translate them.

---

## Before anything else

Read at the start, without announcing it:
1. `02 Context/me.md` (who the user is, voice, projects)
2. The most recent file in `01 Daily/`, to pick up the context of the last session

---

## Hard rules (do NOT break any)

- **Do NOT rename, move or delete** the system folders: `00 Inbox`, `01 Daily`, `02 Context`, `03 Projects`, `03 Intelligence`, `04 Resources`, `05 Archives`, `AIOS/`, `knowledge/`, `.claude/`. The hooks use these exact paths, and touching them breaks the agent.
- **Do NOT touch** `README.md`, `CLAUDE.md`, or `index` files. They look loose in the graph but they are structural and correct that way. They never go on the orphan list.
- **NEVER delete anything.** Redundancy goes to `05 Archives/`, never to the trash.
- **Close Obsidian before moving files** (it avoids conflict copies like "Note 2.md"). Warn the user about this before running Phase 4.
- Use Obsidian **wikilinks `[[ ]]`**, never markdown links for internal notes.
- Work silently during execution. Confirmation only at the end.

---

## Contract

This command changes **where a note lives and how it connects**, never what it says.

### Reads

| Path | Why | If missing |
|---|---|---|
| The vault tree, two levels | The Phase 1 map | There is no vault. Stop |
| `02 Context/me.md` | Who the user is, voice, active projects: this is what decides the destination | **Stop.** Without it the routing becomes a guess |
| The most recent file in `01 Daily/` | Context of the last session | Go on without it and say you did |
| `AIOS/knowledge-routing.md` | The canonical destination table | Use the Phase 2 table and say you did not confirm |

### Writes

| Path | What | Frontmatter |
|---|---|---|
| The destination folder of each moved note | The **moved** file, with `03 Projects/{name}/` created when needed | ensures `type`, `date`, `status`, `tags` |
| Any moved note | The connecting wikilinks. Every note ends up with at least one inbound or outbound link | preserves the body |
| `05 Archives/` | The redundancy, moved. Several on the same theme get a short `05 Archives/{theme}/README.md` | preserves the original |
| `knowledge/index.md` | The routed notes, if the file exists | already exists |
| `02 Context/me.md` | **Only** the routing rule the person corrected, at the moment they corrected it (rule 5 of [[operating-rules]]) | already exists |

### Never writes

| Not this | Owner |
|---|---|
| Renaming, moving or deleting a system folder (`00 Inbox`, `01 Daily`, `02 Context`, `03 Projects`, `03 Intelligence`, `04 Resources`, `05 Archives`, `AIOS/`, `knowledge/`, `.claude/`) | Nobody. The hooks use these exact paths and touching them breaks the agent |
| `README.md`, `CLAUDE.md` or any `index` treated as an orphan | Nobody. They are structural and correct as loose nodes in the graph |
| The body of any note | Its author. Here only location, frontmatter and wikilinks change |
| Moving in bulk without the "go ahead" from Phase 3 | The vault owner. It is the only approval this command requires |
| An invented destination | Nobody. Without certainty, ask in Phase 2 or send it to `00 Inbox/` |
| Deleting anything | Nothing. Everything that leaves goes to `05 Archives/` |
| Translating content, a path or a frontmatter key | Nobody. The language of the conversation changes; the language of the file does not |
| A numbered log in `logs/` | The `eiirp` skill, or whoever did the work |

If execution runs into one of these lines, say so in the Phase 5 summary and leave the file alone. A stub written by the wrong skill is worse than an honest gap.

---

## Phase 1: Map (change nothing)

1. List the vault's current folder tree (up to 2 levels).
2. Identify the **orphan notes**: `.md` files the user created or pasted that are loose. A note is an orphan if:
   - it has no outbound `[[ ]]` wikilink AND no other note links to it, OR
   - it sits at the vault root or in `00 Inbox/` with no clear destination.

   **Always exclude** `README.md`, `CLAUDE.md`, any `index`, and notes that already live correctly inside a project or context subfolder and are already linked.
3. For each orphan note, say in 1 line what it seems to be.
4. Show this list to the user. Do not change anything yet.

---

## Phase 2: Classify and ask

Classify each orphan note using this routing:

| Type of content | Destination |
|---|---|
| Identity, avatar, voice, positioning, promise, offer | `02 Context/` |
| Real project (course, product, marketplace, client) | `03 Projects/{name}/` |
| Framework, method, swipe, template, reusable prompt | `04 Resources/` |
| Market or competitor research, strategic decision | `03 Intelligence/` |
| Draft with no clear owner | `00 Inbox/` |

**Where the destination is obvious, decide on your own.** Where it is NOT obvious, ask via AskUserQuestion, **one question at a time**, with the folders as options. Also ask when:

- **Duplicates:** two notes look like the same thing.
  - Question: "`{{note A}}` and `{{note B}}` look like the same content. What should I do?"
  - Header: `Duplicate`
  - Options: `Merge into one` / `Keep A, archive B` / `Keep B, archive A` / `Keep both`

- **"CONSOLIDATED" versions:** several files look like versions of the same doc.
  - Question: "I found {{N}} versions of '{{theme}}'. Which is the good one? The others go to 05 Archives."
  - Header: `Good version`
  - Options: list the files as options, plus `Keep all`

- **Abandoned draft:** an old, empty or clearly discarded note.
  - Question: "`{{note}}` looks like an abandoned draft. Archive it in 05 Archives?"
  - Header: `Archive?`
  - Options: `Yes, archive` / `No, it matters, keep it` / `You decide where it goes`

- **Ambiguous destination:** there is no way to tell the folder.
  - Question: "Where does '`{{note}}`' go? Summary: {{1 line}}."
  - Header: `Destination`
  - Options: `02 Context` / `03 Projects` / `04 Resources` / `03 Intelligence` / `00 Inbox`

Gather the doubts and resolve all of them before building the plan. Do not comment between questions, go straight to the next one.

---

## Phase 3: Plan (wait for the "go ahead")

Build the final plan and STOP:

```
ORGANIZATION PLAN

Move ({{N}}):
- {{note}} -> {{destination folder}}
- ...

Archive in 05 Archives ({{N}}):
- {{note}}: reason
- ...

Wikilinks to create:
- {{note}} links to {{note or hub}}
- ...
```

Ask: "Can I run it? (remember to close Obsidian first)". Only move on to Phase 4 with explicit approval.

---

## Phase 4: Execute (only after approval)

Work silently:

1. **Move** each note to its destination folder. Create project subfolders (`03 Projects/{name}/`) when needed.
2. **Frontmatter:** ensure `type`, `date`, `status`, `tags` on every moved note. Fill in what is missing based on the content.
3. **Wikilinks:** connect each note to the context it belongs to. Notes on the same theme link to each other (e.g. avatar, promise and method reference each other and point to the `02 Context` hub). Every note must end up with at least 1 inbound or outbound link.
4. **Archive:** move redundancy to `05 Archives/` (never delete). If you archive several on one theme, create a short `05 Archives/{theme}/README.md` saying what it is and why.
5. **Index:** update `knowledge/index` with the routed notes, if the file exists.

---

## Phase 5: Summary

Short message, no fluff:

> "Organized.
> - Moved: {{N}} notes to {{folders}}
> - Linked: {{N}}
> - Archived: {{N}} in 05 Archives
> - Still open: {{0 or the list of what you could not decide}}
>
> You can reopen Obsidian. The graph should be connected now."

---

## Rules

- Always auto-save. Never ask permission to save, only to move in bulk (Phase 3).
- Never invent a destination. If you do not know, ask (Phase 2) or drop it in `00 Inbox`.
- Never delete. Everything that leaves goes to `05 Archives`.
- Never touch the system folders, README, CLAUDE or index.
- If the user corrects a routing, save the rule in `02 Context/me.md` so the mistake does not repeat.
