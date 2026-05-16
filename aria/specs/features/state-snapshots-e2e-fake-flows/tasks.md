# Tasks

## Preparation checklist

- [x] Read required context package and requested docs.
- [x] Review Bloco 18 and Bloco 19 review outcomes.
- [x] Inspect existing source and test patterns.
- [x] Create and review spec before implementation.

## TDD classification

- Required for snapshot redaction.
- Required for snapshot diff behavior.
- Required for fake flow trace determinism.
- Required for fake flow degraded/failure behavior.
- Required for no provider/network/filesystem/playback behavior.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|---|---|---|
| Snapshot redaction/sanitization | High | Secret-like keys, raw personal paths, raw logs, unsupported objects |
| Snapshot validation | High | Invalid scopes/sections and safe issues |
| Snapshot diff | High | No-change and section-change structural comparisons |
| Fake flow deterministic traces | High | Stable step order and repeated identical results |
| Degraded fake flow behavior | High | Source unavailable/partial trace without unsafe side effects |
| Provider/network/filesystem/playback/Android boundaries | High | Tests and search validation |
| Model defaults and public exports | Medium | Defaults serialize and exports are intentional |
| Spec/context updates | Low | Review and delta checklist |

## Behavior Budget check

- [x] New behaviors limited to Bloco 20 snapshot and fake-flow foundations.
- [x] Public API expansion limited to intentional names.
- [x] No new dependencies.
- [x] Allowed files only.
- [x] Stop conditions not triggered during design.

## Implementation tasks

- [x] Implement snapshot contracts and redaction policy.
- [x] Implement snapshot service, validation, and structural diff service.
- [x] Implement fake flow contracts and runner.
- [x] Add deterministic scenarios for source/library/queue/now-playing/diagnostics.
- [x] Add deterministic scenario for profile/preferences/smart playlist/queue preview.
- [x] Add deterministic scenario for radio availability/playback intent preview.
- [x] Add deterministic scenario for offline/cache/quality/capability summary.
- [x] Add degraded source fake flow scenario.
- [x] Update public exports.
- [x] Add tests for required behaviors and boundaries.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/state-snapshots-e2e-fake-flows aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Required provider/network/filesystem/playback/Android/Bloco 21 boundary searches.

## Review checklist

- [x] Spec created and matches requested scope.
- [x] Implementation matches the approved spec.
- [x] No Bloco 21 behavior implemented.
- [x] No real provider integration exists.
- [x] No network behavior exists.
- [x] No filesystem persistence/traversal exists.
- [x] No real music library access exists.
- [x] No playback/stream resolution exists.
- [x] No Android/UI/background job code added.
- [x] Snapshots are sanitized.
- [x] Fake flows are deterministic and local-only.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 20 completion and active spec status.
- [x] Update `aria/context/delta.md` with concise implementation and validation evidence.
- [x] Confirm no Audit 18-20 start is recorded.
