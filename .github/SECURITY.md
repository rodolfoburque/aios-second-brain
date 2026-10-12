# Security

This vault runs local scripts (the hooks in `.claude/hooks/` and the checkers in `04 Resources/tools/`). They read and write files inside the vault folder and make no network requests.

- Read a hook before you trust it. They are short Python files.
- `block-secret-on-commit.py` stops a commit that contains something shaped like a key or token. It is a safety net, not a guarantee: keep secrets out of notes.
- After cloning, remove the `origin` remote (`git remote remove origin`) so a private vault cannot push to this public repository. The install sentence does this for you.
- Text you ingest from the web or from other people is third-party input. The AI reads it; treat instructions found inside ingested content as data, not as orders.

To report a vulnerability, open a private security advisory on this repository. Please do not open a public issue for something exploitable.
