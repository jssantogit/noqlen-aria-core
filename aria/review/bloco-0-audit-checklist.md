# Bloco 0 Audit Checklist

Verify:

- Repository exists.
- Branch is `main`.
- Remote is correct if configured.
- Initial commit exists.
- Push status is clear or documented.
- No secrets are committed.
- No local/tooling artifacts are committed.
- `AGENTS.md` is short.
- `aria/context/` exists and is coherent.
- `aria/specs/` templates exist.
- `aria/agents/` exists.
- `aria/prompts/` exists.
- `aria/review/` exists.
- Public docs are in English.
- Minimal CLI exists.
- CLI `--help` works.
- CLI `doctor` works safely.
- Local/smoke tests exist if practical.
- Tests do not require network.
- Tests do not require Anchor.
- Tests do not run Navidrome.
- Nothing from Bloco 1 was implemented.
- No `AriaResult`/`AriaError`/`AnchorClient`/`FakeAnchorClient` contracts were implemented.
- No Android UI/SDK was implemented.
- No playback/queue/cache/now-playing implementation exists.
- Future product context is documented as planning only.
- Future app/player-facing features are documented as planning only and require specs before implementation.
- Bloco 1 boundaries prohibit playback, UI, Android SDK, cache/offline, queue, now playing, MediaSession, Android Auto, and storage/permission UX implementation.
- Android player references are documented as inspiration only.
- Future architecture vocabulary is documentation only, not code.

Validation commands:

```sh
pwd
git status --short --branch
git remote -v
git log --oneline -5
find . -maxdepth 4 -type f | sort
git diff --check
python3 -m py_compile src/noqlen_aria/*.py
PYTHONPATH=src python3 -m noqlen_aria.cli --help
PYTHONPATH=src python3 -m noqlen_aria.cli doctor
python3 -m pytest
git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true
git show --name-only --oneline --stat HEAD
```

Final report format:

1. Model used.
2. Source of truth/context files read.
3. Commit audited.
4. Repository status.
5. Remote/push status.
6. Validation executed.
7. Repository contamination result.
8. Problems found.
9. Fixes made.
10. Remaining risks.
11. Ready for next block? yes/no.
