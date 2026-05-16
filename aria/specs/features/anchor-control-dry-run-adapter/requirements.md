# Requirements

## Status

Draft for Bloco 3 — Anchor Control Adapter Offline/Dry-Run.

## Problem

Bloco 1 defined the `ControlClient` source-agnostic protocol boundary and `FakeControlClient`. Bloco 2 built a service layer (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) on top of `ControlClient`. No real adapter exists that connects the `ControlClient` contract to Anchor public API helpers. Without an `AnchorControlClient` adapter, Aria Core cannot consume real Anchor control-plane data, cannot validate mapping correctness between Anchor output shapes and Aria contracts, and cannot test the end-to-end data flow from Anchor helpers through Aria services — even in dry-run/offline mode.

## Goal

Define a spec for an `AnchorControlClient` adapter that implements the `ControlClient` protocol by calling Anchor public API helpers in offline/dry-run mode only. The spec must prescribe that the adapter translates Anchor public API helper outputs into Aria `ControlClient` contract types, validates mapping correctness via mocked/fake Anchor API tests, and preserves Aria's source-agnostic architecture. No real Anchor provider internals are called, no Anchor CLI is used, no real life-cycle apply operations are executed, and no real music library is accessed.

## Non-goals

- Real Anchor provider internals (any module not in the public Anchor API facade).
- Anchor CLI as an integration layer.
- Real Navidrome execution or control.
- Real Jellyfin, Emby, or other media server control.
- Real life-cycle apply operations (`send_lifecycle_intent` with apply-mode semantics).
- Real music library access or mutation.
- Anchor service configuration or launch.
- Media source integration (`MediaSourceClient` for library/search/stream/playlists).
- Playback engine, queue, now playing, cache/offline, or UI.
- Android SDK, Kotlin, Java, or Gradle code.
- Real server-side diagnostics or health probes against a live Navidrome instance.
- Any filesystem, network, or subprocess calls in the adapter implementation itself (mocked API calls only).

## Actors

- Future thin UI adapters (Android app, CLI test harness).
- Future implementation agents (Bloco 3 implementation phase).
- Maintainer.
- Anchor public API provider (future external dependency; mocked/faked during Bloco 3).

## Functional requirements

- FR01: `AnchorControlClient` must satisfy the `ControlClient` protocol (`runtime_checkable Protocol` defined in `src/noqlen_aria/contracts.py`) structurally, without subclassing or importing Anchor internals directly in its class definition.
- FR02: `AnchorControlClient` must delegate each `ControlClient` method to one or more Anchor public API helper calls and translate the returned Anchor output shapes into Aria contract types (`AriaResult`, `ServerViewState`, `LibraryViewState`, `ReadinessViewState`, `DiagnosticsViewState`, `LifecycleIntent`, `PermissionState`, `StorageAccessState`).
- FR03: `AnchorControlClient` must only call Anchor public API facade helpers. If exact callable names from the Anchor public API are uncertain at spec time, the adapter must document the candidate Anchor surface and require confirmation during implementation from the current Anchor public API module.
- FR04: `AnchorControlClient` must operate in offline/dry-run mode only. It must not execute real life-cycle apply operations. The `send_lifecycle_intent` method must return a preview-only result (or raise a safe error) that indicates apply-mode is blocked.
- FR05: All Anchor output mapping must go through Aria's existing `ResultMappingService` (or equivalent mapping layer) where appropriate, to enforce consistent error/warning normalization and `AriaResult` wrapping.
- FR06: `AnchorControlClient` must handle the case where the `noqlen_anchor` package is not installed. The import of Anchor public API symbols must be guarded (e.g., lazy import, optional dependency check) and must return safe error results rather than crashing the application.
- FR07: Tests must mock Anchor public API helpers. No real Anchor package, no real Navidrome, no real music library, and no network/filesystem calls may be involved in tests.
- FR08: The adapter must be defined in a dedicated module under `src/noqlen_aria/` (e.g., `src/noqlen_aria/anchor_adapter.py`) and must be importable without a hard dependency on `noqlen_anchor`.
- FR09: The adapter must support status, diagnostics, readiness, capability summary, and life-cycle preview flows where the Anchor public API provides matching helpers.
- FR10: The adapter must sanitize outputs: no secrets, no raw logs, no personal paths, no provider-internal error messages in returned Aria results.
- FR11: The adapter must preserve Aria's source-agnostic architecture: Anchor is a concrete adapter implementing the generic `ControlClient` protocol. No Anchor-specific types or naming conventions may leak into the public-facing contract layer.
- FR12: The adapter must honor Aria's dry-run/apply safety boundary: any method with side-effect potential (lifecycle, reconfiguration) must either be read-only/preview-only or return a clear error indicating that apply-mode is not available.

## Non-functional requirements

- NFR01: No runtime dependency on `noqlen_anchor` for core Aria module imports. The Anchor import must be optional and guarded.
- NFR02: All tests must run without the `noqlen_anchor` package installed.
- NFR03: The adapter must not add any dependency to `pyproject.toml`.
- NFR04: The adapter must not call network, filesystem, or external processes directly. Only mocked/faked Anchor API calls are permitted during testing.
- NFR05: All public names must be explicit, stable, and documented in English.
- NFR06: The adapter must use Bloco 1 contract types exclusively for all inputs and outputs. No raw Anchor types may cross the `ControlClient` boundary.
- NFR07: Tests must be deterministic: repeated runs with identical mock configurations must produce identical results.
- NFR08: Adapter code must follow existing project conventions (Python 3.11+, `dataclasses`, `typing`, no third-party deps).

