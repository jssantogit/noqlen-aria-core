# Validation Checklist

Before commit, record evidence for relevant commands.

Use `aria/review/repository-hygiene-checklist.md` for repository contamination checks. Use `aria/review/block-audit-checklist.md` or `aria/review/bloco-0-audit-checklist.md` for audit-specific validation. Use `aria/context/test-risk-matrix.md` for proportional test expectations.

Bloco 0 baseline:

- `pwd`
- `git status --short --branch`
- `git remote -v`
- `find . -maxdepth 4 -type f | sort`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest` when available
- `git diff --check`
- Repository contamination check with `git ls-files` patterns

Review for:

- Active spec compliance.
- `aria/context/current.md` and `aria/context/delta.md` status.
- Context package used.
- Behavior Budget result.
- Test Risk Matrix coverage.
- Non-goals.
- Changed files.
- Validation evidence.
- No private/local artifacts.
- No `git add .` usage.
- No Anchor internals.
- No direct Navidrome.
- No Android UI/SDK.
- No playback/cache implementation in Bloco 0.
