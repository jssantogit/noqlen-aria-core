# Repository Hygiene

This file is the canonical repository hygiene policy.

- Never use `git add .`.
- Use explicit `git add` by allowlist only.
- Never commit `.opencode/`.
- Never commit `.skills/`.
- Never commit `opencode.json`.
- Never commit `docs/development/`.
- Never commit `docs/audit-report-*.txt`.
- Never commit `model-routing*`.
- Never commit local logs.
- Never commit `.env`.
- Never commit `credentials.json`.
- Never commit `.secrets`.
- Never commit local config files.
- Never commit caches.
- Never commit temporary files.
- Never commit local tool artifacts.
- Use `.git/info/exclude` for local-only exclusions.
- Do not commit `.git/info/exclude`.
- Before commit, check tracked forbidden files.
- After commit, review `git show --name-only --oneline --stat HEAD`.
- Do not force push unless explicitly instructed by the user.
- Do not overwrite or destructively clean local repositories.
- Do not recreate existing remote repositories.

Canonical commands:

```sh
git status --short --branch
git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true
git show --name-only --oneline --stat HEAD
```