## Edge cases

- `noqlen_anchor` not installed: every `AnchorControlClient` method must return `AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", ...))`.
- `noqlen_anchor` installed but the underlying Anchor service is unavailable (simulated via mock): adapter must return appropriate `ServerViewState(connected=False, ...)` or similar error results.
- Anchor public API returns unexpected data shapes (simulated via mock): adapter must handle gracefully, returning error results with `ANCHOR_UNEXPECTED_OUTPUT` or equivalent error code.
- All `ControlClient` protocol methods called on the adapter: must return `AriaResult`-wrapped values matching the protocol's return type annotations structurally.
- `send_lifecycle_intent` called on the adapter: must return `AriaResult(ok=False, error=AriaError(code="APPLY_MODE_BLOCKED", ...))` or equivalent, indicating apply-mode is blocked in this adapter version.
- Anchor public API helper raises an exception (simulated via mock): adapter must catch and wrap into `AriaResult(ok=False, ...)`.
- Sensitive data in Anchor API return values (simulated via mock): adapter must sanitize before returning.
- Repeated calls to adapter methods with identical mock state: must return equivalent results (deterministic behavior).

## Acceptance criteria

- AC01: `aria/specs/features/anchor-control-dry-run-adapter/` contains the spec (requirements, design, tasks, review).
- AC02: No source code, test code, `pyproject.toml`, or other non-spec files are created by this spec.
- AC03: Spec clearly states Bloco 3 is a spec/planning phase only. Implementation is a later phase after spec approval.
- AC04: Spec clearly states the adapter must use Anchor public API helpers only, in dry-run/offline mode only, with no real apply operations, no provider internals, and no Anchor CLI.
- AC05: Spec defines the expected Anchor public API candidate surfaces for mapping (diagnostics helpers, readiness/safety summary helpers, server status/inspection helpers, config dry-run/render helpers, Navidrome offline/dry-run helpers).
- AC06: Spec defines how `AnchorControlClient` fits under the generic `ControlClient` boundary and how Anchor outputs map through existing `ResultMappingService`.
- AC07: Spec defines how import/dependency behavior works when `noqlen_anchor` is unavailable.
- AC08: Spec defines how tests will mock Anchor API without requiring real Anchor/Navidrome.
- AC09: Spec defines how dry-run/apply safety is enforced.
- AC10: Existing Bloco 0 + Bloco 1 + Bloco 2 validation commands pass without regression.
- AC11: Repository contamination check is clean.
- AC12: Spec is committed with `docs(spec): add Anchor control dry-run adapter spec`.

## Open questions

- OQ01: What are the exact callable names in the current Anchor public API facade for diagnostics, readiness, server status, library metadata, config dry-run, and Navidrome offline inspection? (Requires confirmation from the current Anchor public API module during implementation. The spec documents candidate surfaces; exact names must be resolved at implementation time.)
- OQ02: Should `AnchorControlClient` be a class with Anchor API import inside `__init__` (lazy import) or should the import be at the top of the module with a try/except? (Deferred to design: lazy import is recommended to avoid import-time failures.)
- OQ03: Should `AnchorControlClient` cache Anchor API helper references after the first call, or re-resolve on each method invocation? (Deferred to design: constructor-time resolution with lazy import is recommended.)
- OQ04: Should the adapter expose a `is_anchor_available()` class/static method for external readiness checks? (Deferred to design: yes, a static check is useful for diagnostics and should be included.)
- OQ05: How should the adapter handle the case where Anchor public API changes between Aria versions? (Mitigation: the adapter maps Anchor shapes into Aria contracts, so internal mapping code can be updated without changing the `ControlClient` contract. Version compatibility checks are out of scope for Bloco 3.)
- OQ06: Should mapping from Anchor output shapes to Aria view states be in a separate `AnchorResultMapper` class or inline in `AnchorControlClient` methods? (Deferred to design: separate mapper for testability; mapping logic should be independently testable.)
- OQ07: How should `send_lifecycle_intent` previews be generated from Anchor helpers? (The adapter should call Anchor config dry-run/render helpers or readiness helpers to produce a life-cycle preview, not execute the intent. Exact mapping depends on available Anchor helpers.)
- OQ08: What `AriaWarning` codes should the adapter produce for Anchor-specific diagnostics? (Deferred to design/implementation: codes like `ANCHOR_NOT_AVAILABLE`, `ANCHOR_CONFIG_STALE`, `ANCHOR_SERVICE_UNHEALTHY` may be appropriate.)
- OQ09: Should the adapter hold a reference to an Anchor API client object, or should each method call standalone public API helpers? (Deferred to design: depends on the Anchor public API module structure.)
- OQ10: Should `AnchorControlClient` tests use `unittest.mock` or a hand-rolled fake Anchor API? (Deferred to design: `unittest.mock` with `MagicMock`/`patch` for controlled behavior is recommended for simplicity and stdlib compatibility.)
