# Architecture

Noqlen Aria Core is the modular app/player-facing core of a music player. It owns contracts, states, services, policies, capabilities, fakes, mappers, adapters, snapshots, safe serialization, and tests.

Canonical architecture details and the roadmap live in `docs/aria-core-handoff.md`.

High-level flow:

`Future UI/App/Player -> Aria Core -> contracts/adapters -> providers/backends`

Bloco 5 defines the future UI/app shell boundary in `docs/ui-shell-boundary.md`. The future UI is a thin adapter: it renders Aria Core state, emits Aria Core intents, and never calls providers, Anchor, Navidrome, Android/player bridges, playback engines, queues, now playing, cache, or lifecycle/apply behavior directly.

Layer model:

- Public API / Snapshot Layer
- Control Plane
- Media Provider Layer
- Media Source Layer
- Library Layer
- Sync Layer
- Playlist / Smart Playlist Layer
- Queue / Now Playing Layer
- Offline / Cache / Download Policy Layer
- Stream Quality / Transcoding Layer
- Output / Renderer / Audio Capability Layer
- Playback Policy Layer
- Android Boundary Layer
- Backup / Profiles / Preferences Layer

Anchor is not the center of Aria. Anchor is one optional dry-run `ControlClient` adapter/control-plane backend. Aria must depend on contracts, not Anchor internals, and must not use Anchor CLI or provider internals as integration APIs.

Future UI must be thin and must not contain core business behavior.

UI-facing data must be app-facing and sanitized. Status/readiness views consume `ServerViewState` and `ReadinessViewState`; diagnostics views consume `DiagnosticsViewState`; permission/storage views consume `PermissionState` and `StorageAccessState`; playback/media controls emit intents that Aria Core routes through boundary contracts in future work.

Bloco 6 hardens the MVP public surface. The top-level `noqlen_aria` package intentionally exports only stable app-facing contracts, services, the optional `AnchorControlClient`, and safe output helpers (`safe_serialize`, `sanitize_text`). Android/player boundary vocabulary remains available from `noqlen_aria.android_boundaries` as abstract contracts and fakes, not as Android SDK or playback implementation.
