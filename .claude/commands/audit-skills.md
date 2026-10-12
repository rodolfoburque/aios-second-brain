---
description: Audits the vault's skill ecosystem. Runs the checker (check-skills.py) for the three surfaces and internal integrity, and does by hand only what requires judgment - overlap, description quality and coverage gaps.
allowed-tools: Read, Grep, Glob, Bash
---

# Audit Skills

A consistency audit of the whole ecosystem, not of one skill at a time. Runs with no input.

To **create** a new skill or **review** a single skill, the path is `skill-creator`, which has an eval harness. This command exists for what it does not do: look at the set.

## The three surfaces

A skill in this vault lives in three places, and the typical defect is that they drift apart silently:

| Surface | Where | Role |
|---|---|---|
| **Executable** | `.claude/skills/<name>/SKILL.md` | the source of truth, what runs |
| **Card** | `AIOS/skills/<name>.md` | a pointer that resolves the wikilink in the graph and decides routing |
| **Index** | `AIOS/index.md` | the table row that makes the skill findable |

House rule: **the card never copies the body of the executable**, because a copy diverges silently. The card points.

> [!note] `AIOS/skills/` does not ship with the vault
> Without the folder, `check-skills.py` skips the card contract (it prints `BLOCK A  no cards in this vault`) and still checks the inside of each skill. With the folder created and empty, it runs and flags each executable as `EXECUTABLE WITHOUT CARD`: that is the initial state of a new vault, not a defect to fix in bulk. Create the folder, and each skill's card when it needs to be found through the graph; until then the index (`AIOS/index.md`) is the minimum surface.

## Step 0: Run the checker before looking at anything by hand

> [!important] Added on 2026-08-14: steps 1 to 3 became mechanical
> ```bash
> python "04 Resources/tools/check-skills.py"
> ```
> It covers, with an exit code, what steps 1, 2 and 3 used to do by grep: inventory of the three
> surfaces, misalignment (executable without a card, dead pointer, card that became a copy,
> not in the catalog) and broken redirection (`GHOST SIBLING SKILL`). And it covers what
> no step here could see, because it looks **inside** the skill folder: dead reference,
> orphan reference, foreign path from an incomplete adaptation of a third-party pack, ghost MCP and ghost hook.
>
> **Paste the output into the report.** If it passes, steps 1 to 3 are closed and you do not
> redo them by grep: spend the effort on steps 4, 5 and 6, which require judgment that no regex
> can supply. If it fails, its finding **is** the audit's finding.
>
> It exists because nothing looked inside the skill folder: a reference the skill tells you to
> read before writing could contradict `SKILL.md` without anyone noticing.

## Step 1: Inventory of the three surfaces (covered by Step 0)

```bash
cd "<vault root>"
echo "== executables =="; ls .claude/skills/ | wc -l
echo "== commands ==";    ls .claude/commands/ | wc -l
echo "== cards ==";       ls AIOS/skills/ | wc -l
echo "== index rows =="; grep -cE "^\| \[\[AIOS[\\/]skills" AIOS/index.md
```

## Step 2: Misalignment between surfaces

```bash
# executable without a card (a skill that runs and nobody finds through the graph)
for d in .claude/skills/*/; do n=$(basename "$d"); [ -f "AIOS/skills/$n.md" ] || echo "NO CARD: $n"; done

# card without an executable or a command (a pointer aimed at nothing)
for f in AIOS/skills/*.md; do n=$(basename "$f" .md); \
  [ -d ".claude/skills/$n" ] || [ -f ".claude/commands/$n.md" ] || echo "ORPHAN CARD: $n"; done

# executable missing from the index
# search by the CANONICAL PATH in column 2, never by the wikilink:
# the index stores the wikilink as `skills/<n>\|<n>` and the backslash
# before the pipe makes any naive pattern match nothing or match everything.
# The index also mixes the / and \ separators, so test both.
for d in .claude/skills/*/; do n=$(basename "$d"); \
  if grep -qF "skills/$n/SKILL.md" AIOS/index.md || grep -qF "skills\\$n\\SKILL.md" AIOS/index.md; \
  then :; else echo "NOT IN INDEX: $n"; fi; done
```

