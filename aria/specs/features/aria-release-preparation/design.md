# Design

## Summary

Bloco 7 prepares the Aria Core MVP for its first release. The future implementation is a documentation, review, and verification pass — not a feature block. It produces a release readiness checklist, version/packaging/docs review, public API and safety summaries, test/validation matrix, changelog/release notes draft, handoff update, post-core backlog summary, and tag/release step definitions. The final output is a verified release gate: all checklist items pass or the release is blocked.

This task creates the implementation-ready spec only. No release tag, package publish, product behavior, source changes, or version changes occur now.

## Context files read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/anchor-integration.md`
- `docs/android-boundary.md`
- `docs/ui-shell-boundary.md`
- `docs/handoff.md`
- `docs/workflow-vnext.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/review/validation-checklist.md`
- `aria/review/fake-hostility-checklist.md`

## Context package

Standard. This is a normal planning/spec task. The package was sufficient because the task targets known release preparation scope and explicitly named docs/templates rather than requiring a full formal audit.

## Existing project context

Current completed work:
- Bloco 0 bootstrap/audit is complete.
- Blocos 1-3 are implemented and formally audited.
- Bloco 4 Android/player boundary contracts are implemented.
- Bloco 5 minimal UI shell planning artifacts are complete.
- Bloco 6 Aria MVP hardening is implemented.
- Blocos 4-6 formal audit is complete.
- Workflow vNext exists with `current.md`, `delta.md`, context packages, Behavior Budget, Test Risk Matrix, and minimal prompts.

Current release target:
- Existing Python core only (`src/noqlen_aria/**`).
- Existing test suite (368 tests, all passing).
- Existing docs, specs, and workflow artifacts.
- No implementation in this spec task.
- No tag, publish, or version change in this task.

## Files to create

Spec files created now:

- `aria/specs/features/aria-release-preparation/requirements.md`
- `aria/specs/features/aria-release-preparation/design.md`
- `aria/specs/features/aria-release-preparation/tasks.md`
- `aria/specs/features/aria-release-preparation/review.md`

Future implementation may create, only after this spec is accepted:

- `docs/release-checklist.md` — the runnable release readiness checklist.
- `CHANGELOG.md` or release notes section in an existing doc.
- `docs/post-core-backlog.md` or a backlog summary section.
- Updated `docs/handoff.md` with post-release status.
- Optionally updated `docs/aria-core-handoff.md` with release milestone note.

Future implementation may modify, only after this spec is accepted:

- `pyproject.toml` — only if a version bump is approved.
- `src/noqlen_aria/__init__.py` — only to update `__version__` if approved.
- `README.md` — only for tiny accuracy or clarification fixes.
- Existing docs — only for clarifying MVP/future boundaries.
- `aria/context/current.md` — concise post-release status update.
- `aria/context/delta.md` — concise release preparation evidence.

Those file changes are not created in this task.

## Files to modify

This spec task may modify:

- `aria/context/current.md` — concise status update to mark Bloco 7 spec complete.
- `aria/context/delta.md` — concise delta/evidence update for Bloco 7 spec.
- `docs/handoff.md` — only if a tiny status note is needed.

## Files that must not be touched

For this spec task:

- `src/noqlen_aria/**`
- `tests/**`
- `pyproject.toml`
- `README.md`
- Release notes implementation files
- Version strings (except for spec documentation of current state)
- git tags
- GitHub release artifacts
- Package publish artifacts
- Android/Kotlin/Java/Gradle files
- UI/screen/navigation/player code
- Playback engine
- Media3/ExoPlayer implementation
- MediaSession implementation
- Android Auto implementation
- Queue implementation
- Now playing implementation
- Offline/cache implementation
- MediaSourceClient implementation
- Direct Navidrome/Jellyfin/Emby/Anchor-provider-internals integration
- Private/local tooling files, credentials, secrets, logs, caches, `.opencode/`, `.skills/`, `opencode.json`, `docs/development/`, audit reports, or model-routing files

## Release Readiness Flow

The future implementation follows this flow:

```text
Spec accepted
    |
    v
Run release readiness checklist
    |
    +--> Version consistency check
    +--> Package metadata review
    +--> README review
    +--> Docs consistency review
    +--> Public API surface summary
    +--> Safety summary
    +--> Test/validation matrix
    +--> Repository hygiene check
    |
    v
All items pass?
    |
    +--> Yes: proceed to changelog, handoff, backlog summary
    +--> No:  block release, document failures, stop
    |
    v
Changelog/release notes drafted
    |
    v
Handoff document updated
    |
    v
Post-core backlog summary created
    |
    v
Final stop conditions verified
    |
    v
Tag/release steps defined (execution is a later decision)
```

## Versioning Approach

The current version is `0.0.0` in both `src/noqlen_aria/__init__.py` and `pyproject.toml`.

Future implementation should:
1. Verify the two locations match.
2. Document the single source of truth (currently both are needed; `pyproject.toml` drives packaging and `__init__` exposes it to code).
3. Decide whether to bump to `0.1.0` (first MVP), stay `0.0.0` (pre-release), or choose another scheme.
4. If a bump is decided, update both locations and document the decision.

