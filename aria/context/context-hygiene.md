# Context Hygiene

Before non-trivial work, read the relevant files in `aria/context/` and `aria/review/`.

Allowed project files are source, tests, docs, and intentional Aria workflow files. Canonical repository hygiene rules live in `aria/context/repository-hygiene.md`.

Local tool state belongs in `.git/info/exclude` and must not be committed.

Stop conditions:

- Required source-of-truth context is unavailable and cannot be recovered from the task handoff.
- Existing repository state is unsafe or conflicting.
- A requested implementation would cross Bloco 0 boundaries.
- Remote configuration conflicts with the intended repository.
