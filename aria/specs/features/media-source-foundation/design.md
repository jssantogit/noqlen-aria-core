# Design

## Summary

Define `MediaSourceClient` as a `@runtime_checkable Protocol`, `FakeMediaSourceClient` as its deterministic fake, plus source capability models (`SourceCapability`, `SourceCapabilitySummary`), media source identity models (`MediaSourceId`, `MediaSourceInfo`, `MediaSourceType`), abstract media ID models (`MediaId`, `MediaIdKind`), an abstract stream handle (`StreamHandle`, `StreamAvailability`), provider/source availability states (`SourceAvailabilityState`, `ProviderAvailabilityState`), and a provider capability discovery model (`ProviderCapability`) — all proposed for a future `src/noqlen_aria/media_source.py` module. No source code is created by this spec. All contracts are provider-agnostic, UI-independent, and use Python standard library types with zero provider-specific imports.

## Context files read

- `AGENTS.md`
- `docs/aria-core-handoff.md`
- `docs/handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/anchor-integration.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `aria/context/future-product-context.md`
- `aria/review/validation-checklist.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/android-player-boundary-contracts/requirements.md`
- `aria/specs/features/android-player-boundary-contracts/design.md`
- `aria/specs/features/android-player-boundary-contracts/tasks.md`
- `aria/specs/features/android-player-boundary-contracts/review.md`
- `src/noqlen_aria/contracts.py`

## Context package

Standard. This is a non-trivial spec with multiple boundary vocabularies, capability models, edge cases, safety concerns, and provider-agnostic design decisions.

## Existing project context

Blocos 0-7 (Aria Core MVP) are complete with local tag `v0.1.0`. The repository has `AriaResult[T]`, `AriaError`, `AriaWarning`, `ControlClient`, `FakeControlClient`, services, the `AnchorControlClient` dry-run adapter, and Android/player boundary contracts defined. `ControlClient` is the control-plane boundary; `MediaSourceClient` is a new media/library boundary that complements it.

Architecture model: `Future UI/App/Player -> Aria Core -> ControlClient/MediaSourceClient contracts -> adapters -> providers/backends`.

Anchor is not the center of Aria. Anchor is one `ControlClient` adapter. Current Anchor integration remains Navidrome-focused. Provider extension readiness (Bloco 20) is a future concern. `MediaSourceClient` must not assume Anchor already supports multiple providers.

Bloco 8 is the first post-core feature block. It defines the media source foundation layer — contracts, fakes, and capability models — without implementing real provider integration.

## Files to create

Spec (created now):

- `aria/specs/features/media-source-foundation/requirements.md`
- `aria/specs/features/media-source-foundation/design.md`
- `aria/specs/features/media-source-foundation/tasks.md`
- `aria/specs/features/media-source-foundation/review.md`

Source (targeted for future implementation, not created now):

- `src/noqlen_aria/media_source.py` — single module with `MediaSourceClient`, `FakeMediaSourceClient`, and all supporting types.

Tests (targeted for future implementation, not created now):

- `tests/test_media_source.py` — tests for `MediaSourceClient` contract compliance, `FakeMediaSourceClient` determinism, capability mapping, availability states, and safe degraded behavior.

## Files to modify

- `aria/context/current.md` — update to reflect Bloco 8 spec completion.
- `aria/context/delta.md` — record Bloco 8 spec creation.
- `docs/handoff.md` — add Bloco 8 spec status note if needed.

## Files that must not be touched

- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/anchor_adapter.py`
- `src/noqlen_aria/android_boundaries.py`
- `tests/*.py`
- `pyproject.toml`
- All Android, Kotlin, Java, Gradle files (none exist)
- Any secret, credential, log, cache, or temporary file

## Proposed module layout (`src/noqlen_aria/media_source.py`)

Proposed contents for future implementation (not created now):

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType, Protocol, runtime_checkable

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
)

# ── Media source identity ────────────────────────────────────

MediaSourceId = NewType("MediaSourceId", str)


class MediaSourceType(Enum):
    REMOTE_SERVER = auto()
    LOCAL_LIBRARY = auto()
    CLOUD_STORAGE = auto()


class SourceAvailabilityState(Enum):
    AVAILABLE = auto()
    DEGRADED = auto()
    UNAVAILABLE = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class MediaSourceInfo:
    source_id: MediaSourceId
    display_name: str
    source_type: MediaSourceType
    availability: SourceAvailabilityState = SourceAvailabilityState.UNKNOWN

# ── Abstract media IDs ───────────────────────────────────────

MediaId = NewType("MediaId", str)


class MediaIdKind(Enum):
    ARTIST = auto()
    ALBUM = auto()
    TRACK = auto()
    PLAYLIST = auto()
    GENRE = auto()
    FOLDER = auto()
    STREAM = auto()

# ── Source capabilities ──────────────────────────────────────

class SourceCapability(Enum):
    ARTISTS = auto()
    ALBUMS = auto()
    TRACKS = auto()
    PLAYLISTS = auto()
    GENRES = auto()
    FOLDERS = auto()
    SEARCH = auto()
    STREAM = auto()
    RATINGS = auto()
    SCROBBLING = auto()
    LYRICS = auto()


