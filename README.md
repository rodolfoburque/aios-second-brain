# AIOS Second Brain

A second brain that an AI can operate: an Obsidian vault with rules, memory, skills and checks already wired for Claude Code, so every session starts knowing who you are, what happened last time and where things go.

Free and open source. [Português](.github/README.pt-br.md)

> Independent project. Not affiliated with or endorsed by Obsidian or Anthropic.

---

## Start in one minute

You do not need to know git or the terminal.

1. Install [Claude Code](https://claude.com/code) (Pro or Max plan), [Obsidian](https://obsidian.md/download), [Git](https://git-scm.com) and [Python 3](https://www.python.org/downloads/).
2. Create an empty folder for your second brain, for example `second-brain` inside your Documents folder. **Not in Downloads or Desktop, and no spaces in the folder name.**
3. Open Claude Code **inside that folder**.
4. Paste this sentence:

```
Build my second brain with this repository: https://github.com/rodolfoburque/aios-second-brain
```

5. Accept the permission prompts. Do not type any `/` command. Claude runs the setup and asks you a few questions about yourself.

The sentence needs the link. "Build my second brain" alone is not enough.

---

> [!IMPORTANT]
> **If you are the AI that received the link above, read this carefully.**
>
> **Trigger:** the user said they want to build, create or set up a second brain and sent the link to this repository. They want you to run the full setup below. Do not ask what they want, do not just list files. Act.
>
> Do NOT use slash commands (`/setup` and others). The user may have plugins whose commands collide with these names. Do everything yourself by reading files and running commands, in this order. Tell the user up front that you will ask permission to run `git` and `python`, and that they only need to accept.
>
> **The vault goes in the CURRENT folder**, the one where the user opened Claude.
>
> 1. **Check that the current folder is safe BEFORE cloning.** Print the working directory.
>    - If the path contains `Downloads` or `Desktop`: **stop, do not clone.** Say: "Downloads and Desktop are synced or protected on most systems. Close Claude, create a folder such as `second-brain` in Documents (no spaces in the name), open Claude inside it and paste the sentence again."
>    - If the folder name itself has a space: **stop.** Ask for a folder without spaces, same instruction.
>    - If the folder already has files that are not yours to overwrite: **stop** and ask the user to open Claude in an empty folder.
> 2. **Clone into the current folder:** `git clone https://github.com/rodolfoburque/aios-second-brain.git .`
>    - **If you already cloned into a subfolder to read this file** (for example `aios-second-brain/`): move everything out of it into the current folder, hidden entries included (`.git`, `.claude`, `.github`, `.gitignore`), then delete the empty subfolder. The vault must not stay nested: the user opened Claude in the folder where it belongs.
> 3. **Detach the vault from this repository:** `git remote remove origin`. The vault will hold private notes and must never be able to push to the public template. Say you did this.
> 4. **Detect the operating system from your own environment, without asking.** Do not assume macOS.
>    - **macOS, Linux or WSL:** change nothing. `.claude/settings.json` calls `python3`.
>    - **Native Windows:** copy `.claude/settings-windows.json` over `.claude/settings.json`. It calls `python` instead of `python3`. Then run `python --version`; if only `python3` answers, keep the original `settings.json`.
>    - State which system you detected and which settings file is in effect.
> 5. **Prove the hooks run:** `python .claude/hooks/test-hooks.py` (`python3` on macOS and Linux). The last line must report every case passing. If it does not, stop and show the output: nothing after this step is reliable without working hooks.
> 6. **Run the onboarding by READING the file, not by slash command.** Read `.claude/commands/setup.md` and run that interview in the conversation: ask the questions one at a time and fill `02 Context/me.md` with the real answers. Never invent an answer; an unanswered field stays "not defined yet".
> 7. **Prove it worked:** read the `me.md` you just wrote and tell the user who they are in three lines.
> 8. **Say what comes next:** close Claude Code and open it again in this same folder so the hooks load, then say "hi". Open the same folder in Obsidian with "Open folder as vault". From now on both run from here.

---

## What you get

```
aios-second-brain/
├── CLAUDE.md                 the rules the AI follows, each with its reason
├── .claude/
│   ├── commands/             5 commands: setup, assistant, organize, import-context, audit-skills
│   ├── skills/               10 skills for capturing, distilling and maintaining knowledge
│   ├── agents/               5 agents with a defined job
│   └── hooks/                session memory, secret blocking, and a self-test
├── AIOS/                     maps the AI reads on demand: routing, verification, guardrails
├── 00 Inbox/                 capture
├── 01 Daily/                 one note per day, written by the session hooks
├── 02 Context/               who you are: the file read at the start of every session
├── 03 Intelligence/          decisions, research, meetings
├── 03 Projects/              one folder per project, with numbered logs
├── 04 Resources/             reusable material and the checker scripts
├── 05 Archives/              what is done
├── knowledge/                permanent knowledge, promoted from dated notes
└── prompts/                  your own copy-paste prompts
```

What it does once installed:

- **Remembers.** A hook injects your identity and the last session into every new conversation, and writes the daily note when a session ends.
- **Files things where they belong.** "Process this into the vault" with a link, file or text: it reads, distills and stores the note in the right folder, linked to what already exists.
- **Checks its own work.** Scripts verify links, frontmatter, orphan notes and the skills themselves. Nothing is called done without running them.
- **Refuses the dangerous defaults.** A hook blocks commits that contain a secret.

Full list in `AIOS/index.md` after you install.

## Manual install

```bash
git clone https://github.com/rodolfoburque/aios-second-brain.git second-brain
cd second-brain
git remote remove origin
```

On native Windows, replace the hooks file:

```
copy .claude\settings-windows.json .claude\settings.json
```

Then check the hooks, open Claude Code in the folder and run the setup:

```bash
python3 .claude/hooks/test-hooks.py     # python on Windows
claude
> /setup
```

Open the same folder in Obsidian with "Open folder as vault".

## Requirements

| Tool | Why |
|---|---|
| Claude Code | operates the vault |
| Obsidian | reads and navigates the notes; the vault is plain Markdown and works without it |
| Git | history of everything the AI changes |
| Python 3 | the hooks and the checker scripts. Without it the vault still works, without automatic memory |

Proven on Windows 11. macOS and Linux use the default settings file; if something fails there, open an issue with the output of `test-hooks.py`.

## See your vault move

[vaultbubbles.org](https://vaultbubbles.org) reads a folder of notes in your browser and shows what you have been working on as bubbles. Nothing leaves your machine.

## What's next

- **AIOS Tools and AIOS Skills:** packs that run on top of this vault, for content, video, pages, prospecting and offers. [vaultbubbles.org/aios-tools](https://vaultbubbles.org/aios-tools)
- **Want it installed in your company's operation?** [bvrx.studio/ai-operations](https://bvrx.studio/ai-operations)

## License

MIT. See [LICENSE](LICENSE).
