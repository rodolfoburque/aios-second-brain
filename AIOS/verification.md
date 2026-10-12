---
type: harness
date: 2026-08-06
status: active
tags: [harness, verification, quality, aios, operations]
---

# Verification: how I know the work came out right

> **Component 4 of the 7 in the harness**, and the one with the highest documented return (2-3x). The harness audit ruler and the setup scorecard do not ship with this vault: when this vault gets its own audit, link it here.
>
> The problem this file solves: a person pointing out "that's not it, it was the other thing" teaches the agent nothing. The AI needs to know **on its own** whether the work is right, before saying it is finished.

## The fixed rule

**I do not declare anything done without running the verification and pasting its output.**

With no pasted output, the right thing to say is *"implemented, not verified"*. The three forbidden phrases, because they look like verification and are not:

- *"it should work"* / *"it should be right"*
- *"I reviewed it and it is correct"*: the model's self-assessment is biased; it does not count as a PASS
- *"the tests probably pass"*

And the corollary that already cost 13 days of a stalled funnel in the source vault: **configuration state is not proof that it works.** An `APPROVED` template plus an `isActive` automation and no message going out is a green dashboard over a dead system. The proof has to be of the **effect**, not of the state.

The second corollary, from 2026-08-12: **a subagent's report is not evidence, command output is.** A subagent that reports "I implemented it and it is working" is doing self-assessment, which is already in the list of forbidden phrases above. The same ruler applies: run the validation command and look at the exit code.

And the third, from the same session: **loading is not working.** A skill that shows up in the list of available skills and a command the harness can see prove that the file was read, nothing more. A new piece only goes from "installed" to "works" after it runs in real work.

The fourth, from 2026-08-12: **a resilience test only counts against the layer that actually goes down.** The keep-alive of a WhatsApp agent was "verified" by killing the `node` process, and the supervisor brought it back in 10s. What took it down for 1h06 was the **Windows task** being terminated, one floor up, where there was nothing. The test passed and measured the wrong layer. Rule: list the layers that can go down (connection, process, task, machine) and kill **each one**; the one that was not reproduced is not covered, no matter how green the test is.

The fifth, from 2026-08-23 (pattern extracted from benai-skills): **a live connector is proven with a cheap read, never with the status the tool declares.** Before scheduling a routine, building an automation or claiming that an integration is up, make a real **read** call per connector, never a write, and record the result as connected, degraded or absent. The source vault was fooled by status twice: `claude mcp list` answers "Connected" for a host that a corporate VPN is blocking, and the call that turns an automation on and off on a funnel platform returns `{}` without saying what state it left the automation in. The cost of skipping this is asymmetric: a routine scheduled against a dead connector fails in silence, piles up empty runs and only shows when someone notices that the result never arrived.


The sixth, from 2026-08-23: **the verifier needs to be verified too, and it errs on the HIGH side.** The five corollaries above are about not trusting the system being measured; this one is about not trusting the instrument. Four different tools, three different authors, the same bias: the hook auditor flagged 5 nonexistent scripts that existed, the wikilink checker overestimated the damage by 2.2x, a course's numbering flagged a missing module that the source already explained, and the vault intelligence metric flagged 44 isolated notes of which 41 were machine output. **A false positive costs the original problem plus the work of repairing what was fine**, and repairing the target based on an inflated report spreads the error across dozens of files. Before acting on a high report: sample 3 to 5 items by hand, and if one is false, fix the tool before the vault. If the pattern repeats here, the full method deserves its own note in `04 Resources/frameworks/`.

The seventh, from 2026-09-17: **a declared sweep with no denominator is a false PASS, and a string count of zero does not prove removal.** Two faces of the same mistake, found on the same day in a rebranding project for a product.

The first: the log of a purge declared the defect *"fixed in 10 files"*. It was: **10 of 41**. It was 25% and it read as 100%, because the sentence carried the numerator and hid the denominator. Every declaration of a sweep says **how many files were swept**, not only how many were changed, and names what was left outside the reach of the search.

