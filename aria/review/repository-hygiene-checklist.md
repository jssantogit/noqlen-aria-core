# Repository Hygiene Checklist

- Confirm `git add .` was not used.
- Confirm explicit staging only.
- Confirm context package and scope did not cause broad repository edits.
- Confirm `aria/context/delta.md` was updated when the task required it.
- Confirm no forbidden local/tooling files are tracked.
- Confirm `.git/info/exclude` may be used locally but is not committed.
- Confirm no secrets.
- Confirm no local logs.
- Confirm no credentials.
- Confirm no temporary files.
- Confirm no tool caches.
- Confirm no generated deployment artifacts.
- Confirm no `site/`.
- Confirm no personal paths.
- Confirm no private data.
- Confirm no real music-library paths.
- Confirm no lyrics.
- Confirm no fingerprints.
- Confirm no `docs/development/`.
- Confirm no audit-report files.
- Confirm path-contamination checks and content-contamination checks are considered separately.
- Run the tracked forbidden files grep.
- Review `git show --name-only --oneline --stat HEAD` after commit.

Commands:

```sh
git status --short --branch
git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets|^site/)' || true
git show --name-only --oneline --stat HEAD
```
