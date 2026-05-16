# Review

## Summary

Bloco 8 spec (Media Source Foundation) is complete. The spec defines `MediaSourceClient` as a `@runtime_checkable Protocol`, `FakeMediaSourceClient` as its deterministic fake, source capability models, media source identity/reference models, abstract media IDs, an abstract stream handle, a provider capability discovery model, and provider/source availability states — all for a proposed future `src/noqlen_aria/media_source.py` module. Implementation is deferred to a later task. No source code, tests, or provider integration was created.

## Requirements coverage

All functional requirements (FR-01 through FR-11) are defined.

| FR | Requirement | Status |
|----|-------------|--------|
| FR-01 | MediaSourceClient boundary | Defined |
| FR-02 | FakeMediaSourceClient | Defined |
| FR-03 | Source capability summary model | Defined |
| FR-04 | Media source identity/reference models | Defined |
| FR-05 | Abstract media IDs | Defined |
| FR-06 | Abstract stream handle | Defined |
| FR-07 | Provider capability discovery model | Defined |
| FR-08 | Provider/source availability states | Defined |
| FR-09 | Safe degraded behavior | Defined |
| FR-10 | No provider internals | Defined |
| FR-11 | Spec-only constraint | Enforced |

All non-functional requirements (NFR01-NFR10) are addressed in the spec.

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | Python stdlib only | `dataclasses`, `enum`, `typing` |
| NFR02 | No external dependencies beyond contracts | Only `noqlen_aria.contracts` |
| NFR03 | No Android SDK / platform code | No such references |
| NFR04 | Public names explicit, documented | All types documented |
| NFR05 | Types serialization-safe | All fields are stdlib types |
| NFR06 | `@runtime_checkable` | Protocol marked with decorator |
| NFR07 | `AriaResult[T]` consistently | All methods return `AriaResult` |
| NFR08 | Exhaustive capability enums | 11 capability values defined |
| NFR09 | Fake-hostility pattern | Error hooks, deterministic, no external calls |
| NFR10 | No provider brand names | Abstract categories only |

8 Canonical Examples defined: CE-01 through CE-08.
12 Edge Cases covered in requirements.

## Context package used

Standard. Per `aria/context/context-packages.md`.

## Files changed

Spec created:

- `aria/specs/features/media-source-foundation/requirements.md`
- `aria/specs/features/media-source-foundation/design.md`
- `aria/specs/features/media-source-foundation/tasks.md`
- `aria/specs/features/media-source-foundation/review.md`

Context updated:

- `aria/context/current.md` — updated to reflect Bloco 8 spec completion.
- `aria/context/delta.md` — recorded Bloco 8 spec creation.
- `docs/handoff.md` — added Bloco 8 spec status note.

Files not touched:

- `src/noqlen_aria/contracts.py`, `services.py`, `anchor_adapter.py`, `android_boundaries.py`, `cli.py`, `__init__.py`
- `tests/test_contracts.py`, `test_services.py`, `test_anchor_adapter.py`, `test_android_boundaries.py`, `test_cli.py`, `test_mvp_hardening.py`
- `pyproject.toml`
- All Android, Kotlin, Java, Gradle files (none exist)
- Any secret, credential, log, cache, or temporary file

## Validation performed