The second: the same project declared two brands at **zero occurrences**, with both counts correct, and both of them showed up on the first screen of the product. Brand and data survive where the text does not exist as text: **split by markup** (`Old<span>Brand</span>`), **drawn** (the acronym in a `<text>` of an inline SVG), **as a config default** (the client's GA4 property, which is a number and not a name), **abbreviated** (`OB-Product.AI` slipping past a search for `oldbrand`), and **as a reference to a file already deleted** (`<img src>` pointing to nothing, served with HTTP 200 and `text/html` by the dev server).

What finds all five forms is the same thing, and it is cheap: **open the screen and look.** Two regex sweeps and an `npm run build` with exit 0 passed right over a 17px brand in the middle of the login screen.

## How to isolate a cause (the night of 2026-08-07, learned six times)

The rule above says how to prove that something **works**. This one says how to find out **why it does not work**, and it was born on a night when four plausible hypotheses were adopted as the cause before being tested.

**The vice, in one sentence: finding a real defect and adopting it as the cause without testing the link.** On 2026-08-06 and 07 it happened four times in a row with the same funnel. A template reclassified as MARKETING, a 3-minute delay, a time window and my own rebuild of the automation: all of them were **real** defects or changes, and **none** was the cause of the failure. Each one consumed a round of fixing that fixed nothing.

What finally separated them:

1. **An experiment with ONE variable.** A disposable, minimal automation, no delay, an approved template, `isActive` confirmed by a read, the same tag and the same contact. The only thing that changed was **who applied the tag**: through the API it did not fire (`executions: 0`), through the interface it fired (`executions: 1`, message delivered). With everything else equal, the conclusion has nowhere to run.
2. **Two independent signals agreeing.** The execution counter **and** the contact's message history. One signal alone lies: `POST /flows/execute` returned `200` and incremented the counter **without executing any step** when the flow had its entry point through triggers.
3. **Look for the counter-evidence before writing the rule.** The conclusion "a write through the API never fires" was knocked down by a line in the daily note of 2026-07-22 recording the opposite. The counter-evidence was in the vault itself.

**Corollary on the scope of the conclusion:** the test was done on the **MCP** and the rule came out written about **"API"**. Too wide, and it was about to enter permanent memory closing exactly the door (REST) that solved the problem. **The conclusion cannot be bigger than the experiment.**

**Corollary on intermittent failure (2026-08-13):** **the test has to last longer than the typical interval between occurrences**, and that interval is measured in the history **before** choosing the window, not guessed. An agent went down every 85-125 minutes; I declared that 15 minutes of observation would prove the fix, ran 17 clean ones and proved nothing, because it easily survived 20 intervals between one crash and the next. A short window against a rare event measures **the interval between the failures**, not the failure, and the clean result is indistinguishable from a real fix. When you cannot wait for the whole window, the honest thing is to say "applied, verdict in N hours" and name the command that will give the verdict.

**Corollary on unit tests:** a test that does not execute the real path attests to its own prose. The verification contract of the Slack bot passed 21 unit checks and would have broken 100% of the tasks in production, because the break was in the Windows `.cmd` shim, which no test touched.

## Master table

| Type of work | Done well (objective) | Done badly | Command/check that proves it |
|---|---|---|---|
| **Note in the vault** | frontmatter with `type`/`date`/`status`/`tags`; every wikilink resolves; no new orphan note | broken link, note with no incoming link, missing frontmatter, markdown link to an internal file | `python "04 Resources/tools/check-note.py" <file|folder>` → exit 0 |
| **Site / landing page** | build passes; the new route answers 200 locally; no type errors | "I pushed it and did not look"; the error only shows up on deploy | `npm run check && npm run build` at the project root; then `npm run preview` and open the route |
| **Performance of a published page** | a number measured at a citable source, not an impression | "it got fast" | PSI API (`PSI_API_KEY`, host `pagespeedonline.googleapis.com`) or the `lighthouse` MCP → keep the 4 scores |
| **Artifact / proposal for a client** | every piece of data has a cited public source; every link opens; positioning present (who you are, why the contact, the document as a demo) | a plausible number with no origin; a dead link in the material that goes to the prospect | check each claim against the saved source; `curl -sI <url>` on each external link → 200; the positioning comes from [[02 Context/me]] |
| **Post / carousel** | the render comes out with no clipped text and no overlap; measured on the image, not on the spec | approving by looking at the JSON | render with whatever engine is installed (this vault does not ship one) and open the final image; a comparison sheet before publishing. Measure, do not deduce |
| **Application code** | the test for the path that changed passes; it runs locally before any upload | "it compiled, so it is right" | the project's runner (`npm test`, `pytest`); if there is no test for the path, writing the test **is** part of the task |
| **Content consistency** | the slot in the window has a finished piece, buffer ≥ 7 days, 3 wildcards | "I publish whatever I produce that day"; a slot found empty the day before | `python "04 Resources/tools/check-content.py"` → exit 0 (optional, does not ship with this vault: without it, check the content queue by hand). Critical becomes an alert in the alerts channel; a warning stays in the console, otherwise the checker turns into noise |
| **Script that runs on its own** (hook, cron, bot) | passes the 4 criteria: VERIFICATION, OBJECTIVE STOP, OBSERVABILITY, CEILING | "it has never fired wrong so far" | a test with falsified input before turning it on. Reference in this vault: `.claude/hooks/test-hooks.py` |
| **Service that has to stay up** (bot, agent, daemon) | comes back on its own after **each** layer is taken down, and comes back **connected**, not just "Running" | killing only the process and declaring the keep-alive verified | take down one layer at a time (connection, process, task/service) and time the return by reading the connection log |
| **Funnel automation** (WhatsApp, DM, email) | **evidence of a delivered message** in the contact's history | card created, tag applied, counter at zero | fire the trigger for real and read the contact's message history; check `category` against the template's `previous_category` |
| **Transactional email** (lead, notice, confirmation) | the message **opened in the recipient's inbox**, with the body checked | `delivered` in the provider's dashboard; "the log says it went out" | read the inbox (through the email connector) and check the body and the accented characters. ⚠ A provider already marked `delivered` on 2 emails that the destination inbox **discarded in silence**: not spam, not trash. A sender with no authenticated domain is the likely cause |
| **Connector before scheduling** | one cheap read per connector, with the result recorded: connected, degraded or absent | trusting the status that the listing tool declares | a real read call per connector **before** creating a cron, hook or routine; `claude mcp list` alone does not count |
| **Change to a credential / MCP** | tested through **both** paths before blaming the vendor | "their MCP is down" | `claude mcp list` + a raw call with the token; rule 20 of [[operating-rules]] |

## Detail by type, where the rule is subtle

### Note in the vault
The checker is `04 Resources/tools/check-note.py`. It has no opinion about content, only about what is mechanically verifiable: frontmatter, wikilink resolution, orphan notes and internal markdown links. **Run it before saying I filed something.** Exit 0 = passed; exit 1 = there are findings, and each finding comes with file and line.

A new orphan is the most expensive failure because it **does not scream**: the note exists, the content is there, and the vault simply never reaches it again.

### Site and landing page
`npm run check` (astro check) catches type and route errors that `build` sometimes swallows. Both, in this order. **Local preview before deploy** is a guardrail rule, not a verification rule ([[guardrails]]).

> [!warning] A green build is not correct copy
> On 2026-08-13 a landing page passed `check` and `build` with **0 errors** and the entire copy without accents ("maquina", "solucao", "voce"). No tool catches that: an accent is content, not syntax. **Only the render gives it away.** On a page in a language that uses accents, read the screen before declaring it done. The same goes for em dashes, which also compile clean.

**Before any local test, confirm which process you are testing against.** In the same session, four orphan dev servers survived the stop commands and held ports 4321-4324. I tested against one of them, without the new env vars, and the symptom was silent: the page answered 200 just the same. Census before the test: `Get-NetTCPConnection -LocalPort N -State Listen`.

### Artifact for a client
This is the type with the highest cost per error, because the error leaves the machine and reaches a third party. The verification is double: **factual** (a source per claim) and **of positioning** (the material has to show who you are, why the contact exists and serve as a demo of the system). Invented data in a diagnosis burns the prospect and the brand along with it.

### Funnel automation
The only accepted proof is a **delivered message**, read in the contact's history. A created card proves nothing, an applied tag proves nothing, the trigger counter proves nothing: all three have already shown green with the WhatsApp leg dead.

And the delivered message proves only the **step** that delivered it, not the funnel. On 2026-08-07 I declared the funnel fixed with a `POST` to the function and a message delivered 2 seconds later: real proof, right mechanism, wrong conclusion. Whoever walked the human path (form, go to the scheduling page, book) received **the wrong message in the wrong order**, because my API call never went through the interval in which the person disappears to pick a time.

> [!important] An API call does not replace the human path
> For a funnel with more than one event (form and booking are two), the verification only closes when **a person walks the whole path at their own speed** and the contact's history is read afterward. What the API call proves is that the plumbing exists; what the walk proves is that the order, the timing and the condition are right.
>
> Practical rule: write down beforehand which message **cannot** arrive in each state. Without that, reading the history becomes "a message arrived, so it worked", which is how the two mistakes of 2026-08-07 got past me in the middle of the night.

## Where this fits

Verification is a declared prerequisite for a **loop**: a loop without verification burns tokens and delivers nothing. While this layer is not running on its own, the systems stay at levels 1-3 of the loop ladder, never at 4.

---

Connected to: [[guardrails]] · [[operating-rules]] · [[hooks]] · [[Home]]
