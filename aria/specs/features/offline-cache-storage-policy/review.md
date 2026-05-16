# Review

## Summary

Bloco 14 (Offline, Cache and Storage Policy) spec and implementation are complete. Implementation delivers offline availability, cache policy and storage pressure foundations as policy/state/intent-preview models with three deterministic local services in `src/noqlen_aria/offline_cache.py`. Zero external dependencies added. 104 new tests pass alongside 642 existing tests (746 total).

No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage APIs, provider mutation, stream resolution, playback engine, or Bloco 15 behavior was added. All contracts are vocabulary-level, UI-independent, and provider-agnostic.

## Requirements coverage

All functional requirements (FR-01 through FR-12) are implemented.

| FR | Requirement | Status |
|----|-------------|--------|
| FR-01 | Offline availability evaluation | Implemented |
| FR-02 | Cache policy state and mode | Implemented |
| FR-03 | Cache operation intent and preview | Implemented |
| FR-04 | Pending cache operation tracking | Implemented |
| FR-05 | Storage pressure modeling | Implemented |
| FR-06 | Storage pressure from explicit inputs | Implemented |
| FR-07 | Cache cleanup preview without deletion | Implemented |
| FR-08 | Confirmation-required state | Implemented |
| FR-09 | Invalid budget/size validation | Implemented |
| FR-10 | Deterministic local policy services | Implemented |
| FR-11 | Safe confirmation modeling | Implemented |
| FR-12 | OfflineCachePolicyService | Implemented |

All non-functional requirements (NFR01-NFR08) are addressed:

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | Python stdlib only | `dataclasses`, `enum`, `typing` |
| NFR02 | No provider integration | No such references |
| NFR03 | No Android platform code | No such references |
| NFR04 | No filesystem or network access | Verified in boundary tests |
| NFR05 | No real cache mutation | No file ops |
| NFR06 | Deterministic behavior | Verified in tests |
| NFR07 | AriaResult consistency | All methods return AriaResult |
| NFR08 | Public names intentional | All types in __all__ |

8 Canonical Examples tested: CE-01 through CE-08 all pass.
12 Edge Cases covered in tests.

## Context package used

Standard.

## Files changed

Source created:
- `src/noqlen_aria/offline_cache.py` — all offline/cache/storage policy models and services.

Tests created:
- `tests/test_offline_cache_storage_policy.py` — 104 tests.

Source modified:
- `src/noqlen_aria/__init__.py` — added Bloco 14 public exports.
- `tests/test_mvp_hardening.py` — updated expected exports set.

Spec created:
- `aria/specs/features/offline-cache-storage-policy/requirements.md`
- `aria/specs/features/offline-cache-storage-policy/design.md`
- `aria/specs/features/offline-cache-storage-policy/tasks.md`
- `aria/specs/features/offline-cache-storage-policy/review.md`

Context updated:
- `aria/context/current.md`
- `aria/context/delta.md`

Files not touched:
- All other existing source, tests, and docs.

## Validation performed