> **First run in the source vault, 2026-08-12:** 50 executables, 22 commands, 88 cards, 87 index rows. No executable without a card. **One missing from the index: `prompt-auditor-4d`**, installed that morning with its card created and the table row forgotten. Fixed the same day. It is exactly the defect this command exists to catch: the skill runs, has a card, and does not show up for anyone searching the index.

**How to judge:** an orphan card is not necessarily a mistake. It can be a skill cataloged on purpose without being installed (an evaluated candidate, or a capability that exists as a command). What the card needs is to say which case it is, in the `kind` field of the frontmatter. An orphan card **without** a declared `kind` is a defect.

## Step 3: Broken redirection

The most common and most invisible defect: a skill tells you to use another one that does not exist here. It happens every time outside material is adopted, because the original author had a different ecosystem.

```bash
# names cited in "use X", "see X", backticks inside description and Out of Scope
grep -rhoE '\b(use|see) `?[a-z0-9-]{4,}`?' .claude/skills/*/SKILL.md \
  | awk '{print $2}' | tr -d '`' | sort -u > /tmp/cited.txt
ls .claude/skills/ > /tmp/existing.txt
comm -23 /tmp/cited.txt /tmp/existing.txt
```

Every name left over is a candidate. Discard the false positives (a common word, the name of an external tool, a command with `/`) and check the rest against `.claude/commands/`. Whatever is left after that is a real broken redirection, and the fix is to point to the real skill or remove the line.

> Real case: `vertical-slides` arrived from outside citing **9 nonexistent skills** (`create-presentation`, `frontend-animations`, `deploy-landing`, `script-presentation`, `youtube-script`, `short-viral-content`, `vsl-webinar`, `copywriting`, `site-architecture`). All of them were removed in the adaptation, before installing.

## Step 4: Overlap

Two skills that cover the same domain make the model choose wrong, or not choose at all.

For each suspicious pair, the 3-question test:

1. **Is the input the same?** If both receive the same thing, it is real overlap.
2. **Is the output the same?** If they deliver the same artifact, one of the two is redundant.
3. **Would a user know which to pick by reading only the two `description` fields?** If not, the problem is the declared boundary, not the existence.

**Decision:** input and output overlap → merge or retire one. Poorly declared boundary → fix the `description` of both, each one citing the other explicitly ("for X, use Y").

## Step 5: Frontmatter quality

```bash
# description missing or too short to trigger
for f in .claude/skills/*/SKILL.md; do \
  d=$(grep -m1 '^description:' "$f" | wc -c); \
  [ "$d" -lt 120 ] && echo "SHORT DESCRIPTION ($d): $f"; done

# skills with no trigger phrase in the language the vault operates in (default English)
grep -LiE "use when|when the user|'[a-z ]{4,}'" .claude/skills/*/SKILL.md
```

A `description` with no trigger word does not fire. It is the most expensive defect, because the skill exists and is never used.

## Step 6: Coverage gap

Cross the domain map with what exists: acquisition, offer, copy, landing, content, video, CRM, research, vault/meta. A domain with no skill is a gap; a domain with three skills is a candidate for Step 4.

## Report

```markdown
## Skill Ecosystem Audit: <date>

**Surfaces:** [N] executables · [N] commands · [N] cards · [N] index rows

### Misalignment
| Skill | Executable | Card | Index | Action |
|---|---|---|---|---|

### Broken redirections
| Skill | Cites | Exists? | Fix |
|---|---|---|---|

### Overlaps
| Pair | Same input? | Same output? | Decision |
|---|---|---|---|

### Gaps
| Domain | Covered by | Note |
|---|---|---|

### Priority
1. [what breaks usage today]
2. [what confuses the choice]
3. [what is cosmetic]
```

## Rules

- **Do not fix anything during the audit.** The output is the report; the fix is a separate decision, one at a time.
- Card and executable diverging in content: the source of truth is always the executable, and the card is what gets adjusted.
- Do not propose a new skill to plug a gap without first checking whether a command already solves it.

## Provenance

Adapted from the AUDIT mode of a third-party skill (`skill-forge`), read on 2026-08-12. The original scans a single folder; here the object is the **three surfaces** of this vault, which is where misalignment actually happens. Steps 3 and 4 come from it (the redirection check and the 3-question test for overlap); the rest was rewritten for the local context. The whole skill was not installed because `skill-creator` already covers creating and reviewing, with an eval harness that `skill-forge` does not have.