- `pwd` — confirmed working directory.
- `git status --short --branch` — only expected changes (spec + context files).
- `git diff --check` — no whitespace issues.
- `find aria/specs/features/media-source-foundation aria/context -maxdepth 5 -type f | sort` — all spec files present.
- `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- `python3 -m pytest` — 368/368 passed, no regression.
- Repository contamination check with `git ls-files` patterns — clean.

## Validation notes

All validation commands passed without regression. No source code, test code, or `pyproject.toml` was modified. The spec defines 11 non-trivial functional requirements, 8 canonical examples, 12 edge cases, and a complete design with proposed module layout, data flow, error handling, security considerations, provider boundary considerations, and risk classification.

Grep for provider brand names in the spec directory confirms no Navidrome, Jellyfin, Emby, or other provider-specific names appear in proposed type, field, or enum names. The spec explicitly states that Anchor is not the center of Aria, current Anchor remains Navidrome-focused, and multi-provider support is a Bloco 20 future concern.

## Non-goals check

| Non-goal | Status |
|---|---|
| No real provider integration | Pass — spec only, no integration code |
| No real streaming implementation | Pass — StreamHandle is abstract, defaults to UNAVAILABLE |
| No real playback engine | Pass — no playback references |
| No UI, Android, screens, navigation | Pass — no UI references |
| No direct Navidrome/Jellyfin/Emby calls | Pass — provider brand names absent from type/field/enum names |
| No assumption Anchor is multi-provider | Pass — spec explicitly states Anchor remains Navidrome-focused |
| No Anchor CLI integration | Pass — no Anchor CLI references |
| No source code created | Pass — spec files only |
| No pyproject.toml modified | Pass |
| No queue/now playing/cache implementation | Pass |

## Behavior Budget result

All budget constraints respected:

| Constraint | Status |
|---|---|
| New behaviors: spec only | Pass |
| Public API changes: proposed only, no source code | Pass |
| Files allowed: spec files + context/handoff | Pass |
| Tests required: none in this task | Pass |
| Dependencies: none added | Pass |
| Stop if implementation becomes necessary | Not triggered |

## Risk/test coverage result

Per `aria/context/test-risk-matrix.md`:

| Area | Classification | Expected Tests (future) | Status |
|------|---------------|------------------------|--------|
| Capability mapping (FR-03) | High risk | 8+ | Defined in spec |
| Safe degraded behavior (FR-09) | High risk | 6+ | Defined in spec |
| FakeMediaSourceClient (FR-02) | High risk | 7+ | Defined in spec |
| MediaSourceClient protocol (FR-01) | Medium risk | 3+ | Defined in spec |
| Source identity/availability (FR-04, FR-08) | Medium risk | 5+ | Defined in spec |
| Abstract media IDs (FR-05) | Medium risk | 3+ | Defined in spec |
| Stream handle (FR-06) | Medium risk | 3+ | Defined in spec |
| Provider capability (FR-07) | Medium risk | 2+ | Defined in spec |

All high-risk areas have TDD requirements and negative test coverage expectations documented in the spec.

## Delta updated?

Yes. `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` updated.

## Fake-hostility checks applied?

Not applicable in this spec-only phase. The `FakeMediaSourceClient` design follows the established fake-hostility pattern:
- Non-frozen dataclass with `_*_error` hooks on all public methods.
- Configurable state overrides.
- Deterministic behavior (no random, no real I/O).
- Never calls real network, filesystem, or provider code.

Fake-hostility checklist will be applied during implementation.

## Risks remaining

- R01: Spec defines 11 `SourceCapability` values; real provider surfaces may require more. Mitigation: enum is extensible.
- R02: `request_stream` method is underspecified — real streaming details are deferred. Mitigation: explicitly marked as abstract/future.
- R03: Gap between `MediaSourceClient` and `ControlClient` — two separate boundaries that must be consumed independently. Future work may need a composite boundary.
- R04: `MediaId` is a simple string newtype; source-specific ID schemes and ID collisions across sources are deferred concerns.
- R05: No security review beyond the spec's stated boundaries; implementation should be reviewed against safety.md and repository-hygiene.md.

## Known limitations

- Spec only — no runtime behavior to validate.
- `FakeMediaSourceClient` implementation details (exact catalog population, stream handle resolution logic) are deferred to implementation.
- `ProviderCapability` to `SourceCapability` mapping is described conceptually but exact mapping rules are deferred.
- No mock catalog data is defined; ad-hoc test data will be created during implementation.
- `request_stream` behavior for media types that are not streamable (folders, genres) is defined as an error but exact error codes are deferred.

## Follow-up tasks

- Bloco 8 implementation: create `src/noqlen_aria/media_source.py` and `tests/test_media_source.py`.
- Bloco 9: Library Browse/Search (depends on `MediaSourceClient`).
- Bloco 20: Provider Extension Readiness (depends on `MediaSourceClient` and provider capability models).
- Apply fake-hostility checklist during Bloco 8 implementation.
- Consider TDD for capability mapping, fake error/degraded behavior, and stream handle unavailable behavior as specified.

## Aria context updates needed

Completed in this task:

- `aria/context/current.md` — updated active milestone and active spec sections to reflect Bloco 8 spec completion.
- `aria/context/delta.md` — recorded Bloco 8 spec creation.
- `docs/handoff.md` — added Bloco 8 spec status note.

## Final status

Pass. Spec is implementation-ready. No source code, tests, or provider integration was created.

## Spec review summary

| Item | Status |
|------|--------|
| Requirements defined (11 FR, 10 NFR) | Pass |
| Canonical Examples (8 Given/When/Then) | Pass |
| Edge cases (12 documented) | Pass |
| Design with module layout | Pass |
| Data flow diagrams | Pass |
| Error handling strategy | Pass |
| Provider boundary considerations | Pass |
| Security considerations | Pass |
| Behavior Budget | Pass |
| Test Risk Matrix | Pass |
| TDD classification | Pass |
| Task breakdown (8 implementation tasks) | Pass |
| Delta update checklist | Pass |
| Non-goals enforced | Pass |
| No provider brand names in types | Pass |
| Anchor multi-provider assumption avoided | Pass |
