# Design

## Summary

Define a planning blueprint for a future minimal UI/app shell that consumes Aria Core as a thin adapter. The shell is a display layer with no business logic. It interacts with Aria Core exclusively through a single `AppShellAdapter` facade, consuming app-facing state snapshots (`AppShellState`) and emitting user actions (`AppShellInput`). All control-plane, playback, diagnostics, permission, and boundary contract logic stays inside Aria Core.

This is a spec/planning task only. No source code, tests, or implementation artifacts are created. The spec proposes types, boundaries, and rules for a future implementation block.

## Context files read

- `AGENTS.md`
- `docs/aria-core-handoff.md`
- `docs/handoff.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
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
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/anchor_adapter.py`
- `src/noqlen_aria/android_boundaries.py`

## Context package

Standard. This is a non-trivial planning spec with multiple proposed types, boundary rules, view model definitions, and cross-layer concerns.

## Existing project context

Blocos 0-4 are complete. The repository has:

- `ControlClient` / `FakeControlClient` (Bloco 1): control-plane contract for status, diagnostics, readiness, lifecycle intents, permissions, storage.
- Five services (Bloco 2): `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`, `ResultMappingService`.
- `AnchorControlClient` adapter (Bloco 3): dry-run Anchor adapter satisfying `ControlClient`.
- Nine Android boundary bridge protocols (Bloco 4): `PlaybackEngineBridge`, `MediaSessionBridge`, `AndroidStorageBridge`, `AndroidAutoBridge`, `ForegroundServiceBridge`, `AppLifecycleBridge`, `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge`, plus composite `AndroidBoundarySnapshot`.

Architecture model: `Future UI/App Shell (thin adapter) -> Aria Core -> ControlClient/MediaSourceClient contracts -> adapters -> providers/backends`.

Bloco 5 is planning a future UI shell layer that wraps all existing Aria Core services behind a single entry-point facade.

## Files to create

Spec (created now):

- `aria/specs/features/minimal-ui-shell-planning/requirements.md`
- `aria/specs/features/minimal-ui-shell-planning/design.md`
- `aria/specs/features/minimal-ui-shell-planning/tasks.md`
- `aria/specs/features/minimal-ui-shell-planning/review.md`

Source (targeted for future implementation, NOT created now):

- `src/noqlen_aria/app_shell.py` — `AppShellAdapter` protocol, `FakeAppShellAdapter`, `AppShellState`, `AppShellInput`.
- `src/noqlen_aria/view_models.py` — per-screen view model dataclasses (or colocated in `app_shell.py`).

Tests (targeted for future implementation, NOT created now):

- `tests/test_app_shell.py` — tests for `AppShellAdapter` contract, fake adapter, state composition, action routing, and anti-coupling verification.

## Files to modify

- `aria/context/current.md` — update to reflect Bloco 5 spec completion.
- `aria/context/delta.md` — record Bloco 5 spec creation.
- `docs/handoff.md` — add Bloco 5 spec status note.

## Files that must not be touched

- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/anchor_adapter.py`
- `src/noqlen_aria/android_boundaries.py`
- `tests/*.py`
- `pyproject.toml`
- All Android, Kotlin, Java, Gradle, React, Compose files (none exist)
- Any secret, credential, log, cache, or temporary file

## Architecture: Thin UI Shell Boundary

```
┌─────────────────────────────────────────────────────────────┐
│ Future Thin UI Shell                                        │
│ (Kotlin/Compose, Swift/UIKit, React, etc.)                  │
│                                                             │
│  - Renders views from view models                           │
│  - Captures user input as AppShellInput                     │
│  - No business logic                                        │
│  - No direct Anchor/Navidrome/provider calls                │
│  - No direct ControlClient calls                            │
│  - No direct boundary bridge calls                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ single entry point
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ AppShellAdapter (proposed future module)                    │
│                                                             │
│  - get_app_shell_state() -> AriaResult[AppShellState]       │
│  - send_input(input: AppShellInput, **kwargs) ->            │
│    AriaResult[bool]                                         │
│  - collect_diagnostics() -> AriaResult[DiagnosticsViewState]│
│  - subscribe(callback) -> AriaResult[bool]                  │
│                                                             │
│  Internally wires:                                          │
│  - ControlClient (status, library, readiness, lifecycle)    │
│  - StatusService, DiagnosticsService, ReadinessService      │
│  - LifecycleIntentService                                   │
│  - PlaybackEngineBridge, MediaSessionBridge (Bloco 4)       │
│  - AndroidStorageBridge, AndroidAutoBridge (Bloco 4)        │
│  - Other Bloco 4 bridges                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Aria Core (existing, no changes needed)                     │
│                                                             │
│  - contracts.py: ControlClient, view states, result types   │
│  - services.py: StatusService, DiagnosticsService, ...      │
│  - anchor_adapter.py: AnchorControlClient                   │
│  - android_boundaries.py: 9 bridge protocols + fakes        │
└─────────────────────────────────────────────────────────────┘
```

## Expected module layout (proposal, not created now)

### `src/noqlen_aria/app_shell.py` (proposed future file)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Protocol, runtime_checkable

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    DiagnosticsViewState,
    LifecycleIntent,
    PermissionState,
    ReadinessViewState,
    ServerViewState,
    StorageAccessState,
)
from noqlen_aria.android_boundaries import (
    AndroidBoundarySnapshot,
    AppLifecycleBridge,
    AndroidAutoBridge,
    AndroidStorageBridge,
    ForegroundServiceBridge,
    HeadsetControlBridge,
    LockScreenBridge,
    MediaSessionBridge,
    NotificationControlBridge,
    PlaybackEngineBridge,
    PlaybackCommand,
)


class AppShellInput(Enum):
    """User-facing actions emitted by the thin UI shell."""

    INITIALIZE = auto()
    SHUTDOWN = auto()
    RESET = auto()
    REFRESH_STATUS = auto()
    COLLECT_DIAGNOSTICS = auto()
    ASSESS_READINESS = auto()
    CHECK_PERMISSION = auto()
    CHECK_STORAGE = auto()
    PLAYBACK_COMMAND = auto()       # payload: PlaybackCommand + kwargs
    MEDIA_SESSION_ACTION = auto()   # payload: MediaSessionAction + kwargs
    NOTIFICATION_ACTION = auto()    # payload: NotificationAction
    LOCK_SCREEN_ACTION = auto()     # payload: NotificationAction
    HEADSET_EVENT = auto()          # payload: HeadsetEventType


@dataclass(frozen=True)
class AppShellState:
    """Composite snapshot of all app-facing state for UI shell consumption."""

    server: ServerViewState = field(default_factory=ServerViewState)
    diagnostics: DiagnosticsViewState = field(default_factory=DiagnosticsViewState)
    readiness: ReadinessViewState = field(default_factory=ReadinessViewState)
    permission: PermissionState = PermissionState.UNKNOWN
    storage_access: StorageAccessState = StorageAccessState.UNKNOWN
    android_boundary: AndroidBoundarySnapshot | None = None


@runtime_checkable
class AppShellAdapter(Protocol):
    """Single entry-point facade for all UI-to-Core communication.

    Future UI shells call only this protocol.
    No direct ControlClient, Anchor, Navidrome, provider, or bridge access.
    """

    def get_app_shell_state(self) -> AriaResult[AppShellState]: ...

    def send_input(
        self, input: AppShellInput, **kwargs
    ) -> AriaResult[bool]: ...

    def collect_diagnostics(self) -> AriaResult[DiagnosticsViewState]: ...

    def subscribe(
        self,
        callback: Callable[[AppShellState], None],
    ) -> AriaResult[bool]: ...
```

Note: This is a design proposal. Exact field lists, method signatures, and defaults are subject to refinement during implementation. `subscribe` is a future concern for reactive UI; initial implementation uses pull-based `get_app_shell_state()`.

### View models (proposed, per-screen)

```python
# ── Status Screen View Model ────────────────────────────

@dataclass(frozen=True)
class StatusScreenViewModel:
    connected: bool = False
    server_url: str = ""
    server_version: str = ""
    latency_ms: int | None = None
    last_error_message: str = ""


# ── Diagnostics Screen View Model ───────────────────────

@dataclass(frozen=True)
class DiagnosticsWarningItem:
    code: str
    message: str
    severity: str = "warning"  # "info", "warning", "error"


@dataclass(frozen=True)
class DiagnosticsScreenViewModel:
    warnings: list[DiagnosticsWarningItem] = field(default_factory=list)
    warning_count: int = 0
    all_clear: bool = True


# ── Readiness Screen View Model ─────────────────────────

@dataclass(frozen=True)
class ReadinessCheckItem:
    label: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class ReadinessScreenViewModel:
    checks: list[ReadinessCheckItem] = field(default_factory=list)
    all_ready: bool = False


# ── Permission/Storage Screen View Model ────────────────

@dataclass(frozen=True)
class PermissionScreenViewModel:
    permission_state: str = "unknown"     # "granted", "denied", "unknown"
    storage_state: str = "unknown"        # "available", "unavailable", "unknown"
    storage_checks: list[ReadinessCheckItem] = field(default_factory=list)
    overall_ok: bool = False
```

These view models are display-ready: strings, booleans, numbers. No raw error objects, no internal identifiers requiring interpretation. UI shell renders them directly.

## Data flow

```
User Action
    │
    ▼
UI Shell captures action
    │
    ▼
UI Shell emits AppShellInput via adapter.send_input()
    │
    ▼
AppShellAdapter routes to appropriate Aria Core service:
    ├── INITIALIZE/SHUTDOWN/RESET  ──> LifecycleIntentService + ControlClient
    ├── REFRESH_STATUS             ──> StatusService
    ├── COLLECT_DIAGNOSTICS        ──> DiagnosticsService
    ├── ASSESS_READINESS           ──> ReadinessService
    ├── CHECK_PERMISSION           ──> ControlClient.get_permission_state()
    ├── CHECK_STORAGE              ──> ControlClient.get_storage_access_state()
    ├── PLAYBACK_COMMAND           ──> PlaybackEngineBridge.send_command()
    ├── MEDIA_SESSION_ACTION       ──> MediaSessionBridge.handle_action()
    ├── NOTIFICATION_ACTION        ──> NotificationControlBridge.handle_action()
    ├── LOCK_SCREEN_ACTION         ──> LockScreenBridge.handle_action()
    └── HEADSET_EVENT             ──> HeadsetControlBridge.handle_event()
    │
    ▼
Aria Core returns AriaResult
    │
    ▼
AppShellAdapter returns result to UI Shell
    │
    ▼
UI Shell re-renders from updated state
```

State flow (pull):

```
UI Shell requests state
    │
    ▼
adapter.get_app_shell_state()
    │
    ▼
AppShellAdapter composes AppShellState:
    ├── server    ← ControlClient.get_server_state()
    ├── diagnostics ← DiagnosticsService.collect()
    ├── readiness   ← ReadinessService.assess()
    ├── permission  ← ControlClient.get_permission_state()
    ├── storage_access ← ControlClient.get_storage_access_state()
    └── android_boundary ← AndroidBoundarySnapshot (if Android platform)
    │
    ▼
Returns AppShellState to UI Shell
```

## Anti-coupling rules (design-time and review-time enforcement)

| Rule | Verification method |
|------|-------------------|
| UI shell must not import `noqlen_aria.anchor_adapter` | grep for `anchor_adapter` in UI code |
| UI shell must not call `ControlClient` directly | grep for `ControlClient` in UI code |
| UI shell must not call `PlaybackEngineBridge` directly | grep for `PlaybackEngineBridge` in UI code |
| UI shell must not call any bridge protocol directly | grep for `Bridge` in UI code |
| UI shell must not import `Navidrome`, `Anchor`, provider modules | grep for provider names in UI code |
| UI shell must communicate exclusively through `AppShellAdapter` | only `AppShellAdapter` import allowed in UI code |
| UI shell must not contain playback logic (state machines, transitions) | review for playback state machine code in UI |
| UI shell must not contain queue/now-playing logic | review for queue data structures in UI |
| UI shell must not construct `AriaResult` objects | grep for `AriaResult` constructor calls in UI code |

These rules are enforced by convention and architecture review. Future blocks may add runtime guards (e.g., `__all__` restrictions, adapter-only access patterns).

## Error handling

- All adapter methods return `AriaResult[T]` for consistent error propagation.
- UI shell must handle `AriaResult.ok=False` by rendering the error message from `result.error.message`.
- UI shell must not interpret `AriaError.code`; codes are for logging and internal routing.
- Adapter must never throw raw exceptions to UI shell; all failures are wrapped in `AriaResult`.
- If any sub-service fails during `get_app_shell_state()`, the adapter collects what it can and populates `DiagnosticsViewState` with appropriate warnings.
- `AppShellState` uses safe defaults (e.g., `connected=False`, `all_ready=False`) when services are unavailable.

## Security considerations

- No secrets, tokens, URLs, or credentials in adapter or view model types.
- No network calls from view model construction.
- No filesystem access from adapter layer.
- No subprocess execution.
- No real Android API access.
- `AppShellState` must not leak internal error details to UI.
- `AriaWarning.message` and `AriaError.message` are sanitized, display-ready strings.
- No caching of sensitive data in `AppShellState` or view models.

## Dependencies

- No runtime dependencies beyond Python 3.11+ standard library (`dataclasses`, `enum`, `typing`).
- Internal dependencies: `noqlen_aria.contracts` (existing), `noqlen_aria.services` (existing), `noqlen_aria.android_boundaries` (existing).
- No additions to `pyproject.toml`.
- No Android SDK, Kotlin, Java, Gradle, React, Compose, or any UI framework.

## Behavior Budget

- New behaviors: documentation/spec only. Zero runtime behavior changes.
- Public API changes: proposed only. No source code created or modified.
- Files allowed: `aria/specs/features/minimal-ui-shell-planning/**`, plus `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` if needed.
- Tests required: none in this task. Validation only (existing commands must pass).
- Dependencies: none added.
- Stop if: any implementation code, source file change, test file change, UI code, Android file, or framework dependency becomes necessary.
- All proposed types are vocabulary-level only. No real adapter implementation.

## Risks

- R01: `AppShellState` may grow too large as more Aria Core services are added, causing unnecessary data transfer. Mitigation: individual getter methods on `AppShellAdapter` allow partial queries; `get_app_shell_state()` is for convenience/serialization.
- R02: `AppShellInput` enum may not cover all future UI actions, leading to enum proliferation. Mitigation: `**kwargs` pass-through allows payload extension without enum changes.
- R03: Anti-coupling rules are convention-based and could be violated accidentally. Mitigation: grep checks in CI/review; future blocks may add runtime guards.
- R04: Per-screen view models may become stale or inconsistent with `AppShellState`. Mitigation: view models are derived from `AppShellState` at construction time; no caching.
- R05: `AndroidBoundarySnapshot` optional field may be misunderstood by non-Android UI shells. Mitigation: explicitly documented as `None` for non-Android platforms.
- R06: Gap between this planning spec and future implementation may lead to design drift. Mitigation: keep spec files as living documents; update during implementation.

## Risk classification

Per `aria/context/test-risk-matrix.md`:

- High risk: Anti-coupling rules (safety rules). Permission/storage state routing (dry-run/apply boundaries). These affect core architectural safety.
- Medium risk: View-state defaults. Public exports (proposed `AppShellAdapter` protocol). `AppShellInput` action routing.
- Low risk: Spec documentation only (this task). No source code changes. Proposed types only.

For this spec-only task, risk is inherently low since no behavior changes are made.

## Rollback strategy

Spec-only task: if the spec is found to be incorrect during review or later implementation, edit the spec files in a focused commit. If the UI shell architecture design is fundamentally wrong, the spec files may be updated or replaced. No source code rollback is needed.

## Validation plan

During this spec-only phase:

1. Run `pwd` to confirm working directory.
2. Run `git status --short --branch` to confirm clean or only expected changes.
3. Run `find aria/specs/features/minimal-ui-shell-planning aria/context -maxdepth 5 -type f | sort` to confirm all spec files present.
4. Run `git diff --check` to confirm no whitespace issues.
5. Run `python3 -m py_compile src/noqlen_aria/*.py` to confirm no regression.
6. Run `PYTHONPATH=src python3 -m noqlen_aria.cli --help` to confirm CLI works.
7. Run `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` to confirm doctor works.
8. Run `python3 -m pytest` to confirm all existing tests pass (358 expected).
9. Run repository contamination check with `git ls-files` patterns.
10. Commit spec files only.

During future implementation phase:

1. Create `src/noqlen_aria/app_shell.py` with `AppShellAdapter` protocol and `FakeAppShellAdapter`.
2. Create `tests/test_app_shell.py` with comprehensive tests.
3. Run full validation suite including structural typing and anti-coupling grep checks.
