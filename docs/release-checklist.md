# Release Checklist

Aria Core MVP release readiness checklist. This checklist is the final gate before any tag or publish action.
All items must pass. Document any failures with the reason.

## Version Consistency

- [x] `__version__` in `src/noqlen_aria/__init__.py` matches `version` in `pyproject.toml`
  - Command: `grep -r '__version__\|version\s*=' src/noqlen_aria/__init__.py pyproject.toml`
  - Result: Both at `0.0.0`
- [x] No hardcoded version strings exist elsewhere in docs or code that conflict
  - Search: `grep -rn '0\.0\.0' src tests docs README.md pyproject.toml | grep -v __pycache__`
  - Result: Only in `__init__.py` and `pyproject.toml`

## Package Metadata

- [x] `pyproject.toml` fields are correct: name, description, Python requirement, dependencies, entry points, license, authors
- [x] Package description is consistent with MVP scope (no references to unimplemented features)
- [x] Build system and packaging configuration is valid
- [x] No optional dependency extras reference nonexistent packages

## README

- [x] `README.md` accurately describes current MVP behavior
- [x] README does not promise future/backlog features as implemented
- [x] README includes correct installation and usage instructions
- [x] README references or implies the license file

## Documentation Consistency

- [x] `docs/architecture.md` — consistent with MVP behavior; future layers marked as future/backlog
- [x] `docs/safety.md` — all listed safety boundaries hold in current MVP
- [x] `docs/anchor-integration.md` — Anchor described as one `ControlClient` adapter; dry-run only
- [x] `docs/android-boundary.md` — boundary contracts are vocabulary/fakes, not Android SDK
- [x] `docs/ui-shell-boundary.md` — marked as planning artifacts, not implementation
- [x] `docs/handoff.md` — reflects current Bloco status
- [x] `docs/aria-core-handoff.md` — roadmap and status updated
- [x] `docs/workflow-vnext.md` — current workflow status and policies accurate
- [x] No doc implies real Navidrome, provider, Android SDK, playback, queue, now playing, or cache support exists
- [x] Anchor consistently described as one `ControlClient` adapter, not the center of Aria

## Public API Surface

- [x] Public API surface summary exists at `docs/api-surface.md`
- [x] All public exports are source-agnostic (no provider internals, Anchor internals, Android SDK types, UI types, playback types)
- [x] Export decisions covered by existing hardening tests (`tests/test_mvp_hardening.py`)
- [x] Internal or unstable names in public modules are documented

## Safety

- [x] Safety summary exists at `docs/safety-summary.md`
- [x] Confirmed: no real music-library access
- [x] Confirmed: no direct Navidrome calls
- [x] Confirmed: no Anchor provider internals
- [x] Confirmed: no Android/UI/playback/queue/cache implementation
- [x] Confirmed: no provider hard coupling
- [x] Confirmed: no secrets or credentials in release artifacts
- [x] Confirmed: optional Anchor dependency behavior is safe and documented
- [x] Confirmed: lifecycle apply remains blocked/unavailable
- [x] Confirmed: serialized output is sanitized and safe for display

## Validation

- [x] `pwd` — correct working directory
- [x] `git status --short --branch` — working tree clean before commit
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — no compilation errors
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — CLI help works
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — doctor works, reports version `0.0.0`
- [x] `python3 -m pytest` — all tests pass
  - Run and record exact pass count.
- [x] `git diff --check` — no whitespace errors

## Repository Hygiene

- [x] Contamination check: `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
  - Must return no tracked forbidden files.
- [x] No private/local/tooling artifacts are staged or committed
- [x] `git add .` was NOT used for any release-related commit

## Search Checks

- [x] No Android SDK references: `grep -R "android\.\|androidx\.\|Media3\|ExoPlayer\|Activity\|Fragment\|Compose\|Kotlin\|Gradle" -n src tests docs || true`
  - Matches are documentation/planning references only; no implementation.
- [x] No forbidden implementations: `grep -R "QueueService\|NowPlaying\|OfflineCache\|MediaSourceClient" -n src tests || true`
  - Must return no matches in source or tests.
- [x] No apply-mode helpers: `grep -R "start_navidrome_apply\|stop_navidrome_apply\|restart_navidrome_apply\|render_navidrome_config_apply" -n src tests || true`
  - Must return no matches in source (negative-test assertions and generated cache notices only).
- [x] No provider/CLI integration: `grep -R "NavidromeProvider\|FakeServerProvider\|noqlen_anchor.cli\|subprocess.*noqlen-anchor" -n src tests || true`
  - Must return no matches in source or tests.

## Release Artifacts

- [x] Release checklist exists at `docs/release-checklist.md`
- [x] Release notes exist at `docs/release-notes.md`
- [x] Public API surface summary exists at `docs/api-surface.md`
- [x] Safety summary exists at `docs/safety-summary.md`
- [x] Post-core backlog summary exists at `docs/post-core-backlog.md`
- [x] Handoff document updated at `docs/handoff.md`
- [x] Changelog or release notes cover completed Blocos 0-6 scope
- [x] Release notes distinguish implemented features from future/backlog
- [x] Release notes include safety boundaries, known limitations, and version information

## Final Stop Conditions (block any tag/publish)

- [ ] ALL items above pass.
- [ ] No source, test, or package metadata changes uncommitted.
- [ ] No forbidden files tracked.
- [ ] No uncommitted changes in working tree.
- [ ] Tag/publish approved by the maintainer (not yet approved in this task).

## Tag/Release Reference (do not execute yet)

The following steps are defined for reference when tagging is later approved:

1. Decide version (currently `0.0.0`; options: `0.1.0` for first MVP, `1.0.0` for first stable).
2. If bumping, update `__version__` in `src/noqlen_aria/__init__.py` and `version` in `pyproject.toml`.
3. Commit version bump with message `chore: bump version to <version>`.
4. Create lightweight tag: `git tag -a v<version> -m "Aria Core MVP <version>"`.
5. Push tag: `git push origin v<version>`.
6. Build package: `python3 -m build`.
7. Publish to PyPI: `python3 -m twine upload dist/*` (when publishing is approved).
8. Create GitHub release from the tag, using `docs/release-notes.md` as the body.

Do NOT execute these steps in this task.