@dataclass(frozen=True)
class SourceCapabilitySummary:
    supported: frozenset[SourceCapability] = field(default_factory=frozenset)
    unavailable: frozenset[SourceCapability] = field(default_factory=frozenset)

# ── Stream handle ────────────────────────────────────────────

class StreamAvailability(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    STREAM_NOT_RESOLVED = auto()


@dataclass(frozen=True)
class StreamHandle:
    stream_id: str
    media_id: MediaId
    source_id: MediaSourceId
    availability: StreamAvailability = StreamAvailability.STREAM_NOT_RESOLVED
    format_hint: str | None = None
    quality_hint: str | None = None

# ── Provider capability ──────────────────────────────────────

class ProviderAvailabilityState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    AUTH_REQUIRED = auto()
    ERROR = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class ProviderCapability:
    capabilities: frozenset[SourceCapability] = field(default_factory=frozenset)
    availability: ProviderAvailabilityState = ProviderAvailabilityState.UNKNOWN

# ── MediaSourceClient ────────────────────────────────────────

@runtime_checkable
class MediaSourceClient(Protocol):
    def get_source_info(self) -> AriaResult[MediaSourceInfo]: ...
    def get_capability_summary(self) -> AriaResult[SourceCapabilitySummary]: ...
    def request_stream(self, media_id: MediaId) -> AriaResult[StreamHandle]: ...

# ── FakeMediaSourceClient ────────────────────────────────────

@dataclass
class FakeMediaSourceClient:
    source_id: MediaSourceId = MediaSourceId("fake-source-1")
    display_name: str = "Fake Media Source"
    source_type: MediaSourceType = MediaSourceType.REMOTE_SERVER
    availability: SourceAvailabilityState = SourceAvailabilityState.AVAILABLE
    supported_capabilities: frozenset[SourceCapability] = field(default_factory=frozenset)

    _get_source_info_error: AriaError | None = None
    _get_capability_summary_error: AriaError | None = None
    _request_stream_error: AriaError | None = None

    def get_source_info(self) -> AriaResult[MediaSourceInfo]:
        ...

    def get_capability_summary(self) -> AriaResult[SourceCapabilitySummary]:
        ...

    def request_stream(self, media_id: MediaId) -> AriaResult[StreamHandle]:
        ...
```

Note: This is a design proposal. Exact method signatures, field lists, and defaults are subject to refinement during implementation. All fake implementations must be deterministic and must never call real network, filesystem, or provider code. The `FakeMediaSourceClient` must follow the failure-injection pattern established by `FakeControlClient` (non-frozen dataclass, `_*_error` hooks, optional state overrides).

## Data flow

```
Future UI/App/Player
    │
    ├── ControlClient ──────────────> Aria Core Control Plane
    ├── MediaSourceClient ──────────> Aria Core Media/Library Layer (future)
    │
    └── adapters ──────────────────> providers/backends
```

```
MediaSourceClient (contract)
    │
    ├── get_source_info()        ──> MediaSourceInfo (identity + availability)
    ├── get_capability_summary() ──> SourceCapabilitySummary (what source offers)
    └── request_stream(media_id) ──> StreamHandle (future stream resource)
```

In Bloco 8 (spec):
1. Define `MediaSourceClient` protocol, `FakeMediaSourceClient`, and all supporting types.
2. No implementation, no tests, no source code.

In future implementation:
1. Tests instantiate `FakeMediaSourceClient` for each scenario.
2. Tests verify contract compliance, capability mapping, availability states, and safe degraded behavior.
3. Future library and sync layers consume `MediaSourceClient` without touching provider internals.

Capability discovery flow:
```
Source declares capabilities (e.g., Navidrome supports artists/albums/tracks/playlists)
    -> MediaSourceClient.get_capability_summary()
    -> SourceCapabilitySummary normalizes to SourceCapability enum values
    -> Aria library layer reads supported/unavailable sets
    -> UI renders appropriate browse targets or disabled sections
```

Provider capability vs source capability:
```
ProviderCapability: what a provider type can offer in theory
    e.g., "Navidrome-type providers support artists, albums, tracks, playlists"

SourceCapabilitySummary: what a specific source instance currently exposes
    e.g., "my-navidrome-server currently supports artists, albums, tracks; playlists disabled"
```

## Error handling

- All `MediaSourceClient` methods return `AriaResult[T]` for consistent error propagation.
- `SOURCE_UNAVAILABLE` — source is not connected, try later.
- `STREAM_NOT_RESOLVED` — the requested media cannot be resolved to a stream.
- `CAPABILITY_NOT_SUPPORTED` — the requested operation is not supported by this source.
- `INVALID_MEDIA_ID` — the media ID is malformed or refers to an entity that is not streamable.
- Unknown/invalid inputs return `AriaResult.ok=False` with an `AriaError`.
- `FakeMediaSourceClient` returns deterministic results; it does not throw raw exceptions.
- `StreamHandle` with `availability=STREAM_NOT_RESOLVED` is a valid result (not an error); the caller checks availability.

## Provider boundary considerations

`MediaSourceClient` is the media/library boundary. Aria must never call provider internals directly:

- `ControlClient` remains the control-plane boundary (status, diagnostics, readiness).
- `MediaSourceClient` is the media/library boundary (capabilities, media IDs, streams).
- Anchor currently remains Navidrome-focused.
- Additional providers are a future provider-extension-readiness concern (Bloco 20).
- `MediaSourceClient` must not assume Anchor already supports multiple providers.
- No Navidrome, Jellyfin, Emby, or other provider brand names appear in type or field names.
- Provider type is abstract (`REMOTE_SERVER`, `LOCAL_LIBRARY`, `CLOUD_STORAGE`), not brand-bound.

```
Correct:
  UI -> MediaSourceClient -> future adapters -> Anchor/Navidrome
  (Anchor exposes Navidrome through a public boundary, not provider internals)

Incorrect:
  UI -> Navidrome API directly
  UI -> Jellyfin API directly
  UI -> MediaSourceClient -> provider._navidrome_api
  UI -> MediaSourceClient -> Anchor._subsonic_internals
```

## Security considerations

- No secrets, tokens, URLs, or credentials in contract definitions.
- No network calls, filesystem access, or subprocess execution in boundary contracts.
- No real provider connection, authentication, or authorization code.
- `MediaSourceId` and `MediaId` are opaque identifiers — no credential-derived components.
- `StreamHandle` carries abstract identifiers and format hints only — no real stream URLs or tokens.
- `FakeMediaSourceClient` never accesses real resources.
- No provider internals are exposed through any type or method.

## Dependencies

- No runtime dependencies beyond Python 3.11+ standard library (`dataclasses`, `enum`, `typing`).
- Internal dependency on `noqlen_aria.contracts` for `AriaResult` and `AriaError`.
- No additions to `pyproject.toml`.
- No Android SDK, Kotlin, Java, Gradle, or platform-specific code.

## Behavior Budget

- New behaviors: spec only. Zero runtime behavior changes.
- Public API changes: proposed only via future module layout. No source code created.
- Files allowed: `aria/specs/features/media-source-foundation/**`, plus `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` if needed.
- Tests required: none in this task. Validation only (existing commands must pass).
- Dependencies: none added.
- Stop if: any implementation code, provider integration, or source code change becomes necessary.
- All contracts are vocabulary-level only. No real source, stream, or provider implementation.

## Risks

- R01: Capability model may not cover all future provider feature surfaces. Mitigation: `SourceCapability` enum is extensible; new capabilities can be added non-breakingly.
- R02: `MediaSourceClient` may become too large as a single protocol. Mitigation: sub-protocols can be introduced in future blocks without breaking the base protocol.
- R03: Gap between spec and Anchor's current Navidrome-focused integration may cause confusion about what is available today. Mitigation: spec explicitly documents that current Anchor is Navidrome-focused and multi-provider is Bloco 20 future work.
- R04: `StreamHandle` is underspecified for real streaming implementation. Mitigation: stream handle is intentionally abstract; real streaming details are a future concern.
- R05: Capability mapping between provider capabilities and `SourceCapability` enum may be lossy. Mitigation: normalized vocabulary intentionally simplifies provider differences; source-specific extensions are a future refinement.

## Risk classification

Per `aria/context/test-risk-matrix.md`:

- High risk: Capability mapping (FR-03). These affect safety rules and boundary behavior. Safe degraded behavior (FR-09).
- Medium risk: Source identity and availability states (FR-04, FR-08). Fake `MediaSourceClient` behavior (FR-02). These affect view-state defaults and public exports.
- Low risk: Spec documentation only (this task). No source code changes.

For this spec-only task, risk is inherently low since no behavior changes are made.

## Rollback strategy

Spec-only task: if the spec is found to be incorrect during review or later implementation, edit the spec files in a focused commit. If the boundary vocabulary is fundamentally wrong, the spec files may be updated or replaced. No source code rollback is needed.

## Validation plan

During this spec-only phase:
1. Run `pwd` to confirm working directory.
2. Run `git status --short --branch` to confirm clean or only expected changes.
3. Run `find aria/specs/features/media-source-foundation aria/context -maxdepth 5 -type f | sort` to confirm all spec files present.
4. Run `git diff --check` to confirm no whitespace issues.
5. Run `python3 -m py_compile src/noqlen_aria/*.py` to confirm no regression.
6. Run `PYTHONPATH=src python3 -m noqlen_aria.cli --help` to confirm CLI works.
7. Run `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` to confirm doctor works.
8. Run `python3 -m pytest` to confirm all 368 existing tests pass.
9. Run repository contamination check with `git ls-files` patterns.
10. Review spec for Anchor multi-provider assumption, provider brand names, and non-goal compliance.
11. Commit spec files only.

During later implementation phase:
1. Run `python3 -m py_compile src/noqlen_aria/media_source.py`.
2. Run `PYTHONPATH=src python3 -c "import noqlen_aria.media_source"`.
3. Run `python3 -m pytest tests/test_media_source.py -v`.
4. Run full Bloco 0-8 validation suite including structural typing and fake hostility checks.
