# Review

## Summary

Bloco 6 — Aria MVP Hardening spec is created as planning only. It defines the future hardening scope for public API review, intentional exports, safe serialization, sanitized errors/warnings, optional dependency behavior, Anchor dry-run/apply safety, forbidden integration checks, documentation consistency, test coverage review, repository hygiene, and Bloco 4-6 formal audit readiness.

No hardening implementation is created by this task.

## Requirements coverage

| Requirement area | Status |
|------------------|--------|
| Public API surface review | Covered by FR-10 and design public API section |
| Intentional exports | Covered by FR-20 and future Task A |
| Safe serialization review | Covered by FR-30 and future Task B |
| Sanitized errors/warnings | Covered by FR-40 and future Task B |
| Optional dependency behavior | Covered by FR-50 and future Task C |
| Anchor dry-run/apply safety verification | Covered by FR-60 and future Task D |
| No provider internals | Covered by FR-70 and non-goals |
| No CLI-as-integration | Covered by FR-60/FR-70 and non-goals |
| No real Navidrome execution | Covered by FR-60/FR-70 and non-goals |
| No real music library access | Covered by FR-70 and non-goals |
| No Android SDK dependency | Covered by FR-70 and non-goals |
| No UI implementation | Covered by FR-70 and non-goals |
| No playback/queue/cache implementation | Covered by FR-70 and non-goals |
| Documentation consistency | Covered by FR-80 and future Task E |
| Test coverage review | Covered by FR-90 and Test Risk Matrix |
| Repository hygiene | Covered by FR-100 and validation plan |
| Bloco 4-6 formal audit readiness | Covered by FR-100 and future Task E |

Canonical Examples CE-01 through CE-08 are included and use Given / When / Then.

## Context package used

Standard. Per `aria/context/context-packages.md`.

## Files changed

Created:

- `aria/specs/features/aria-mvp-hardening/requirements.md`
- `aria/specs/features/aria-mvp-hardening/design.md`
- `aria/specs/features/aria-mvp-hardening/tasks.md`
- `aria/specs/features/aria-mvp-hardening/review.md`

Expected concise context updates:

- `aria/context/current.md`
- `aria/context/delta.md`

No source or test files are expected to change.

## Validation performed

To be completed after file creation in this task:

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find aria/specs/features/aria-mvp-hardening aria/context -maxdepth 5 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check

## Validation notes

All requested validation commands passed. `python3 -m pytest` reported 358 passed. The contamination check returned no tracked forbidden files. Final command results are reported in the task response and recorded concisely in `aria/context/delta.md`.

## Non-goals check

| Non-goal | Status |
|----------|--------|
| No hardening implementation in this task | Pass by scope |
| No source changes | Pass |
| No tests changed | Pass |
| No `pyproject.toml` changes | Pass |
| No Android SDK/Kotlin/Java/Gradle | Pass |
| No UI/screen/navigation/player code | Pass |
| No playback engine/Media3/ExoPlayer/MediaSession/Android Auto | Pass |
| No queue/now playing/offline/cache/download implementation | Pass |
| No provider internals, Anchor CLI integration, direct Navidrome, real music-library access | Pass |
| No dependencies added | Pass |

## Behavior Budget result

Budget for this spec task:

| Constraint | Result |
|------------|--------|
| New behaviors proposed only | Pass |
| Public API changes proposed only | Pass |
| Files allowed: spec directory plus concise context updates | Pass |
| Tests required: none, validation only | Pass |
| Dependencies: none | Pass |
| Stop if implementation code becomes necessary | Not triggered |

## Risk/test coverage result

Per `aria/context/test-risk-matrix.md`:

| Area | Risk | Current result |
|------|------|----------------|
| Safe serialization | High | Spec requires future negative tests |
| Sanitized errors/warnings | High | Spec requires future negative tests |
| Dry-run/apply boundary | High | Spec requires future apply-block tests |
| Optional dependency behavior | High | Spec requires future unavailable-dependency tests |
| Public exports | Medium | Spec requires future intentional export tests |
| Documentation consistency | Low | Spec requires review/checklist validation |
| Repository hygiene | Low | Spec requires contamination command |

No tests are created in this spec task.

## Delta updated?

Yes. `aria/context/current.md` and `aria/context/delta.md` were updated concisely.

## Fake-hostility checks applied?

Not applicable to this spec task. No fake implementation is created.

Future hardening tests should preserve fake-first behavior and avoid happy-path-only coverage, especially for optional dependency absence and unsafe serialization inputs.

## Risks remaining

- Public export decisions may require source changes in the future implementation.
- Sanitization gaps may require a larger follow-up task if behavior changes are not minimal.
- Optional dependency behavior can be environment-sensitive and must be simulated deterministically.
- Documentation consistency fixes must not imply implementation of future UI/player/provider features.

## Known limitations

- This spec does not decide the exact future export set.
- This spec does not choose a serialization helper implementation.
- This spec does not implement or test any hardening behavior.
- This spec does not perform the Bloco 4-6 formal audit; it prepares readiness criteria for it.

## Follow-up tasks

- Implement Bloco 6 hardening from this spec after approval.
- Add focused tests for high-risk hardening areas.
- Update docs only where needed to clarify MVP/future scope.
- Record validation evidence in `aria/context/delta.md` during implementation.
- Run Bloco 4-6 formal audit after hardening is complete.

## Aria context updates needed

- `aria/context/current.md`: mark Bloco 6 spec complete and next step as Bloco 6 implementation after approval.
- `aria/context/delta.md`: record spec creation and validation evidence concisely.