- `pwd` — confirmed working directory.
- `git status --short --branch` — only expected changes.
- `git diff --check` — no whitespace issues.
- `find src/noqlen_aria tests aria/specs/features/offline-cache-storage-policy aria/context -maxdepth 6 -type f | sort` — all files present.
- `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- `python3 -m pytest` — 746/746 passed (642 existing + 104 new).
- Search check — provider integration: CLEAN.
- Search check — network library usage: CLEAN.
- Search check — filesystem access: CLEAN (only test self-checks match).
- Search check — Android references: CLEAN (existing LibraryActivity vocabulary only).
- Search check — forbidden future: CLEAN.
- Repository contamination check — CLEAN.

## Validation notes

All validation commands passed without regression. The implementation adds `src/noqlen_aria/offline_cache.py` (models + services) and `tests/test_offline_cache_storage_policy.py` (104 tests). `src/noqlen_aria/__init__.py` was modified to add exports. `tests/test_mvp_hardening.py` was updated for the expected exports set. No other source or test files were modified.

## Non-goals check

| Non-goal | Status |
|---|---|
| No real downloads | Pass |
| No real cache writes/deletes | Pass |
| No destructive cleanup | Pass |
| No filesystem traversal | Pass |
| No Android storage APIs | Pass |
| No SAF/MediaStore | Pass |
| No provider mutation | Pass |
| No stream resolution | Pass |
| No playback engine | Pass |
| No UI | Pass |
| No Bloco 15 behavior | Pass |
| No network behavior | Pass |
| No Anchor/Navidrome/Jellyfin/Emby | Pass |
| No smart playlist | Pass |

## Behavior Budget result

All budget constraints respected:

| Constraint | Status |
|---|---|
| New behaviors: offline/cache/storage policy models, cache operation intents, storage pressure, cleanup preview, 3 services | Pass |
| Public API changes: `offline_cache.py` with 22 public exports, `__init__.py` updated | Pass |
| Files allowed: source, tests, spec, context | Pass |
| Tests required: 104 tests written covering all high-risk areas | Pass |
| Dependencies: none beyond noqlen_aria.contracts | Pass |
| Stop if exceeded: not triggered | Pass |

## Risk/test coverage result

Per `aria/context/test-risk-matrix.md`:

| Area | Classification | Tests | Negative Tests |
|------|---------------|-------|----------------|
| Cache eligibility (FR-02) | High risk | 5 | Yes (ineligible cases) |
| Storage pressure policy (FR-05, FR-06) | High risk | 15 | Yes (invalid, critical) |
| Cleanup preview (FR-07) | High risk | 12 | Yes (empty, zero-candidate) |
| Confirmation-required (FR-08) | High risk | 10 | Yes (mode/pressure combos) |
| Invalid budget/size (FR-09) | High risk | 9 | Yes (negative, overflow) |
| Offline availability (FR-01) | Medium risk | 5 | Yes (unsupported sources) |
| Cache operation preview (FR-03) | Medium risk | 10 | Yes (blocked operations) |
| Model defaults and serialization | Medium risk | 19 | Yes (all models covered) |
| Determinism, no external calls | High risk | 8 | Yes |

## Delta updated?

Yes. `aria/context/current.md` and `aria/context/delta.md` updated.

## Fake-hostility checks applied?

Services are deterministic, local, offline, standard-library only:
- Never call real network, filesystem, or provider code.
- Same inputs produce same outputs (verified in tests).
- Return safe error results for invalid inputs.
- Never mutate external state.
- No external dependencies beyond `noqlen_aria.contracts`.

## Risks remaining

- R01: Storage pressure thresholds (10%, 25%, 50%) are arbitrary and may need tuning for real devices. Mitigation: thresholds are simple; easy to adjust.
- R02: Cleanup preview depends on explicit candidate lists from callers. Real candidate enumeration is deferred. Mitigation: preview accepts explicit lists.
- R03: Conservative/Balanced/Aggressive mode semantics may not match all user expectations. Mitigation: modes are documented policy rules; deterministic behavior is predictable.

## Required fixes

None.

## Optional improvements

None.

## Final status

Pass. Implementation complete and validated. 746/746 tests pass. No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage APIs, provider mutation, stream resolution, playback engine, or Bloco 15 behavior added.

## Known limitations

- Storage pressure thresholds are percentage-based and excluded from real device inspection.
- Cleanup preview requires explicit candidate item lists from callers.
- Policy mode rules are hardcoded; future work could make them configurable via preferences.
- `PendingCacheOperation` is a tracking model only; no queueing engine exists.

## Follow-up tasks

- Bloco 15: Stream Quality, Transcoding and Network Policy (do not start without explicit approval).
- Audit 14-16: Offline/Quality/Capabilities Audit (do not start without explicit approval).
- Future: Real cache engine consuming approved intents (separate spec).

## Aria context updates needed

Completed.
