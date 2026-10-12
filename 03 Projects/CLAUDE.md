# Projects: rules for this folder

One subfolder per active project. Each project has a `README.md` as its entry point.

## Structure of a project

```
03 Projects/
└── Project Name/
    ├── README.md          ← status, next steps, links
    ├── research/          ← research, references, analyses
    ├── drafts/            ← drafts of content or documents
    └── notes/             ← working notes, scratchpad
```

## When to create subfolders
- Only create one if there is already content to put in it: do not create empty folders
- `research/` → when a piece of research or analysis has been done
- `drafts/` → when there is a real draft
- `notes/` → for loose working notes

## Default README.md
```markdown
---
type: project
status: active
date: YYYY-MM-DD
tags: [project]
---

## Overview
{{what this project is and why it exists}}

## Current status
{{where it stands now}}

## Next steps
- [ ] {{action 1}}
- [ ] {{action 2}}
```

## Rules
- When the user mentions a project: route to `03 Projects/{name}/README.md`
- Finished projects: move them to `04 Resources/archive/` or delete them
- Use wikilinks to connect projects to daily notes and context

---

Navigation: go back to the hub at [[Home]].
