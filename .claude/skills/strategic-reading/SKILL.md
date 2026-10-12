---
name: strategic-reading
description: Applied synthesis of a source. Use when the user drops an article, book or video and says 'read this for X', 'what do I do with this', 'how does this apply to my project' or 'give me the playbook' - extracts only what applies to the active project and turns it into next actions. Do not use it for pure capture ('just save this' is ingest) or for a batch of transcripts (that is curate-transcripts).
type: skill
skill: strategic-reading
status: active
date: 2026-06-11
tags: [skill, aios, reading, research, synthesis, portable]
---

## Skill: Strategic Reading

Read a source (article, transcript, book, competitor post, thread) through the lens of a specific problem the user is facing right now, and output a playbook, not a summary. The difference: a summary tells you what the text says; a playbook tells you what to DO about your situation because of it.

---

### When To Use This Skill

Run when:
- The user drops a source and says "read this for {problem}", "what do I do with this", "how does this apply to {project}", or "give me the playbook".
- A competitor, expert, or news piece is clearly relevant to an active decision (a launch, a positioning call, a feature, a pricing move).

Do NOT run it for pure capture ("just save this"). That is the `ingest` skill. Strategic Reading always has a problem to aim at. If the problem is not stated, ask for it in one line before reading.

---

### What This Skill Does

Produces a problem-anchored playbook: the tactics worth stealing, the traps to avoid, and concrete short / medium / long-term moves for the user's actual situation. Saved to the relevant project so the thinking is reusable, not lost in chat.

---

### Inputs Required

- The source (URL, file, pasted text, or transcript). For YouTube use yt-dlp, never WebFetch.
  For **x.com / Twitter**, WebFetch always returns **HTTP 402**: use
  `tavily_extract` with `extract_depth: "advanced"`, which renders the JS and returns the whole post
  (validated on 2026-08-06, 6 long posts in one call). The result blows past the token limit,
  so save it to a file: strip the markdown noise and split it by author **before** reading.
  Code blocks and prompts that are images or embeds do not come through. Record that as an access limitation.
  Open a browser only if this fails.
- The problem or decision to read against (one sentence). Ask if missing.
- The relevant project context (read its `README.md` so the playbook is grounded in reality, not generic).

---

### The Process

1. Confirm the lens. State the problem in one line and the project it serves. If unclear, ask.
2. Read the source in full. No skimming.
3. Extract the **playbook**: what the source does that works, the underlying mechanism (why it works), and what the user could borrow.
4. Extract the **counter-tactics**: the traps, the parts that do NOT apply to the user's context, where copying it blindly would hurt.
5. Map to **moves**: short-term (this week), medium-term (this month), long-term (this quarter). Each move concrete and assigned to a project.
6. Close with **gap analysis** per the answer discipline in [[operating-rules]]: what the source does NOT answer for this problem, what still needs testing or research.
7. Save the playbook to the project (`research/{slug}.md` or `notes/{slug}.md` per [[knowledge-routing]]). Cross-link the source and the project. Report the path.

---

### Output Format

```markdown
---
type: playbook
date: YYYY-MM-DD
status: active
tags: [playbook, strategic-reading]
project: [[Project]]
---

> [!summary] Lens
> Problem: {one line}. Source: {title + link}.

## Playbook (steal this)
- **Tactic:** {what they do}. **Mechanism:** {why it works}. **For us:** {how to borrow it}.

## Counter-tactics (do not copy blindly)
- {trap or non-applicable part, and why}

## Moves
- **This week:** {concrete action}, routed to [[Project]]
- **This month:** {concrete action}
- **This quarter:** {concrete action}

## Gap analysis
- {what the source does not answer; what to test next}
```

---

### Examples

Run: The user drops a competitor's launch post and says "read this for the course launch".
Output: a playbook saved to `03 Projects/Online Course/research/{competitor}-launch-playbook.md` with tactics to borrow, traps (their audience is not the user's), and 3 dated moves, cross-linked to the project README (`03 Projects/Online Course/README.md`).

---

### Anti-Patterns

- Do not produce a neutral summary. Every line must serve the stated problem.
- Do not invent a problem to read against. Ask for it.
- Do not leave the playbook in chat. It goes to the project or it did not happen.
- Do not copy a tactic without naming the mechanism and checking it fits the user's context.

---

## Meta

Created: 2026-06-11 (adapted from GBrain `strategic-reading`)
Last revised: 2026-06-11
