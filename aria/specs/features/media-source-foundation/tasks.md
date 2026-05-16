# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/media-source-foundation/requirements.md`.
- [x] Read `aria/specs/features/media-source-foundation/design.md`.
- [x] Confirm Bloco 0-7 validation passes (CLI help, doctor, py_compile, pytest: 368 tests).
- [x] Confirm no source file exists at `src/noqlen_aria/media_source.py`.
- [x] Confirm no test file exists at `tests/test_media_source.py`.
- [x] Confirm `pyproject.toml` has no external dependencies to add.
- [x] Confirm no provider integration, streaming, playback, or UI code exists.

## TDD classification

For future implementation:

### Required for TDD

- Capability mapping: source capability summary must correctly normalize supported/unavailable capabilities for every combination. Incorrect capability mapping silently misleads the library layer and UI.
- Fake source error/degraded behavior: `FakeMediaSourceClient` failure injection must be deterministic and safe. Degraded paths (source unavailable, capability missing) are safety-critical.
- Stream handle unavailable behavior: when a stream cannot be resolved, the result must be safe and the caller must handle it without crashing.

### Recommended for TDD

- Model defaults and safe serialization: all dataclass and newtype defaults must be valid and serialization-safe.
- `MediaSourceInfo` availability state transitions: all four states must be modeled correctly.
- `SourceCapabilitySummary` with empty supported/unavailable sets: edge case for a source with no declared capabilities.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`, future implementation must address:

| Area | Risk | Expected Tests | Coverage Focus |
|------|------|---------------|----------------|
| Capability mapping (FR-03) | High | 8+ | All SourceCapability values, supported/unavailable split, normalization |
| Safe degraded behavior (FR-09) | High | 6+ | SOURCE_UNAVAILABLE, STREAM_NOT_RESOLVED, capability-missing states |
| FakeMediaSourceClient (FR-02) | High | 7+ | Determinism, error injection on all public methods, configurable state |
| MediaSourceClient protocol (FR-01) | Medium | 3+ | Structural typing, runtime_checkable compliance |
| Source identity/availability (FR-04, FR-08) | Medium | 5+ | SourceAvailabilityState transitions, MediaSourceInfo defaults |
| Abstract media IDs (FR-05) | Medium | 3+ | MediaIdKind values, serialization, equality |
| Stream handle (FR-06) | Medium | 3+ | StreamAvailability states, format hints, unavailable default |
| Provider capability (FR-07) | Medium | 2+ | ProviderCapability → SourceCapability mapping |
| Canonical Examples | — | 8 | CE-01 through CE-08 |
| Edge Cases | — | 8+ | EC-01 through EC-10 at minimum |

All high-risk items must have negative tests proving failure paths are safe and deterministic.

## Behavior Budget check

For this spec task:

- New behaviors: spec only. Zero runtime behavior changes. ✓
- Public API changes: proposed only via future module layout. No source code created. ✓
- Files allowed: `aria/specs/features/media-source-foundation/**`, plus `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` if needed. ✓
- Tests required: none in this task. Validation only (existing 368 tests must pass). ✓
- Dependencies: none added. ✓
- Stop if: any implementation code, provider integration, or source code change becomes necessary. Not triggered. ✓

For future implementation, the budget will be re-evaluated against the design.

## Implementation tasks

All tasks complete.

### Task 1: Create source file skeleton

- [x] Create `src/noqlen_aria/media_source.py` with module docstring and imports.
- [x] Import `AriaResult`, `AriaError` from `noqlen_aria.contracts`.
- [x] Create `tests/test_media_source.py` with test imports and pytest markers.
- [x] Validate: `python3 -m py_compile src/noqlen_aria/media_source.py` passes.

### Task 2: Implement media source identity models

- [x] Define `MediaSourceId`, `MediaSourceType`, `SourceAvailabilityState`, `MediaSourceInfo`.
- [x] Test source identity construction, defaults, and availability state.
- [x] Validate: pytest passes for identity model tests.

### Task 3: Implement abstract media ID models

- [x] Define `MediaId`, `MediaIdKind`.
- [x] Test MediaId construction, kind enumeration, equality, and serialization.
- [x] Validate: pytest passes for media ID tests.

### Task 4: Implement source capability models

- [x] Define `SourceCapability` enum with all values (ARTISTS through LYRICS).
- [x] Define `SourceCapabilitySummary` with `supported` and `unavailable` frozensets.
- [x] Define `ProviderCapability` and `ProviderAvailabilityState`.
- [x] Write TDD tests for capability mapping, normalization, and edge cases.
- [x] Validate: pytest passes for capability tests.

### Task 5: Implement stream handle model

- [x] Define `StreamAvailability` enum and `StreamHandle` dataclass.
- [x] Test stream handle defaults (availability=STREAM_NOT_RESOLVED), format hints, and serialization.
- [x] Validate: pytest passes for stream handle tests.

### Task 6: Implement MediaSourceClient protocol

- [x] Define `MediaSourceClient` as `@runtime_checkable Protocol` with `get_source_info`, `get_capability_summary`, `request_stream`.
- [x] Test structural typing compliance with `isinstance` checks.
- [x] Validate: pytest passes for protocol tests.

### Task 7: Implement FakeMediaSourceClient

- [x] Implement `FakeMediaSourceClient` as a non-frozen dataclass with `_*_error` hooks.
- [x] Implement `get_source_info` with deterministic behavior and failure injection.
- [x] Implement `get_capability_summary` with configurable `supported_capabilities` and failure injection.
- [x] Implement `request_stream` with configurable stream availability and failure injection.
- [x] Write TDD tests for all public methods, error injection, determinism, and safe defaults.
- [x] Validate: pytest passes for all fake tests.

### Task 8: Final validation

- [x] Run full validation suite: `py_compile`, import check, pytest, contamination check.
- [x] Confirm no regression in Bloco 0-7 tests (368 base tests + 100 new = 468 total).
- [x] Confirm no provider brand names appear in source.
- [x] Confirm no Anchor internals, provider internals, or real streaming code.
- [x] Update spec review.md with implementation review.
- [ ] Commit implementation artifacts.

## Validation checklist

Spec phase (this task):

- [x] `pwd` — confirmed working directory.
- [x] `git status --short --branch` — reviewed; only expected changes.
- [x] `git diff --check` — no whitespace issues.
- [x] `find aria/specs/features/media-source-foundation aria/context -maxdepth 5 -type f | sort` — all spec files present.
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [x] `python3 -m pytest` — 368/368 passed.
- [x] Repository contamination check with `git ls-files` patterns — clean.
- [x] Confirm no source code changed beyond spec/context files.
- [x] Confirm no `MediaSourceClient` implementation was created.
- [x] Confirm no provider integration was added.
- [x] Confirm no claim that current Anchor is multi-provider.
- [x] Confirm no Android/UI/playback/queue/cache code was added.

Implementation phase (future):

- [x] `python3 -m py_compile src/noqlen_aria/media_source.py` — passes.
- [x] `PYTHONPATH=src python3 -c "import noqlen_aria.media_source"` — imports clean.
- [x] `python3 -m pytest tests/test_media_source.py -v` — 100/100 pass.
- [x] Full validation suite — 468/468 pass (368 base + 100 new).
- [x] Provider brand name grep on `src/noqlen_aria/media_source.py` — clean.
- [x] Structural typing check: `FakeMediaSourceClient` satisfies `MediaSourceClient` — confirmed.
- [x] Fake hostility checklist applied to `FakeMediaSourceClient` — no external calls, deterministic, error hooks on all public methods.

## Review checklist

Implementation phase:

- [x] Confirm non-goals: no real provider integration, no real streaming, no real playback, no UI.
- [x] Confirm no pyproject.toml changed.
- [x] Confirm no local/private/tooling artifacts staged.
- [x] Confirm Canonical Examples translated to tests (CE-01 through CE-08).
- [x] Confirm Behavior Budget respected.
- [x] Confirm Test Risk Matrix applied.
- [x] Confirm context package (Standard) documented.
- [x] Confirm Anchor multi-provider assumption avoided.
- [x] Confirm no Navidrome/Jellyfin/Emby in type/field/enum names.
- [x] Confirm `MediaSourceClient` boundary defined alongside `ControlClient`.
- [x] Confirm 100 tests covering contracts, fakes, capability mapping, error injection, determinism, and safe degraded behavior.

## Delta update

- [ ] Update `aria/context/current.md` to reflect Bloco 8 implementation completion.
- [ ] Update `aria/context/delta.md` to record Bloco 8 implementation.
- [ ] Update `docs/handoff.md` with Bloco 8 implementation status note.

## Delta update checklist

Before commit, confirm:

- [x] `aria/context/current.md` updated: active milestone and spec sections reflect Bloco 8 spec.
- [x] `aria/context/delta.md` updated: what changed, evidence, next step recorded.
- [x] `docs/handoff.md` updated if a tiny status note is needed.
- [x] Delta is concise and does not duplicate spec content.
- [x] Delta uses consistent tense (past for completed items).
