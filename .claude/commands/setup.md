---
description: Fills in the vault's context (who you are and how you work) with short questions, reads the links and files you point to, and proves at the end that the context went in
---

# Setup: your context

You are going to fill in `02 Context/me.md`, the file the AI reads at the start of every session. Run the phases in order. Speak in the language of the message that called the command (default English); file names, folders and frontmatter keys are not translated.

## Rules for this command

- **Never invent.** A field with no answer is written as "not defined yet". Data taken from a link or file goes in labeled "(from the site, to confirm)" until the person confirms it.
- **One question at a time.** The person can answer "skip" to any of them.
- **A single context file:** `02 Context/me.md`. Do not create other identity files, a file at the vault root, or a new folder.
- **Do not announce a command or skill that is not in `AIOS/index.md`.**
- Work silently when writing: do not narrate file by file.

## Phase 0: read the state

Read `02 Context/me.md`.

- If the frontmatter has `status: draft` or the fields are empty, this is the first run: go to Phase 1.
- If it already has real content, this is an update: say in one line what is already filled in, ask only about what is empty or "not defined yet", and never overwrite what exists unless the person asks.

## Phase 1: welcome

Send this message and nothing else:

> "I'm going to build this vault's context in three steps: reuse what already exists about you (optional), ask nine short questions, and show you what was saved. You can answer 'skip' to any question."

## Phase 2: reuse what already exists (optional)

Ask, in a single message:

> "Before the questions, three shortcuts, all optional: (1) your public links, like a website, portfolio, Instagram or LinkedIn; (2) files that describe your work, like a CV, a presentation or a list of services; (3) another AI that already knows you, like ChatGPT. Send me whatever you have, or answer 'none'."

- **Links:** read each one. If a link does not open, say which one and move on. Note what you found for each field of `me.md`.
- **Files:** read them and take notes the same way. If the file is outside the vault, do not copy it in without asking.
- **Another AI:** read `.claude/commands/import-context.md` and run that flow right here, then come back to Phase 3.

What you found becomes a **proposed answer**: in Phase 3, instead of asking from scratch, show what you found and ask for confirmation ("Your site says X. Is that right?").

## Phase 3: the nine questions

One at a time, in this order. Skip any that was already answered and confirmed in Phase 2.

| # | Question | Field in `02 Context/me.md` |
|---|---|---|
| 1 | What is your name, and what do you do, in one sentence? | Me and my work: Name · What I do, in one sentence |
| 2 | Who do you serve or work for? Describe the typical client, employer or audience. | Me and my work: Who I serve or work for |
| 3 | Where do you work (city, region, remote), and do you work alone or with other people? | Me and my work: Where I work · Who I work with |
| 4 | What is your role, and what will you use this vault for day to day? | How to work with me: Role and what I use this vault for |
| 5 | How do you want me to answer: short and direct, or explained? Is there any way of being addressed that you dislike? | How to work with me: How to address me and the tone of answers · Answer language |
| 6 | What tools do you use today (task manager, spreadsheets, messaging, email, calendar)? | How my work happens today: Tools in use |
| 7 | What are the three repetitive tasks that take the most of your time? | How my work happens today: The three repetitive tasks that take the most time |
| 8 | What can never go wrong in your work (deadline, regulation, someone else's data)? | How my work happens today: What can never go wrong |
| 9 | What should I never do without asking you first (send a message, delete, publish, touch money)? | What the AI never does here without asking |

If an answer mentions a project or a line of work in progress, keep the name for Phase 4.

## Phase 4: save

1. **`02 Context/me.md`:** fill in each field with the real answer, in the person's words. Change `date` to today's date and `status` to `active`. Skipped field: "not defined yet". Keep the file's sections and order; do not delete "Permanent corrections".
2. **`AIOS/project-map.md`:** for each project mentioned, add a block in the format of the "Block template" in the file itself, and replace the "no project registered" notice. Do not create the folder in `03 Projects/` now: it is created at the project's first real piece of work.
3. **`AIOS/tools.md`:** do not touch it. The tools from question 6 are the ones the person **uses**, not the ones the AI can reach; only what was connected and proven with a real read goes in there.
4. **`AIOS/open-loops.md`:** one line per field left as "not defined yet" and per piece of data marked "(to confirm)", pointing to `[[me]]`.
5. **`01 Daily/YYYY-MM-DD.md`:** record the session in the format of `01 Daily/CLAUDE.md`: what was filled in, what was left open, where each piece of data came from (direct answer, link, file, another AI).

## Phase 5: prove

1. Reread `02 Context/me.md` from disk.
2. Run `python "04 Resources/tools/check-note.py" "02 Context/me.md"` and show the output. If it fails, fix it before moving on.
3. Give back to the person, in six lines at most, who they are and how they work, written from the file. Then list what was left as "not defined yet" or "to confirm".

If anything in the summary is wrong, the correction goes into `me.md` right away.

## Phase 6: the next step

Close with:

> "Context saved. Close this session and open it again in this folder: from the next one on, I start out already knowing who you are. For the first real piece of work, hand me one of your documents or links and say 'process this into the vault'."

If the person asks what else can be done, answer from `AIOS/index.md`.
