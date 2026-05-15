# Requirements

## Status

Draft for Bloco 2 — Fake Control Client and State Mapping.

## Problem

Bloco 1 defined contracts (`AriaResult`, `AriaError`, `AriaWarning`, view states, `LifecycleIntent`, `PermissionState`, `StorageAccessState`, `ControlClient`, `FakeControlClient`) but no service layer that maps raw `ControlClient` results into app-facing states, normalizes errors/warnings/results, previews lifecycle intents, or composes readiness/diagnostics from lower-level control data. Without this mapping layer, future blocks cannot consume contract data through a stable app-facing surface.

## Goal

Implement a fake-driven service layer that maps `ControlClient` data into Aria app-facing state/results. Every service receives a `ControlClient` (or `FakeControlClient`) and produces normalized `AriaResult`, view-state compositions, diagnostics aggregates, and lifecycle intent previews. All services are deterministic and local-only when used with `FakeControlClient`.

## Non-goals

- No real Anchor adapter (`AnchorControlClient`).
- No media source integration (`MediaSourceClient` for library/search/stream/playlists).
- No playback engine, queue, now playing, cache/offline, or UI.
- No Android SDK, Kotlin, Java, or Gradle.
- No Navidrome, Jellyfin, or Emby integration of any kind.
- No filesystem, network, or subprocess calls from services.
- No CLI expansion or new CLI commands.

## Actors

- Future thin UI adapters (Android app, CLI test harness).
- Future implementation agents (Bloco 3+).
- Maintainer.

## Functional requirements

- FR01: `ResultMappingService` normalizes raw `AriaResult` from `ControlClient` methods into consistent app-facing `AriaResult` shapes, mapping `AriaError` codes and wrapping/unwrapping data where needed.
- FR02: `StatusService` composes `ServerViewState` into a high-level connectivity status response, combining ping latency and server state into a single app-facing result.
- FR03: `DiagnosticsService` collects warnings from multiple `ControlClient` calls (server, library, readiness) into a single `DiagnosticsViewState` aggregate, normalizing `AriaWarning` codes.
- FR04: `LifecycleIntentService` validates and previews lifecycle intents (`INITIALIZE`, `SHUTDOWN`, `RESET`) without executing them against a real control client.
- FR05: `ReadinessService` produces a composite `ReadinessViewState` from `ControlClient` data, computing `all_ready` from server connectivity, library availability, diagnostics warnings, and control configuration status.
- FR06: Every service accepts a `ControlClient` via constructor injection (or method parameter) and delegates all data access to it.
- FR07: All services return only `AriaResult`-wrapped values or contract types from Bloco 1; no raw primitives leak to callers.
- FR08: Services must work correctly with `FakeControlClient` and produce deterministic, reproducible results.
- FR09: `FakeControlClient` must expose configuration hooks (e.g., mutable attributes) so tests can inject failure states (disconnected server, unavailable library, error codes) for service testing.
- FR10: `ResultMappingService` must define factory/helper methods for creating `AriaResult.ok(data)` and `AriaResult.err(error)` instances.
- FR11: `LifecycleIntentService.preview(intent)` must return a structured preview (e.g., `LifecycleIntentPreview`) describing the effect of the intent without invoking `ControlClient.send_lifecycle_intent`.
- FR12: `DiagnosticsService` must produce a `DiagnosticsViewState` with at minimum: latency-based warnings, library staleness warnings, and control-configuration warnings.
- FR13: All services must be defined in dedicated module(s) under `src/noqlen_aria/` and must be importable without external dependencies.
- FR14: All services must not call network, filesystem, or external process.

## Non-functional requirements

- NFR01: No runtime dependencies beyond Python 3.11+ standard library.
- NFR02: Every service must be testable with `FakeControlClient` only; no real Anchor or Navidrome required.
- NFR03: `FakeControlClient` configuration hooks must be simple attribute assignments (no complex mocking framework required).
- NFR04: Service method signatures must use Bloco 1 contract types exclusively for inputs and outputs.
- NFR05: All public names must be explicit, stable, and documented in English.
- NFR06: Module structure must allow importing individual services without side effects (e.g., `from noqlen_aria.services import StatusService`).
- NFR07: Tests must be deterministic: repeated runs with identical `FakeControlClient` configuration must produce identical results.

## Edge cases

- Services receiving `AriaResult(ok=False, error=...)` from `FakeControlClient` (failure-injection scenario).
- `StatusService` when `ServerViewState.last_error` is set.
- `ReadinessService` when server connected but library unavailable (partial readiness).
- `ReadinessService` when `control_configured=False`.
- `DiagnosticsService` when no warnings are present (empty list).
- `DiagnosticsService` when library `last_scan_timestamp` is `None` or very old.
- `LifecycleIntentService.preview()` with each valid `LifecycleIntent` value.
- `LifecycleIntentService.preview()` with an invalid/unknown intent (must handle gracefully, e.g., return error result).
- `ResultMappingService` when `AriaResult.ok=True` but `data` is `None`.
- `ResultMappingService` when `AriaResult.ok=False` but `error` is `None` (malformed result from client).
- Multiple services composed together: `ReadinessService` consuming output of `StatusService` and `DiagnosticsService`.
- Repeated calls to services with same input must return equivalent results.

## Acceptance criteria

- AC01: `aria/specs/features/fake-control-state-mapping/` contains the spec (this file plus design, tasks, review).
- AC02: No source code, test code, `pyproject.toml`, or other non-spec files are created by this spec.
- AC03: Spec clearly states Bloco 2 implements fake-driven mapping/services only; no real Anchor adapter.
- AC04: Spec defines the expected source file(s) and test file(s) for later implementation.
- AC05: Spec lists all five services with their responsibilities.
- AC06: Spec defines `FakeControlClient` failure-injection hooks needed for service testing.
- AC07: Existing Bloco 0 + Bloco 1 validation commands pass without regression.
- AC08: Repository contamination check is clean.
- AC09: Spec is committed with `docs(spec): add fake control state mapping spec`.

## Open questions

- OQ01: Should `FakeControlClient` failure-injection hooks use attribute assignment or a builder pattern? (Deferred to design/implementation: attribute assignment for simplicity.)
- OQ02: Should `DiagnosticsService` expose configurable thresholds (e.g., max latency, max library staleness) or hardcode them? (Deferred to design: configurable via constructor with sensible defaults.)
- OQ03: Should `LifecycleIntentPreview` be a frozen dataclass or a simple named tuple? (Deferred to design: frozen dataclass for consistency with Bloco 1.)
- OQ04: Should `ResultMappingService` be a stateless module with free functions or a class? (Deferred to design: class for consistency with other services and testability.)
- OQ05: Exact method signatures for each service. (Deferred to design: design will propose initial signatures.)
- OQ06: Should services be in a single `services.py` module or one module per service? (Deferred to design: single module for now, given the limited scope of five services.)
- OQ07: Should `ReadinessService` accept pre-computed sub-states or compute them internally from `ControlClient`? (Deferred to design: compute internally for now; decomposition can come later.)
- OQ08: Should `LifecycleIntentService` eventually execute intents via `ControlClient.send_lifecycle_intent`? (Yes, in a future block with explicit apply-mode protection. Not in Bloco 2.)
