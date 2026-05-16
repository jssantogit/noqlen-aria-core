# Post-Core Backlog

Aria Core MVP is the foundation. The following features are planned post-core work and are not implemented in the current release. Every future feature requires a dedicated spec before implementation.

## Spec'd Future Blocks (from Roadmap)

The roadmap in `docs/aria-core-handoff.md` defines the following planned blocks:

### Fase 3 — Library / Search / Playlists

| Bloco | Feature | Status |
|-------|---------|--------|
| 7 | Library Browse/Search (artists, albums, tracks, folders, playlists, genres, search, filters, sort, pagination) | Not started |
| 8 | User Library States (recently added, recently played, favorites, play count, last played, resume points, unavailable/missing, health badges) | Not started |
| 9 | Playlists / Smart Playlists (playlist items, availability, smart rules, saved filters, mixes) | Not started |

### Fase 4 — Queue / Now Playing / Playback Intents

| Bloco | Feature | Status |
|-------|---------|--------|
| 10 | Multiple Queues (active queue, history, add/remove/move/clear, play next, replace, repeat/shuffle per queue) | Not started |
| 11 | Now Playing / Playback Intents (current track, position, play, pause, skip, seek, play item) | Not started |
| 12 | Playback Availability (unavailable reasons, source/stream unavailable, permission denied, unsupported format, provider errors) | Not started |

### Fase 5 — Offline / Stream Quality / Output

| Bloco | Feature | Status |
|-------|---------|--------|
| 13 | Offline / Cache / Download Policy (offline inventory, download queue, offline/auto rules, playback/permanent/rolling cache, storage pressure) | Not started |
| 14 | Stream Quality / Transcoding (original quality, max bitrate, transcoding capability, network quality, offline quality) | Not started |
| 15 | Output / Renderers / Audio Capabilities (renderers, USB DAC, Bluetooth, remote, high-res, bit-perfect, sample rate, bit depth, DSD/MQA metadata, processing bypass) | Not started |

### Fase 6 — Playback Policies / Android Boundaries / Backup

| Bloco | Feature | Status |
|-------|---------|--------|
| 16 | Transitions / Loudness Policies (fade, crossfade, smart fade, gapless, ReplayGain, loudness, bit-perfect conflicts) | Not started |
| 17 | Android Media Boundaries (MediaSession, notification, lock-screen, Bluetooth/headset, Android Auto browse, foreground service, widget) | Not started |
| 18 | Backup / Restore / Profiles / Preferences (backup manifest, restore plan, encrypted backup, provider-bound data, profiles, preferences) | Not started |

### Fase 7 — API / Snapshot / Release

| Bloco | Feature | Status |
|-------|---------|--------|
| 19 | Public API / Automation Intents (sync, playback, start media, settings, queue load, backup, cache cleanup, provider connection, renderer selection) | Not started |
| 20 | State Snapshots / API Hardening (`AriaStateSnapshot`, safe serialization, compatibility rules, stable exports) | Not started |
| 21 | End-to-End Fake Flows / Final Release (full fake flow from provider to sync to library to queue to now playing to cache/output/diagnostics/backup, release prep, final hardening) | Not started |

## Unspec'd Future Features

The following are mentioned in architecture docs but not yet broken into dedicated blocks or specs:

- Real Anchor apply-mode integration (currently dry-run only).
- Real provider integrations (Navidrome, Jellyfin, Emby, Plex, Subsonic, AudioBookShelf, Kodi, cloud storage).
- `MediaSourceClient` implementation for library media source access.
- `PlaybackEngine` real audio engine boundary implementation.
- `PlaybackRenderer` and `OutputRoute` real output/renderer implementation.
- DSP/EQ audio processing.
- Real bit-perfect audio driver integration.
- Real Android app shell (Kotlin/Compose) implementing the thin UI adapter.
- Platform-specific permission and storage adapters.
- Real Android Auto, MediaSession, and widget implementation.
- Mutation testing framework and policies.
- Pact Broker for contract testing.
- Automated CI/CD pipeline for testing, linting, and publishing.

## Rules for Post-Core Work

1. Every feature requires a dedicated Aria spec before implementation.
2. New features must follow fake-first development.
3. New features must not break existing safety boundaries.
4. New features must not couple to specific providers, platforms, or engines without abstraction layers.
5. The `ControlClient` remains source-agnostic.
6. Anchor remains one adapter, not the center of Aria.
7. Repository hygiene and scope boundaries must be preserved.
