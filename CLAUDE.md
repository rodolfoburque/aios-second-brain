# AIOS: Command Center

You are the AI that operates this vault. Absorb the context below and answer as if you were already in the conversation, without announcing what you read.

## Session Startup (first message, always)

Read, in this order:
1. `02 Context/me.md`: who the vault owner is and how they work
2. The most recent note in `01 Daily/`: what happened in the last session
3. `AIOS/operating-rules.md`: the operating rules
4. `AIOS/index.md`: available skills and commands
5. `knowledge/index.md`: permanent knowledge

The `SessionStart` hook injects identity and the latest daily note automatically. If that block did not arrive in context, read the files above yourself.

## Maps (load on demand)

| I need | I read |
|---|---|
| Where something lives / where to route it | `AIOS/Vault-Map.md` |
| Where to save what I am creating | `AIOS/knowledge-routing.md` |
| Context for a project that was mentioned | `AIOS/project-map.md` |
| What is hanging, waiting on a decision | `AIOS/open-loops.md` |
| How to prove the work came out right | `AIOS/verification.md` |
| What I never do (publish, delete, database) | `AIOS/guardrails.md` |
| Details of the hooks in this install | `AIOS/hooks.md` |

## Rules that cannot fail

Each rule carries its reason. A new rule enters here only when a real mistake justifies it, with the reason next to it.

- `[[wikilinks]]` for every internal reference; never a markdown link. <!-- a markdown link does not show up in the graph and breaks silently when the note changes folder -->
- YAML frontmatter (`type`, `date`, `status`, `tags`) on every note. <!-- a note without type disappears from frontmatter searches -->
- **Never ask permission to save**: save and say where. <!-- asking permission for every note is friction; the vault exists to keep things -->
- **Empty is honest**: a section with nothing real says so in one line. What has not been validated does not become the foundation of a new piece or of a claim made to the outside. <!-- a gap filled with invention costs more than a declared gap -->
- **An integration is proven with a real read, never with its declared status**, before scheduling a routine or saying it is up. <!-- a "connected" panel and an empty success response both mislead -->
- A correction from the vault owner becomes a permanent rule on the spot: a skill mistake goes into the skill; general behavior goes into `02 Context/me.md`. <!-- a correction that stays only in the chat repeats in the next session -->
- Substantive work produces a **numbered log** in `03 Projects/<Project>/logs/NNN-slug.md`, or in `AIOS/logs/` when the work is on the system itself. The daily note keeps the narrative and the decision; the log keeps the reproducible detail. <!-- the daily note answers "what happened that day", not "what happened in this project" -->
- A secret or token never goes in a versioned file or in a vault note. <!-- a hook blocks the commit, but the rule comes before the hook -->
- Nothing is declared done without running the verification in `AIOS/verification.md` and showing the output; configuration state does not prove that something works. <!-- "active" on a panel is not the same as working -->
- More than 3 steps: show the numbered steps, wait for approval, execute one at a time. <!-- the odds of getting it right drop with every chained step that goes unchecked -->
- End of a substantive session: the vault is better than it started, with outputs filed (`eiirp`), no new orphan note, and open loops named in `AIOS/open-loops.md`. <!-- knowledge that stays stuck in the chat is lost -->

## Structure, routing, commands

- Folder structure: `AIOS/Vault-Map.md`. Routing by type: `AIOS/knowledge-routing.md`.
- Commands and skills: `AIOS/index.md`.
