---
name: roundtable
description: Multi-expert strategic council. Use for genuinely multi-dimensional decisions (pricing, GTM, conversion, growth, retention), or when the user says 'run a roundtable', 'what would the experts say', 'get me a council on this' - selects 3-5 expert lenses, each argues from their own framework, surfaces tensions, then synthesizes a recommendation. Do not use it for execution tasks with a clear right answer, or to stress-test the user's own plan one question at a time (that is grilling).
type: skill
skill: roundtable
status: active
date: 2026-05-12
tags: [skill, aios, strategy, expert-council, decision-support, brains]
---

## Skill: Expert Roundtable

Run a structured multi-expert consultation on any strategic, product, or business problem. Each expert speaks from their own frameworks and mental models: not as a generic advisor, but from the specific lens documented in their brain file.

Invoke with `/roundtable {problem or question}`.

---

### When to Use

Use this skill when a decision or problem is genuinely multi-dimensional, where marketing logic, product logic, business strategy, and behavioral psychology would each pull in different directions, and you need to surface the tension before committing to a path.

Good triggers:
- "Why is this landing page not converting?"
- "Should we launch with freemium or reverse trial?"
- "How do we price the booking app for independent salons?"
- "What is the right next move to grow from 10 to 50 customers?"
- "This email sequence has low open rates. What's wrong with it?"

Not a good fit for: execution tasks with a clear right answer, technical implementation questions, routine content creation.

---

### Expert Selection

Do not always pull the same experts. Select 3 to 5 based on which domains are most relevant to the specific problem. Use this routing guide:

| Problem domain | Primary experts |
|---|---|
| Landing page / copy not converting | joanna-wiebe, robert-cialdini, dan-ariely |
| Pricing design | dan-ariely, patrick-campbell, alex-hormozi |
| Offer design (what to offer, not how to say it) | alex-hormozi, dan-ariely, patrick-campbell |
| Brand narrative / homepage structure | donald-miller, april-dunford, joanna-wiebe |
| Product positioning / messaging | april-dunford, marty-neumeier, donald-miller |
| Go-to-market strategy | wes-bush, elena-verna, april-dunford |
| Growth system design | brian-balfour, casey-winters, andrew-chen |
| Email sequence / nurture | brennan-dunn, joanna-wiebe, robert-cialdini |
| Retention and churn | lincoln-murphy, brian-balfour, nir-eyal |
| Customer onboarding / time-to-value | lincoln-murphy, nir-eyal, alex-hormozi |
| Cold outreach / sales | steli-efti, aaron-ross, robert-cialdini |
| Customer discovery / validation | rob-fitzpatrick, teresa-torres, joanna-wiebe |
| Product strategy and roadmap | marty-cagan, teresa-torres, shreyas-doshi |
| Brand and differentiation | marty-neumeier, april-dunford, donald-miller |
| Agency pricing / client work | chris-do, alex-hormozi, april-dunford |
| Agency positioning / escaping commodity | chris-do, april-dunford, marty-neumeier |
| AI workflow or tooling | ethan-mollick, simon-willison |
| Startup strategy and PMF | paul-graham, sam-altman, rob-fitzpatrick |
| Long-term defensibility | hamilton-helmer, clayton-christensen |
| SaaS metrics and scaling | jason-lemkin, patrick-campbell, lincoln-murphy |
| Solo founder / bootstrapped | pieter-levels, marc-lou, dhh |
| Personal brand architecture / KPI positioning | daniel-priestley, david-perell, seth-godin |
| Building an oversubscribed business or practice | daniel-priestley, alex-hormozi, april-dunford |
| Creator-to-product trajectory / audience-first | nathan-barry, daniel-priestley, brennan-dunn |
| Focus, output quality, solo founder productivity | cal-newport, shreyas-doshi, dhh |
| Activation rate is low / aha moment diagnosis | lenny-rachitsky, lincoln-murphy, nir-eyal |
| NRR below 100% / growth accounting | lenny-rachitsky, patrick-campbell, lincoln-murphy |

If the problem crosses domains, pull from the relevant rows, but cap at 5 experts. More is noise.

---

### Output Format

Produce the roundtable output in this structure:

---

**Problem:**
[State the problem clearly in one sentence.]

---

**The Council**

List the selected experts and the primary framework each brings to this problem.

---

**[Expert Name]: [Primary Framework]**

*"[A direct quote or paraphrase in their voice: how they would frame this problem based on their documented philosophy]"*

What [Expert] sees:
- [Specific observation about this problem through their lens]
- [The framework they would apply and what it reveals]
- [Their specific recommendation or next question]

Relevant framework: [Name the specific framework from their brain file]

---

[Repeat for each selected expert]

---

**Where They Agree**

List the consensus points: what two or more experts, coming from different frameworks, independently recommend.

---

**Where They Diverge**

Surface the genuine tensions. Where would these experts argue? Name the trade-off explicitly. Do not smooth over real disagreements. The tension is often where the important decision lives.

---

**Synthesis: The Prioritized Move**

Based on the council's analysis:

1. [Highest-priority action, grounded in the expert consensus]
2. [Second move: resolves the main tension or addresses the leading objection]
3. [Optional third move: longer-horizon consideration]

**The watch-out:** [The thing the council collectively warns against: the most common failure mode for this type of problem]

---

### Rules for Running a Good Roundtable

**Speak in each expert's voice, not a generic voice.** A roundtable where all experts sound the same is not a roundtable. It is one voice with five names attached. Each expert should challenge, reframe, or contradict in ways consistent with their documented mental models.

**Allow genuine disagreement.** Wes Bush and DHH will disagree about growth strategy. April Dunford and Brian Balfour will disagree about what to optimize first. Surface the disagreement. The user is not served by artificial consensus.

**Name the framework explicitly.** Every recommendation should be traceable to a specific framework in the expert's brain file. This is not opinion generation. It is framework application.

**Do not pad.** Three sharp expert perspectives with a clean synthesis is better than five vague ones. Quality over quantity.

**Link the brain files.** At the end of the roundtable output, list the brain files consulted so the user can go deeper on any expert's framework.

---

### Example Invocations

```
/roundtable The booking app's pricing page is not converting: 3 tiers visible, most signups go to Solo (cheapest), almost nobody upgrades
```

```
/roundtable Should the booking app launch with a free trial or a reverse trial given our current 5 paying customers?
```

```
/roundtable The email sequence after signup has 40% open rate on day 1 but drops to 8% by day 5. What's wrong?
```

```
/roundtable We need to go from 10 to 50 customers in the next 60 days. What is the right growth move?
```

---

### Output Location (Optional)

If the roundtable is for a consequential strategic decision, save the output to:

`03 Intelligence/decisions/YYYY-MM-DD-roundtable-{topic}.md`

Use the same frontmatter as a decision record. The roundtable output is the "alternatives considered" section in permanent form.
