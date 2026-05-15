# Repository Hygiene Checklist

- Confirm `git add .` was not used.
- Confirm explicit staging only.
- Confirm no forbidden local/tooling files are tracked.
- Confirm `.git/info/exclude` may be used locally but is not committed.
- Confirm no secrets.
- Confirm no local logs.
- Confirm no credentials.
- Confirm no temporary files.
- Confirm no tool caches.
- Confirm no `docs/development/`.
- Confirm no audit-report files.
- Run the tracked forbidden files grep.
- Review `git show --name-only --oneline --stat HEAD` after commit.

Commands:

```sh
git status --short --branch
git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true
git show --name-only --oneline --stat HEAD
```
