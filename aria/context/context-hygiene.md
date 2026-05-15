# Context Hygiene

Before non-trivial work, read the relevant files in `aria/context/` and `aria/review/`.

Allowed project files are source, tests, docs, and intentional Aria workflow files. Local tool state belongs in `.git/info/exclude` and must not be committed.

Forbidden files include secrets, credentials, logs, temporary scratch files, generated caches, local prompts outside `aria/prompts/`, `.opencode/`, `.skills/`, `opencode.json`, `docs/development/`, audit reports, and model-routing files.

Stop conditions:

- Required source-of-truth context is unavailable and cannot be recovered from the task handoff.
- Existing repository state is unsafe or conflicting.
- A requested implementation would cross Bloco 0 boundaries.
- Remote configuration conflicts with the intended repository.
