# Architecture Context

Aria Core exposes a music-player-core API facade while keeping UI/app adapters thin.

Repository-local handoff and broader architecture context live in `docs/aria-core-handoff.md`.

## Layer Model

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

## Boundary Roles

`ControlClient` is the control-plane boundary for status, diagnostics, readiness, lifecycle preview, and control-plane capability. Anchor is one adapter/backend for this boundary.

`MediaSourceClient` is the future media-source boundary for library, search, playlists, metadata, stream handles, normalized IDs, and source capabilities.

`PlaybackRenderer` and `OutputRoute` are future output boundaries for phone, USB DAC, Bluetooth, remote renderer, and route/capability state. They model capabilities and diagnostics, not real drivers.

`PlaybackEngine` is a future real audio engine boundary. It is not part of the current core implementation.

Development is fake-first: define contracts, fakes, mappers, snapshots, and local validation before real integration. Tests must not require network, real music libraries, Anchor, Navidrome, Android, or playback engines.

Aria must use provider/backend adapters through contracts. It must not call Navidrome directly, import Anchor provider internals, or use Anchor CLI as the integration layer.
