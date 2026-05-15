# Requirements

## Status

Draft for Bloco 1 — Aria Core Contracts.

## Problem

Aria Core has no app-facing product contracts. Bloco 0 is a bootstrap only. Without explicit contracts for results, errors, view states, lifecycle intents, permission state, storage access state, and a source-agnostic control client boundary, future blocks cannot build product behavior safely and no fake-first development is possible.

## Goal

Define UI-independent contracts and a fake control client so that future blocks can develop and test product behavior without real Anchor, Navidrome, UI, playback, queue, cache, or offline access.

## Non-goals

- No real Anchor integration.
- No Anchor provider internals.
- No Anchor CLI as integration layer.
- No direct Navidrome access.
- No Android SDK or UI.
- No playback implementation.
- No queue implementation.
- No cache/offline implementation.
- No real music library access.
- No UI/product behavior.
- No Android-specific state or names.

## Actors

- Future thin UI adapters (Android app, CLI test harness).
- Future implementation agents.
- Maintainer.

## Functional requirements

- FR01: Define `AriaResult` as a structured, explicit result type for app-facing operations.
- FR02: Define `AriaError` as a structured error type with at minimum a code and a human-readable message.
- FR03: Define `AriaWarning` as a structured warning type for non-fatal diagnostics.
- FR04: Define `ServerViewState` to represent server connectivity and status information independently of UI.
- FR05: Define `LibraryViewState` to represent music library metadata independently of UI.
- FR06: Define `DiagnosticsViewState` to represent safe diagnostic/status snapshots independently of UI.
- FR07: Define `ReadinessViewState` as a composite snapshot that captures whether Aria, Anchor, server, and library are ready.
- FR08: Define `LifecycleIntent` as an enum or equivalent for lifecycle transitions that future UI may request.
- FR09: Define `PermissionState` to represent runtime permission status independently of any Android API.
- FR10: Define `StorageAccessState` to represent storage/library availability independently of any Android or OS API.
- FR11: Define `ControlClient` as a source-agnostic protocol/interface contract specifying control-plane operations that Aria expects from any core controller (Anchor is one future adapter), without importing Anchor internals.
- FR12: Define `FakeControlClient` implementing `ControlClient` with deterministic fake behavior suitable for local tests and early development.
- FR13: All contracts must be defined in a dedicated Python module under `src/noqlen_aria/` and must be importable without any external dependencies.
- FR14: `FakeAnchorClient` must return known fake data and must not call any network, filesystem, or external process.

## Non-functional requirements

- NFR01: UI-independent contracts only; no framework-specific code.
- NFR02: Fake-first: `FakeAnchorClient` must be sufficient for all local tests.
- NFR03: No runtime dependencies beyond Python 3.11+ standard library.
- NFR04: Module must be importable with `import noqlen_aria.contracts` or equivalent.
- NFR05: All public names must be explicit, stable, and documented in English.
- NFR06: Contracts must not leak Android, Navidrome, or Anchor internals.

## Edge cases

- View state defaults for uninitialized or disconnected states.
- `ReadinessViewState` when no Anchor client is configured.
- `FakeAnchorClient` must handle calls before any setup/configuration.
- `FakeAnchorClient` must return consistent results across repeated calls with identical inputs.
- `LifecycleIntent` values must be exhaustively defined; unknown or unsupported values must be handled.
- `AriaResult` must distinguish success (with data) from failure (with error) unambiguously.
- `AriaError.code` must use a stable convention (e.g., `UPPER_SNAKE_CASE` strings).

## Acceptance criteria

- AC01: `aria/specs/features/aria-core-contracts/` contains the spec (this file plus design, tasks, review).
- AC02: No source code, test code, `pyproject.toml`, or other non-spec files are created by this spec.
- AC03: Spec clearly states that Bloco 1 creates contracts and fake client only, not real integration.
- AC04: Spec defines the expected source file(s) and test file(s) for later implementation.
- AC05: Existing Bloco 0 validation commands pass without regression.
- AC06: Repository contamination check is clean.
- AC07: Spec is committed with `docs(spec): add Aria Core contracts spec`.

## Open questions

- OQ01: Should `ControlClient` be a `typing.Protocol` or an ABC? (Settled in design: `Protocol` for structural typing, fake-first compatibility.)
- OQ02: Should `AriaResult` use a generic type parameter for the success data? (Settled in design: Yes, `AriaResult[T]`.)
- OQ03: Should `DiagnosticsViewState` include a `warnings: list[AriaWarning]` field? (Deferred to implementation: design will propose the field list.)
- OQ04: Exact `ControlClient` method set. (Deferred to implementation: design will propose initial methods and note that methods are subject to expansion in later blocks.)
