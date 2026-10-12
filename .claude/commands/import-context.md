---
description: Imports context from another AI (ChatGPT, Claude, Gemini). Generates a prompt for you to paste there, you paste the answer back, and the vault is updated with real depth
---

# Import Context: From another AI into your vault

Use it when you want to update your vault with context another AI already has about you. It works after `/setup` too: the more context, the better.

---

## Language

Detect the language of the message that invoked this command and use it in every question and message.

Default English. Any other language if the user wrote in it.

---

## Phase 1: Choose the source AI

Ask via AskUserQuestion:

- Question: "Which AI do you want to import context from?"
- Header: `Source AI`
- Options:
  - `ChatGPT`: "It has active memory across conversations if you turned it on."
  - `Claude (claude.ai)`: "No persistent memory: it uses the context of that conversation."
  - `Gemini`: "It can search email and Drive if it is Workspace."
  - `Perplexity`: "It has 'spaces' with persistent context."
  - `Another AI`: "A generic prompt that works in any of them."

Keep the choice.

---

## Phase 2: Generate the prompt

Print the appropriate prompt in a clearly visible markdown code block. Before the block, write:

> "Copy the prompt below, paste it into your conversation with {{chosen AI}}, and wait for it to answer. When you have the full answer, paste it here and I will process it."

### Prompt: ChatGPT

```
I am setting up a personal AI system in another tool. Please give me back everything you know about me, based on our previous conversations and your memory. Organize it in markdown, in this exact structure:

## 1. Identity
Name, age (if you know it), location, relevant personal context.

## 2. Profession
Current role, company, industry, for how long, main responsibilities, clients or stakeholders.

## 3. Goals
Short term (90 days), medium term (1 year), long term (3-5 years). If you do not know one of the horizons, say "no data".

## 4. How I work
Routine, tools I use (Notion, Linear, Slack, etc.), style, preferences, productive hours.

## 5. My voice
How I write, words I use, words I avoid, tone (formal/casual/technical), style references.

## 6. Audience
Who I serve professionally, who my audience is if I create content, the profile of those people.

## 7. Channels
Where I publish or communicate (LinkedIn, Instagram, YouTube, newsletter, blog, etc.). Frequency and focus of each channel.

## 8. Current challenges
What is worrying me, where I am stuck, main pains or blockers.

## 9. Relevant history
Important decisions I made, projects that matter, lessons that marked me.

## 10. Network
Important people in my professional life (mentors, partners, frequent collaborators).

## 11. Resources
Books, creators, frameworks, tools I follow or use as reference.

Rules:
- If you have no information about an item, write "no data". Do NOT invent.
- Be concise. Bullet points, not long paragraphs.
- Include dates when you know them.
- Return only the markdown, with no extra comments before or after.
```

### Prompt: Claude (claude.ai)

```
I am setting up a personal AI system in another tool. Based on everything you know about me IN THIS conversation (and any context I pasted earlier), give me back a complete summary in markdown, in the structure below:

## 1. Identity
Name, age (if you know it), location, relevant personal context.

## 2. Profession
Current role, company, industry, for how long, main responsibilities, clients or stakeholders.

## 3. Goals
Short term (90 days), medium term (1 year), long term (3-5 years). If you do not know one of the horizons, say "no data".

## 4. How I work
Routine, tools I use (Notion, Linear, Slack, etc.), style, preferences, productive hours.

## 5. My voice
How I write, words I use, words I avoid, tone (formal/casual/technical), style references.

## 6. Audience
Who I serve professionally, who my audience is if I create content, the profile of those people.

## 7. Channels
Where I publish or communicate (LinkedIn, Instagram, YouTube, newsletter, blog, etc.). Frequency and focus of each channel.

## 8. Current challenges
What is worrying me, where I am stuck, main pains or blockers.

## 9. Relevant history
Important decisions I made, projects that matter, lessons that marked me.

## 10. Network
Important people in my professional life (mentors, partners, frequent collaborators).

## 11. Resources
Books, creators, frameworks, tools I follow or use as reference.

Rules:
- If I did not share information about an item in this conversation, write "no data".
- Do not invent. Do not guess. Only what is explicit in our history here.
- Be concise. Bullets, not paragraphs.
- Return only the markdown.
```

