# Allowed Tools

Allowed local tools:

- `python3` for local package and test validation.
- `pytest` when available.
- `git status`, `git diff`, `git log`, `git show`, `git ls-files`, and explicit `git add` allowlists.
- `gh` only for safe repository existence checks, creation, and non-force push operations when authenticated.
- `.git/info/exclude` for local-only exclusions.

Disallowed operations:

- `git add .`.
- Force push.
- Destructive reset, clean, or checkout commands unless explicitly approved.
- Reading or committing secrets.
- Networked product tests.
- Real Navidrome, Anchor, or music-library access in Bloco 0.
