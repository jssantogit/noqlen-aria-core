# Post-Core Backlog

Aria Core MVP is the foundation. The following features are planned post-core work and are not implemented in the release-prepared MVP. Every future feature requires a dedicated spec before implementation.

## Final Post-Core Roadmap

The roadmap in `docs/aria-core-handoff.md` defines Aria Core MVP as Blocos 0-7. The following Blocos 8-20 are post-core feature expansion and are not implemented in the MVP.

| Bloco | Feature | Status |
|-------|---------|--------|
| 8 | Media Source Foundation: `MediaSourceClient`, `FakeMediaSourceClient`, source capabilities, abstract stream handle, and conceptual provider support via Anchor/provider boundaries | Not started |
| 9 | Library Browse/Search: artists, albums, songs, safe folders, playlists, genres, and search | Not started |
| 10 | Library Filters and Activity: filters, sorting, recently added, recently played, favorites, and library readiness/health badges | Not started |
| 11 | Queue Foundation: `QueueState`, `QueueService`, repeat/shuffle state, predictable queue behavior, and safe errors | Not started |
| 12 | Now Playing Foundation: `NowPlayingState`, current track summary, playback availability, resumable state, and unavailable media state | Not started |
| 13 | Playback Intents: play/pause/skip/seek intent models, intent validation, and blocked/unavailable playback handling | Not started |
| Audit 8-13 | Media/Player State Audit: media sources, library, queue, now playing, and playback intents | Not started |
| 14 | Offline/Cache Policy: `OfflineAvailabilityState`, `CachePolicyState`, storage pressure, pending sync/cache states, and safe confirmations | Not started |
| 15 | Playback Capability Models: gapless, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, and output/device capability state | Not started |
| 16 | Smart Playlists: smart playlists, smart mixes, saved filters, and rule-based playlist planning | Not started |
| 17 | Multi-provider via Anchor: support additional providers beyond Navidrome through Anchor/provider boundaries, without Aria calling provider internals directly | Not started |
| Audit 14-17 | Offline/Capabilities/Providers Audit: offline/cache policy, capabilities, smart playlists, and multi-provider boundaries | Not started |
| 18 | Android Platform Real Integration Planning: real media controls, lock-screen, notification controls, Bluetooth/headset, Android Auto, foreground service, and widgets | Not started |
| 19 | Android Shell Handoff: handoff for the future Android app/UI to consume Aria Core without moving heavy logic into the interface | Not started |
| 20 | Post-core Release Prep: release/handoff for the post-core phase, with docs, checklist, updated backlog, and next steps for the real app | Not started |

## Backlog Resources Covered

The post-core roadmap includes these required feature families:

- Library browse/search for artists, albums, songs, safe folders, playlists, and genres.
- Recently added, recently played, favorites, filters, sorting, and readiness/health badges.
- Queue, repeat/shuffle, predictable queue behavior, and safe queue errors.
- Now playing, playback availability, resumable state, and unavailable media state.
- Playback intents for play, pause, skip, and seek.
- Offline/cache policy, pending sync/cache state, safe confirmations, and storage pressure.
- Real Android media controls, lock-screen controls, notification controls, Bluetooth/headset events, Android Auto, foreground service, and widgets as future Android/platform work.
- Gapless, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, and output/device capability state.
- Smart playlists, smart mixes, saved filters, and rule-based playlist planning.
- Additional providers via Anchor/provider boundaries, without direct provider internals.

## Still Out of Scope Without Future Specs

- Real Anchor apply-mode integration.
- Direct provider integrations or provider internals.
- `PlaybackEngine` real audio engine implementation.
- Real output/renderer/audio driver implementation.
- DSP/EQ audio processing.
- Real bit-perfect audio driver behavior.
- Real Android app shell implementation.
- Real Android Auto, MediaSession, and widget implementation.
- Platform-specific permission and storage adapters.
- Package publishing, tag creation, mutation testing, Pact Broker, or CI/CD changes.

## Rules for Post-Core Work

1. Every feature requires a dedicated Aria spec before implementation.
2. New features must follow fake-first development.
3. New features must not break existing safety boundaries.
4. New features must not couple to specific providers, platforms, or engines without abstraction layers.
5. The `ControlClient` remains source-agnostic.
6. Anchor remains one adapter, not the center of Aria.
7. Other providers come through Anchor/provider boundaries later, not direct provider internals.
8. Android app/UI remains separate and consumes Aria Core.
9. Repository hygiene and scope boundaries must be preserved.
