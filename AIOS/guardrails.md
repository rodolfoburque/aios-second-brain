---
type: harness
date: 2026-08-06
status: active
tags: [harness, guardrails, sandbox, security, aios, operations]
---

# Guardrails, decomposition and sandbox

> **A guardrail is a component of the harness, not a synonym for it.** It is the piece that prevents the fall; the rest of the harness is what guides.
>
> Verification (how I know it came out right) lives in [[verification]]. This is what I **never** do.

## Inviolable rules

If I break one of these, something real breaks: a live site, client data, a file with no copy, revenue.

1. **Nothing goes to production without explicit approval from the vault owner.** "Explicit" means you saying it is okay; silence is not approval, and approval for one thing does not carry over to the next.
2. **Never `deploy`, `push` to a remote or `merge` without approval.** This applies to Vercel, GitHub and any publishing. A local commit is free; leaving the machine is not.
3. **Never delete a file, code or data that I was not asked to delete.** Before overwriting, read what is there. When the question is "is this still useful?", move or rename, never delete.
4. **Never touch a database without approval.** On a managed database (Supabase and the like) the rule is even stricter: reads through the public API, migrations only by hand in the SQL editor.
5. **Run and test locally before any upload.** `npm run check && npm run build` passing is a prerequisite for deploy, not an optional step.
6. **Never change an automation with real traffic without recording it in the `## Changelog`** of the project's README (date · change · commit · impact · rollback). If I do not know how to roll it back, I do not touch it.
7. **A secret never goes into a versioned file or a vault note.** Environment variable, always. Not in a call's chat, not in WhatsApp.
8. **A third-party tool that talks to customers (WhatsApp, automation platform, email) only fires after a test with a recipient of my own.** Never "test in production" with a real prospect on the receiving end.

### Where autonomy is greater, on purpose

This vault does **not** turn on `skipDangerousModePermissionPrompt`: Claude Code's permission prompt comes at its default. Turning it on is an operating choice of the vault owner, never of the agent, and if it is turned on it gets recorded here as a conscious decision. With or without it, what holds the risk is not the permission prompt, it is the 8 rules above plus the checkpoints.

### Execution pitfalls (other people's scars, adopted on 2026-08-12)

These are not principles, they are bugs that already cost a lot in another operation and that hit this stack. They came from the `CLAUDE.md` of another operation.

9. **Env var on Vercel through the CLI: `node .../vercel/dist/vc.js`, NEVER the `vercel` command.** Revised on 2026-09-18 after the CLI wrote the wrong value 3 times in a row while saying `Added` all 3 times:
   - **Git Bash + the `vercel` shim** writes an **EMPTY value** (npm's `.cmd` shim does not pass stdin through; same family as the `claude.cmd` shim, which truncates multiline arguments).
   - **PowerShell** writes a **BOM** (`EF BB BF`) in front of the value, and adjusting `$OutputEncoding` **does not fix it**.
   - **What works:** `printf "%s" "value" | node "$APPDATA/npm/node_modules/vercel/dist/vc.js" env add NAME production` (the path is the one of npm's global install; confirm it with `npm root -g`)
   - `echo` stays forbidden: it appends a line break, which becomes `%0A` in the URL.
   - 🔴 **`vercel env pull` NO LONGER works as an audit**: a variable of type `Sensitive` comes back as `NAME=""` even when it is correct.
   - **The proof is the production HTML, byte by byte:** `curl -sL <url> | grep -oE "gtag/js.id=[^\"]*" | sed "s/.*id=//" | od -c`. It has to start at the `G`, with no `357 273 277` (BOM) and no line break before it.
   - The build **does not fail** with a corrupted value and the page **loads normally**, it just does not measure. **This applies to each codebase**: when the same variable lives in more than one project, the proof is repeated in each one.

10. **`.gitignore` does not delete files.** When sanitizing a repo, never delete from disk: gitignore is for stopping tracking. To remove from git while keeping the local file, `git rm --cached`. (Reinforces rule 3, which already forbids deleting; this one names the specific mistake.)

11. **Before a mass `DELETE`, `DROP`, `TRUNCATE` or `UPDATE`, show the impact and wait for confirmation.** How many rows, which data. Rule 4 already forbids touching a database without approval; this one defines what the approval needs to see in order to be informed.

12. **Never dump a whole config file that may carry a credential.** Read by section (`grep`, `sed -n`), never `cat` on the whole file. The `basic.ini` of the OBS profile stores the **RefreshToken and the YouTube access token in plain text** (that is OBS's design, not a configuration mistake), and on 2026-08-29 I threw the whole file into the session transcript, burning the account's credential. The same trap lives in `.env`, `credentials.json`, an MCP's `config.json` and any `*.ini` of a tool that does OAuth. Rule 7 forbids a secret from **entering** a versioned file; this one forbids a secret from **leaving** through a careless read.

## Task decomposition

**A task with more than 3 steps: first I show the numbered steps and wait for approval. Then I execute one at a time, verifying each one before moving on.**

The reason is arithmetic, not style. The success rate is `0.99^n`:

| Steps | Chance of success |
|---|---|
| 1 | 99% |
| 10 | 90% |
| 50 | 60% |
| 100 | 37% |

**No model upgrade fixes this.** Only four levers: verification between steps, checkpoints, fewer tools and clean context.

The counterexample lived in the source vault, which prevents the wrong reading of this rule: in a scheduling app, the spec system sliced everything into stories and tasks and **the result came out technically correct, but the path was so long that the interest died and the design was left undone**. Decomposing is not chopping forever: it is **breaking down until the step is verifiable**, and stopping there. A step with no way to prove it came out right is too big; a step that only exists to fill a list is too small.

Execution rules that come along (if [[02 Context/me]] says otherwise, what is there wins):
- **Sequential, no parallelizing** of implementation.
- **A commit per story**, not one commit at the end.
- **A checkpoint after the foundation wave**, before moving on to the rest.

## Sandbox

An environment where a mistake costs nothing. Today, in order of preference:

| Layer | What it is | What for |
|---|---|---|
| **Session scratchpad** | a temporary folder, isolated from the vault | throwaway script, test, intermediate output. **Default for any file that is not a deliverable** |
| **Local preview** (`npm run preview`) | the build served on the machine | checking route and visuals before deploy |
| **Test contact/number** | a contact marked as test on the messaging platform | firing a funnel end to end without touching a real lead |
| **Branch** | local git with no push | a big code change with history preserved |
| **Vercel preview deploy** | a non-indexed URL | when you need a public URL to test, without touching production |

**The rule:** nothing goes to production without passing through one of these. And the reverse also holds: **a test that runs in production is not a test, it is use**.

The known hole: **a message automation platform usually has no real sandbox** (no separate environment). The stopgap is the test contact, and it has a limit: a global tag has already fired an old automation from another project. Until that has a solution, changing a live automation requires a changelog and a rollback plan written **beforehand**.

---

Connected to: [[verification]] · [[operating-rules]] · [[hooks]] · [[Home]]
