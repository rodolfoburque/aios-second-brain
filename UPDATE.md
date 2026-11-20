# Updating an installed vault

An installed vault is detached from this repository on purpose: it holds private notes and must never push to a public template. That also means fixes do not arrive by `git pull`. To bring them in, open Claude Code inside the vault folder and paste:

```
Update my second brain with https://github.com/rodolfoburque/aios-second-brain/blob/main/UPDATE.md
```

> [!IMPORTANT]
> **If you are the AI that received the sentence above, read this carefully.**
>
> The user wants the fixes below applied to the vault in the CURRENT folder. Act, do not just describe. Answer in the language the user writes in. Tell the user up front that you will ask permission to run `git` and `python`.
>
> 1. **Check that you are inside an installed vault.** `CLAUDE.md`, `02 Context/me.md` and `.claude/hooks/session-start.py` must exist in the current folder. If they do not, stop and say so.
> 2. **Get the current template into a temporary folder OUTSIDE the vault:** `git clone --depth 1 https://github.com/rodolfoburque/aios-second-brain.git <temp folder>`. Never clone inside the vault.
> 3. **Never overwrite the user's content.** Do not copy the template's `CLAUDE.md`, `02 Context/`, `01 Daily/`, `AIOS/index.md`, `AIOS/project-map.md`, `AIOS/open-loops.md`, `.claude/settings.json` or any note over the user's. Only the files each fix names.
> 4. **Apply every fix below whose check says it is missing**, oldest first. Each one can be run twice without harm. Writing inside `.claude/` asks for one more permission than a normal edit: tell the user to accept it. If it is refused, say exactly which files are still missing and stop; do not report the fix as applied.
> 5. **Prove it:** run `python .claude/hooks/test-hooks.py` (`python3` on macOS and Linux). The last line must report every case passing. If it does not, stop and show the output.
> 6. **Clean up and report:** delete the temporary folder, add a line to today's daily note saying which fixes were applied, and tell the user to close Claude Code and open it again in this folder.

---

## 1.1.1: corrections reach every session

**What was wrong.** Corrections were saved at the end of `02 Context/me.md`, and the session-start hook loads only the first 4,000 characters of that file. Once `me.md` grew past that, saved corrections stopped reaching new sessions, with no warning.

**Check.** The fix is fully applied only if all three are true: `CLAUDE.md` has a line that is exactly `@AIOS/conduct.md`; the file `AIOS/conduct.md` exists; and `.claude/hooks/test-hooks.py` contains the text `corrections reach every session`. If all three are true, skip this fix. If only some are true, a previous run stopped halfway: do the steps that are still missing.

**Steps.**

1. Copy `AIOS/conduct.md` from the template into the vault, unless it already exists.
2. **Move the corrections.** Read the user's `02 Context/me.md`. Every line under "Permanent corrections" (the heading may be in the user's language, for example "Correções permanentes"), and any other line in the file that is a rule about how the AI should behave, becomes one line under `## Corrections` in `AIOS/conduct.md`: a single sentence that says what to do, with its date in parentheses, in the user's language. Do not drop any and do not invent any. Remove the "None yet" line once there is at least one. Then replace that section of `me.md` with:

   ```
   ## Corrections

   Corrections to the AI's behavior do not live in this file: each one is a line in [[conduct]], which is loaded whole into every session.
   ```

   Show the user the list of lines you moved.
3. **`CLAUDE.md`.** Right after the paragraph that starts with "The `SessionStart` hook injects identity", add these lines, with a blank line before and after each:

   ```
   Corrections from the vault owner, one line each, are loaded whole here:

   @AIOS/conduct.md
   ```

   Then, in the rules list, replace the end of the correction rule, `general behavior goes into `02 Context/me.md`.`, with: `general behavior becomes one line in `AIOS/conduct.md`, which is loaded whole into every session. Never in `02 Context/me.md`.` If the user rewrote these parts and the text is not found, add the import at the end of the Session Startup section and add the new rule to the list. Remove nothing else.
4. **`AIOS/operating-rules.md`, rule 5.** Replace `it goes into `02 Context/me.md`.` with: `it becomes one line in `AIOS/conduct.md`, which is loaded whole into every session (never in `02 Context/me.md`, of which a session only loads the beginning).`
5. **`AIOS/knowledge-routing.md`.** In the row "Rules for the AI's behavior", the destination becomes `AIOS/conduct.md` (one line per rule).
6. **`AIOS/Vault-Map.md`.** Under the line for `operating-rules.md`, add: ``- `conduct.md`: Corrections from the vault owner, one line each; loaded whole into every session``.
7. **Copy these from the template over the vault's copies** (they are machinery, not the user's content): `.claude/commands/assistant.md`, `.claude/commands/organize.md`, `.claude/commands/setup.md`, `.claude/skills/ingest/SKILL.md`, `.claude/hooks/test-hooks.py`, `AIOS/hooks.md`. If the user edited one of them, keep the user's edits and change only the sentence that sends corrections to `02 Context/me.md`.
8. Run the hook test. It now has one more case, "corrections reach every session", and it must pass.
