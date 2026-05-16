# Public API Surface

Aria Core MVP stable public exports. All exports are source-agnostic and do not expose provider internals, Anchor internals, Android SDK types, UI types, or playback engine types.

## Top-Level Package `noqlen_aria`

| Export | Type | Description |
|--------|------|-------------|
| `__version__` | `str` | Package version (`0.0.0`) |
| `AnchorControlClient` | class | Optional dry-run/offline `ControlClient` adapter for Anchor |
| `AriaError` | dataclass | Sanitized error with stable internal code |
| `AriaResult` | dataclass | Generic success/failure envelope |
| `AriaWarning` | dataclass | Sanitized warning with stable internal code |
| `ControlClient` | ABC | Source-agnostic control-plane protocol |
| `DiagnosticsService` | class | Diagnostics collection over `ControlClient` |
| `DiagnosticsViewState` | dataclass | Safe diagnostics warnings for UI display |
| `FakeControlClient` | class | Deterministic fake for testing |
| `LibraryViewState` | dataclass | Library availability and aggregate counts |
| `LifecycleIntent` | Enum | Lifecycle actions (startup, shutdown, etc.) |
| `LifecycleIntentPreview` | dataclass | Preview result for a lifecycle intent |
| `LifecycleIntentService` | class | Lifecycle preview service |
| `PermissionState` | dataclass | Platform-agnostic permission state |
| `ReadinessService` | class | Composite readiness assessment |
| `ReadinessViewState` | dataclass | Readiness, status, and diagnostics aggregate |
| `ResultMappingService` | class | Result/value mapping service |
| `ServerViewState` | dataclass | Server connectivity and version |
| `StatusService` | class | Control-plane status service |
| `StorageAccessState` | dataclass | Platform-agnostic storage state |
| `safe_serialize` | function | JSON-compatible safe serialization |
| `sanitize_text` | function | User-facing safe text sanitization |

## Module `noqlen_aria.android_boundaries`

Available as abstract vocabulary and fakes only — not Android SDK integration:

| Export | Type | Description |
|--------|------|-------------|
| `AndroidBoundarySnapshot` | dataclass | Composite snapshot of all boundary states |
| `AndroidAutoBridge` | Protocol | Android Auto browse model boundary |
| `AppLifecycleBridge` | Protocol | App lifecycle event boundary |
| `ForegroundServiceBridge` | Protocol | Foreground service intent boundary |
| `HeadsetControlBridge` | Protocol | Headset/Bluetooth event boundary |
| `LockScreenBridge` | Protocol | Lock-screen control boundary |
| `MediaSessionBridge` | Protocol | MediaSession control boundary |
| `NotificationControlBridge` | Protocol | Notification control boundary |
| `PlaybackEngineBridge` | Protocol | Playback engine boundary |
| `AndroidStorageBridge` | Protocol | Storage access boundary |
| Fake implementations (9 classes) | class | Deterministic fakes for all bridge protocols |
| Supporting enum types (12+) | Enum | Bridge protocol enums |
| Supporting dataclass types (15+) | dataclass | Bridge protocol data types |

## Internal / Not Part of Stable API

The following exist in public modules but are not part of the stable public API surface:

| Name | Module | Reason |
|------|--------|--------|
| `AnchorResultMapper` | `anchor_adapter.py` | Internal mapper; not exported at package level |

## CLI Entry Points

| Entry Point | Command | Description |
|-------------|---------|-------------|
| `noqlen-aria` | `noqlen-aria` | Main CLI entry |
| `noqlen-aria doctor` | `noqlen-aria doctor` | Print safe local package/status info |
