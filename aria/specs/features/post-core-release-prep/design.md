# Design

## Summary

Bloco 24 creates release-preparation documentation for the post-core foundation phase. It does not change product behavior. The artifacts make implemented Aria Core foundation work auditable and make future Android/player/app boundaries explicit before the final Post-core/Core Audit.

## Context package

Standard. The task also required selected roadmap, boundary, handoff, template, review, source export, and test file context to verify documentation claims.

## Context files read

- `AGENTS.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/future-product-context.md`
- `aria/context/android-player-reference.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/android-boundary.md`
- `docs/android-real-integration-plan.md`
- `docs/android-shell-handoff.md`
- `docs/ui-shell-boundary.md`
- `docs/handoff.md`
- `README.md`
- `pyproject.toml`
- `aria/specs/_template/**`
- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/*.py` file list
- `tests/*.py` file list
- `aria/review/validation-checklist.md`
- `aria/review/repository-hygiene-checklist.md`
- `aria/review/block-audit-checklist.md`

## Existing project context

- Aria Core MVP is Blocos 0-7 and local tag `v0.1.0` exists.
- Blocos 8-17 are implemented and audited.
- Blocos 18-21 are implemented; Audit 18-20 is deferred to final post-core/core audit.
- Blocos 22-23 are planning/handoff docs only; Audit 21-23 is deferred to final post-core/core audit.
- Bloco 24 prepares release documentation only.

## Files to create

- `aria/specs/features/post-core-release-prep/requirements.md`
- `aria/specs/features/post-core-release-prep/design.md`
- `aria/specs/features/post-core-release-prep/tasks.md`
- `aria/specs/features/post-core-release-prep/review.md`
- `docs/post-core-release-checklist.md`
- `docs/post-core-release-notes.md`
- `docs/post-core-api-surface.md`
- `docs/post-core-safety-summary.md`
- `docs/post-core-handoff.md`
- `docs/post-core-known-limitations.md`
- `docs/future-android-player-handoff.md`

## Files to modify

- `README.md`
- `docs/handoff.md`
- `docs/post-core-backlog.md`
- `docs/aria-core-handoff.md`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- `src/noqlen_aria/**`
- `tests/**`
- `pyproject.toml`
- Android/Kotlin/Java/Gradle files
- UI/screen/navigation/player code
- MediaSession, Media3/ExoPlayer, Android Auto, playback engine, audio driver, USB output, JNI/NDK/AAudio/Oboe implementation files
- Provider auth, direct provider integration, network behavior, filesystem/device behavior

## Release readiness flow

1. Create release-prep docs.
2. Run validation and repository hygiene checks.
3. Record evidence in spec review and context delta.
4. Commit release-prep docs.
5. Stop. Final Post-core/Core Audit is the next gate.
6. Only after final audit passes may a maintainer decide whether to tag or publish.

## Documentation update plan

- Keep MVP release docs historical.
- Add post-core-specific docs using `post-core-*` names.
- Update README with current post-core status and artifact pointers.
- Update backlog and handoff wording from “not started” to “prepared, final audit pending.”

## Public API summary plan

- Use `src/noqlen_aria/__init__.py` top-level exports as the implemented API source of truth.
- Group names by existing domain modules.
- Avoid listing future-only Android, player, provider, driver, or UI APIs as current API.
- Mention Android boundary/planning docs as documentation, not executable Android APIs.

## Safety summary plan

- Restate provider, network, filesystem, Android, playback, audio-driver, stream, transcoding, cache/restore, and secret/log boundaries.
- Call out that current Anchor remains Navidrome-focused and is not multi-provider.
- Call out that Aria models bit-perfect/custom audio readiness/capability only and does not implement a driver.

## Final audit input plan

- The release checklist includes validation commands, doc status, API/safety status, hygiene status, blockers, and tag/publish criteria.
- The final audit should compare release docs against implementation, exports, tests, and repository hygiene.
- Any validation failure, false implementation claim, private/local tracked file, uncommitted change, source/test modification, or forbidden implementation blocks tag readiness.

## Handoff plan

- `docs/post-core-handoff.md` hands off to final audit, future Android Player phases, and future app/UI work.
- `docs/handoff.md` records repository status for future local work.

## Future Android Player handoff plan

- Document Phase A audio output research, Phase B playback engine adapter, Phase C exclusive USB output prototype, Phase D bit-perfect validation, and Phase E production audio driver/bridge decision as future work outside Aria Core.
- Emphasize Aria Core provides contracts, states, policies, services, capabilities, fakes, and sanitized outputs only.

## Version/tag decision boundary

- Bloco 24 does not create a tag.
- Bloco 24 does not publish packages.
- Final audit decides whether a post-core release tag is ready.
- Tag readiness is blocked by validation failures, dirty working tree, private/local tracked files, source/test changes in this block, false implementation claims, or unresolved final-audit findings.

## Repository hygiene considerations

- Use explicit allowlist staging only.
- Do not use `git add .`.
- Confirm no `.opencode/`, `.skills/`, `opencode.json`, local development docs, audit report files, model routing files, `.env`, credentials, secrets, or deployment artifacts are tracked.
- Keep current and delta context concise.

## Risks

- Docs may overstate future Android/player/provider work as implemented.
- Public API docs may drift from `__all__`.
- Release checklist may be mistaken for final audit approval.
- Validation-command text may produce expected search matches that require explanation.

## Rollback strategy

Revert this documentation-only commit if release-prep artifacts need replacement. No source, test, dependency, version, tag, or publish state is changed by design.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find README.md docs aria/specs/features/post-core-release-prep aria/context aria/review -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
- Required false-claim and forbidden implementation searches from the task prompt.

## Behavior Budget

- New behaviors: documentation/release-prep only.
- Public API changes: none unless only documenting existing public API.
- Files allowed: `aria/specs/features/post-core-release-prep/**`, `docs/**`, `README.md`, `aria/context/current.md`, `aria/context/delta.md`, and `aria/review/**` only if release/final-audit checklist references need alignment.
- Tests required: no new tests required because this block is release documentation/prep only.
- Dependencies: none.
- Stop if: source code changes become necessary; new feature implementation becomes necessary; tag creation becomes necessary; package publishing becomes necessary; Future Android Player work becomes necessary.
