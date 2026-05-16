# Design

## Summary

Bloco 6 hardens the current Aria Core MVP before release preparation. The future implementation is a safety/release-readiness pass over existing behavior, not a feature block. It reviews public exports, safe serialization, error/warning sanitization, optional dependency behavior, Anchor dry-run/apply safety, documentation consistency, test coverage, repository hygiene, and audit readiness.

This task creates the implementation-ready spec only. No source code, tests, dependencies, Android/UI/playback/provider integration, or hardening behavior is implemented now.

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
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/review/validation-checklist.md`

## Context package

Standard. This is a normal planning/spec task. The package was sufficient because the task targets known hardening scope and explicitly named docs/templates rather than requiring a full formal audit.

## Existing project context

Current completed work:
- Bloco 0 bootstrap/audit is complete.
- Blocos 1-3 are implemented and formally audited.
- Bloco 4 Android/player boundary contracts are implemented.
- Bloco 5 minimal UI shell planning artifacts are implemented.
- Workflow vNext exists with `current.md`, `delta.md`, context packages, Behavior Budget, Test Risk Matrix, and minimal prompts.

Current hardening target:
- Existing Python core only.
- Existing CLI smoke behavior only.
- Existing docs/spec/review workflow only.
- No implementation in this spec task.

## Files to create

Spec files created now:

- `aria/specs/features/aria-mvp-hardening/requirements.md`
- `aria/specs/features/aria-mvp-hardening/design.md`
- `aria/specs/features/aria-mvp-hardening/tasks.md`
- `aria/specs/features/aria-mvp-hardening/review.md`

Future implementation may modify, only after this spec is accepted:

- `src/noqlen_aria/__init__.py` for intentional top-level exports if needed.
- `src/noqlen_aria/contracts.py` for serialization/sanitization hardening if tests show a gap.
- `src/noqlen_aria/services.py` for sanitized result mapping hardening if tests show a gap.
- `src/noqlen_aria/anchor_adapter.py` for optional dependency or dry-run/apply safety hardening if tests show a gap.
- Existing docs for tiny consistency clarifications if needed.
- Existing tests or new focused tests for hardening coverage.

Those source/test/doc changes are not created in this task.

## Files to modify

This spec task may modify:

- `aria/context/current.md` — concise status update to mark Bloco 6 spec complete.
- `aria/context/delta.md` — concise delta/evidence update for Bloco 6 spec.
- `docs/handoff.md` — only if a tiny status note is needed.

## Files that must not be touched

For this spec task:

- `src/noqlen_aria/**`
- `tests/**`
- `pyproject.toml`
- Android/Kotlin/Java/Gradle files
- UI/screen/navigation/player files
- Playback/queue/now playing/cache/offline implementation files
- Direct provider, Navidrome, Jellyfin, Emby, or Anchor provider-internal integration files
- Private/local tooling files, credentials, secrets, logs, caches, `.opencode/`, `.skills/`, `opencode.json`, `docs/development/`, audit reports, or model-routing files

## Hardening Architecture

The future hardening implementation is a review-and-tighten pass across existing MVP seams:

```text
Caller / Future UI / CLI smoke
        |
        v
Intentional public Aria Core surface
        |
        +--> contracts/results/states/fakes/services
        +--> optional AnchorControlClient adapter
        +--> Android/player boundary contracts as abstract vocabulary
        |
        v
Safe serialized app-facing output
```

The hardening pass does not add product layers. It verifies existing layers remain safe:

```text
Allowed to harden later:
  public API names, serialization, sanitization, optional dependency handling,
  dry-run/apply guards, docs, tests, repository evidence

Forbidden in hardening:
  provider internals, Anchor CLI integration, direct Navidrome execution,
  real music-library access, Android SDK, UI implementation, playback engine,
  queues, now playing, offline/cache/download behavior
```

## Public API Surface Design

Future implementation should inventory exports by module:

| Module | Hardening question |
|--------|--------------------|
| `noqlen_aria` | Does top-level import expose only intentional MVP names? |
| `contracts` | Are contract/state/result primitives stable and source-agnostic? |
| `services` | Are service names intentional and free of backend details? |
| `anchor_adapter` | Is the adapter public only as a `ControlClient` implementation, without internals? |
| `android_boundaries` | Are bridge protocols/vocabulary intentionally exposed without Android SDK implementation? |
| `cli` | Is CLI smoke behavior kept separate from integration APIs? |

Proposed export rule: stable public names are documented intentionally; private helpers and imported support names are not part of the stable API. If `__all__` changes are needed, future implementation should make the smallest possible source changes and cover them with tests.

## Safe Serialization Design

Future implementation should review serialization paths for:
- dataclass states and nested dataclasses;
- enum values;
- `AriaResult` success/failure envelopes;
- `AriaError` and `AriaWarning` values;
- diagnostics/readiness/status state;
- Android boundary snapshots and fake outputs;
- optional dependency unavailable states.

Safe serialized output must contain only display-safe, stdlib-compatible values. It must not contain raw exception objects, stack traces, provider objects, credentials, local paths, raw logs, direct music-library contents, or backend-internal details.

## Error handling

Future hardening should preserve the current rule: callers receive `AriaResult` or safe state objects instead of raw exceptions.

Required behavior for future implementation:
- unsafe details are converted into stable safe messages;
- error codes remain internal/routing-oriented and never contain secrets;
- diagnostics warnings are display-safe;
- optional dependency absence is represented as safe degraded state or safe failure;
- lifecycle apply attempts return explicit safe non-availability rather than performing mutation.

## Optional Dependency Design

The Anchor adapter remains optional. Core imports, services, fakes, CLI help, and CLI doctor must work without optional Anchor packages installed.

Future implementation should verify:
- lazy import behavior;
- constructor dependency injection paths;
- degraded readiness/status behavior when Anchor is unavailable;
- no raw `ImportError` or backend exception reaches user-facing output;
- no new dependencies are introduced.

## Anchor Dry-Run/Apply Safety Design

Future implementation should verify the dry-run/apply boundary:

| Operation | MVP expectation |
|-----------|-----------------|
| Preview lifecycle intent | Allowed when represented by existing safe dry-run behavior |
| Apply lifecycle intent | Blocked or unavailable in MVP |
| Anchor provider internals | Forbidden |
| Anchor CLI as integration | Forbidden |
| Direct Navidrome execution/calls | Forbidden |
| Real music library access | Forbidden |

Any discovered gap should be fixed with the smallest source change and negative tests.

## Documentation Consistency Design

Future implementation should check docs for a consistent MVP boundary:
- future UI/player/provider/cache features are explicitly future/backlog;
- Android/player boundaries are vocabulary and fake-first contracts, not SDK implementation;
- Anchor is one `ControlClient` adapter, not the center of Aria;
- no doc implies real Navidrome, provider, Android, playback, queue, now playing, or cache support exists;
- docs align with current source and tests.

## Security considerations

- No secrets, credentials, local config, raw logs, or personal paths may appear in serialized output, docs examples, tests, or validation evidence.
- No real provider or library access is allowed.
- No subprocess execution is introduced for integration behavior.
- No Android SDK or UI framework dependency is introduced.
- No lifecycle apply mutation is enabled.
- Repository contamination checks remain mandatory before commit.

## Dependencies

- This spec task adds no dependencies.
- Future hardening adds no dependencies unless a future approved spec changes the budget.
- Python standard library should be sufficient for any future export/serialization/sanitization hardening.

## Behavior Budget

- New behaviors: proposed only, no implementation in this task.
- Public API changes: proposed only, no source code.
- Files allowed: `aria/specs/features/aria-mvp-hardening/**`, plus `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if needed.
- Tests required: none in this task, validation only.
- Dependencies: none.
- Stop if: implementation code becomes necessary; source/test changes become necessary; Android/UI/playback/queue/cache/provider integration becomes necessary; dependency changes become necessary.

Future implementation budget should be defined again before coding. It should be small, focused, and split if hardening reveals multiple unrelated gaps.

## Risks

- R01: Public API tightening may accidentally remove names that existing local callers use. Mitigation: make proposed export changes explicit and test stable names.
- R02: Sanitization tests may reveal behavior changes larger than a hardening pass. Mitigation: stop and split into a follow-up spec if needed.
- R03: Optional dependency behavior may differ by environment. Mitigation: use tests that simulate absence without installing real providers.
- R04: Documentation may describe future roadmap items in ways that look implemented. Mitigation: mark future/backlog explicitly.
- R05: Audit preparation may expand into implementation. Mitigation: enforce Behavior Budget and stop on scope creep.

## Risk classification

Reference: `aria/context/test-risk-matrix.md`.

| Area | Risk | Future test expectation |
|------|------|-------------------------|
| Safe serialization | High | Negative tests for unsafe raw details |
| Sanitized errors/warnings | High | Negative tests for paths, stack traces, credentials, provider details |
| Dry-run/apply boundary | High | Tests proving apply remains blocked/unavailable |
| Optional dependency behavior | High | Tests proving safe absence/degraded behavior |
| Public exports | Medium | Deterministic tests for intentional export set |
| Documentation consistency | Low | Review/checklist validation |
| Repository hygiene | Low | Existing contamination command |

This spec-only task is low runtime risk because it changes no behavior. The future implementation will contain high-risk safety checks and must use tests.

## Rollback strategy

Spec-only rollback: edit or remove the spec files in a focused documentation commit. No runtime rollback is needed.

Future implementation rollback: revert the smallest hardening change that caused a regression while preserving tests that describe the intended safety behavior, or split disputed behavior into a follow-up spec.

## Validation plan

For this spec task, run:

1. `pwd`
2. `git status --short --branch`
3. `find aria/specs/features/aria-mvp-hardening aria/context -maxdepth 5 -type f | sort`
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
- no hardening implementation was created;
- no Android/UI/playback/queue/cache code was added;
- Behavior Budget and Test Risk Matrix are present;
- `current.md` and `delta.md` stayed concise;
- no private/local/tooling files are tracked.

Future implementation validation must include targeted tests for each high-risk hardening area plus the repository baseline commands.