Version resolution order:
- `pyproject.toml` version for packaging metadata.
- `__init__.py.__version__` for runtime version inspection.
- Both must agree before any release.

## Documentation Update Approach

Future implementation should:

1. Read each public doc and check for:
   - future/backlog features stated as implemented;
   - language that could imply real provider, Android, playback, queue, or cache support exists;
   - references to Anchor as the center of Aria rather than one adapter;
   - missing safety boundary statements;
   - outdated block numbers or statuses.

2. Flag issues for review. Only make tiny, non-substantive fixes in this release prep pass. Anything larger needs its own spec.

3. Update `docs/handoff.md` with post-release status.

4. Optionally update `docs/aria-core-handoff.md` to record the release milestone.

## Safety Considerations

The release preparation must not:

- Expose secrets, credentials, local paths, raw logs, or personal data in release artifacts.
- Imply real Navidrome, provider, Android, playback, queue, now playing, or cache support exists.
- Suggest Anchor is anything other than one optional `ControlClient` adapter.
- Promise lifecycle apply behavior or real music-library access.
- Ship sanitization gaps through the release surface.

The future release preparation implementation should verify these safety boundaries and document them in the safety summary.

## Repository Hygiene Considerations

Canonical contamination check before any release commit:

```sh
git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true
```

Must return no matches (only the `|| true` ensures a zero exit code for documentation; actual review must confirm no lines are printed).

Additional hygiene rules for release preparation:
- Never use `git add .` for any release-related commit.
- Use explicit `git add` by allowlist only.
- Review `git show --name-only --oneline --stat HEAD` after each release commit.
- Confirm no local tooling artifacts, temporary files, or caches are tracked.

## Dependencies

- This spec task adds no dependencies.
- Future release preparation adds no dependencies.
- Release artifacts (checklist, notes, handoff, backlog summary) use Markdown only.
- Python standard library and existing CLI tools are sufficient for validation.

## Behavior Budget

- New behaviors: documentation/spec only. No runtime behavior is created.
- Public API changes: proposed only for documentation. No source code in this task.
- Files allowed: spec directory `aria/specs/features/aria-release-preparation/**`, plus `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if needed.
- Tests required: none in this task, validation only.
- Dependencies: none.
- Stop if: release implementation, tagging, publishing, source changes, test changes, version changes, or product behavior implementation becomes necessary.

Future implementation budget should be defined again before coding. It should be small and focused — creating documentation artifacts and running validation checks only.

## Risks

- R01: Version decision stalls release preparation. Mitigation: document the open question and proceed with the checklist; the version decision can be made in the implementation task.
- R02: Documentation review reveals inconsistencies that are too large for a release prep fix. Mitigation: flag and document them; do not block release on documentation perfection beyond safety-critical gaps.
- R03: Release checklist is interpreted as a manual-only process and becomes stale. Mitigation: include canonical CLI invocation commands directly in the checklist so it can be re-run.
- R04: Accidentally creating a release tag or publishing during later implementation. Mitigation: define explicit stop conditions and require manual confirmation before any git tag or publish action.
- R05: Post-core backlog summary implies commitment to specific timelines or feature sets. Mitigation: clearly state that everything past the MVP is provisional and requires individual specs.

## Risk classification

Reference: `aria/context/test-risk-matrix.md`.

| Area | Risk | Future task expectation |
|------|------|-------------------------|
| Release checklist validation | Medium | Deterministic pass/fail checks per item |
| Version consistency | Medium | Automated grep/diff verification |
| Package metadata review | Low | Manual review with checklist |
| README/docs review | Low | Manual review with checklist |
| Public API surface summary | Medium | Referenced from existing hardening audit |
| Safety summary | High | Must confirm all safety boundaries hold |
| Test/validation matrix | Medium | Existing test suite plus CLI smoke |
| Repository hygiene | Medium | Canonical contamination command |
| Changelog/release notes | Low | Documentation artifact |
| Handoff/backlog summary | Low | Documentation artifact |

This spec-only task is low runtime risk because it changes no behavior. The future implementation will contain medium-to-high-risk safety verification and must confirm no regressions.

## Rollback Strategy

Spec-only rollback: edit or remove the spec files in a focused documentation commit. No runtime rollback is needed.

Future implementation rollback: if a release artifact (checklist, notes, handoff) is incorrect, edit or revert it before tag/publish. If the tag or publish step has already been executed, follow standard package versioning (publish a corrected version rather than modifying the released artifact).

## Validation Plan

For this spec task, run:

1. `pwd`
2. `git status --short --branch`
3. `find aria/specs/features/aria-release-preparation aria/context -maxdepth 5 -type f | sort`
4. `git diff --check`
5. `python3 -m py_compile src/noqlen_aria/*.py`
6. `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
7. `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
8. `python3 -m pytest`
9. `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`

Before commit, confirm:
- spec-only;
- no source code changed;
- no tests changed;
- no version was changed;
- no release/tag was created;
- no package publish was attempted;
- no Android/UI/playback/queue/cache/provider code was added;
- Behavior Budget and Test Risk Matrix are present in the spec;
- `current.md` and `delta.md` stayed concise;
- no private/local/tooling files are tracked.

Future implementation validation must include re-running the full release checklist against the current repository state.