### Prompt: Gemini

Use the ChatGPT prompt above, plus this paragraph at the end:

```
If you are Gemini integrated with Google Workspace, you can also pull context from my recent emails, docs and Drive to enrich the answer. If you do, clearly mark which information came from where (e.g. "[from Drive: Q1 2026 Plan]").
```

### Prompt: Perplexity or another AI

Use the ChatGPT prompt with no changes.

---

## Phase 3: Wait for the answer

Tell the user:
> "Waiting for you to paste the answer here. All at once is fine."

Wait for the user's next message. When they paste it:
- Identify each numbered block (`## 1. Identity`, `## 2. Profession`, etc.)
- Extract the data from each block
- Ignore "no data": do not try to fill in those fields

---

## Phase 4: Update the vault

Work silently. Do not narrate each file.

### 4.1: `02 Context/me.md`

Read the current file.
- Empty field (nothing after the colon) or "not defined yet": fill it in with the extracted data.
- Field with real content: **add**, do not overwrite. In case of conflict, what is already in the file wins, and the other AI's data goes in as a complement labeled "(imported, to confirm)".
- On the first import, change `date` to today's date and `status` to `active`.

Map the AI's blocks to the sections of `me.md`:
- Block 1 (Identity) → "Me and my work" (name) and "How to work with me" (how to address me, answer language)
- Block 2 (Profession) → "Me and my work" (what I do, who I serve or work for, where I work, who I work with) and "How to work with me" (role)
- Block 4 (How I work) → "How my work happens today" (tools in use)
- Block 8 (Challenges) → "How my work happens today" (repetitive tasks, what can never go wrong)
- Blocks 3, 5, 6 and 7 (goals, voice, audience, channels) have no section in `me.md`: they go to the derived files below.

### 4.2: Derived files

**Block 3 (Goals) with substance → create or update `02 Context/strategy.md`:**

```markdown
---
type: reference
status: active
date: YYYY-MM-DD
tags: [strategy, goals]
---

# Strategy

## 90-day goal
{{from block 3}}

## 1-year goal
{{from block 3}}

## 3-5-year goal
{{from block 3}}
```

**Blocks 5+6+7 (voice, audience, channels) with substance → create or update `02 Context/brand.md`:**

```markdown
---
type: reference
status: active
date: YYYY-MM-DD
tags: [brand, voice]
---

# Brand and Voice

## Audience
{{block 6}}

## Channels
{{block 7}}

## Voice and Tone
{{block 5}}
```

**Block 11 (Resources) with books, frameworks, tools → save to `04 Resources/personal-references.md`:**

```markdown
---
type: reference
status: active
date: YYYY-MM-DD
tags: [references, resources]
---

# References and Resources

{{content of block 11 organized by category: books, creators, frameworks, tools}}
```

### 4.3: Daily note

Append to today's daily note (`01 Daily/YYYY-MM-DD.md`) or create it if it does not exist:

```markdown
## Context import: {{AI used}}

- **Source:** {{ChatGPT / Claude / Gemini / etc.}}
- **Updated:** {{list of files updated or created}}
- **Next steps:** review `me.md` and adjust anything from the AI that does not match reality.
```

---

## Phase 5: Confirmation

Short message:

> "Context imported from {{AI used}}. I updated:
> - `02 Context/me.md`
> - {{list other files created or updated}}
>
> I recommend opening `me.md` and reviewing it: AIs get some details wrong, especially dates and names.
>
> Next step: hand me a real document or link and say "process this into the vault"."

---

## Rules

- Never overwrite real data in `me.md` with data from the AI: add or complement.
- If the AI answered "no data" for a block, leave the section as it is in the template (or remove it if empty).
- Confirm dates: AIs often get years and deadlines wrong. If something sounds off, mark it with `{{verify}}` in the daily note.
- Do not invent. If the AI did not say it, do not fill it in.
- Use the user's exact words (as they came from the AI) when possible: do not paraphrase tone of voice.
