# Post-Core Backlog

Aria Core MVP is Blocos 0-7 and local tag `v0.1.0` exists. The following features are planned post-core work after `v0.1.0` and are not implemented in the MVP. Every future feature requires a dedicated spec before implementation.

## Final Post-Core Roadmap

The roadmap in `docs/aria-core-handoff.md` defines Aria Core MVP as Blocos 0-7. The following Blocos 8-23 are post-core feature expansion and are not implemented in the MVP.

| Bloco | Feature | Status |
|-------|---------|--------|
| 8 | Media Source Foundation: `MediaSourceClient`, `FakeMediaSourceClient`, source capabilities, abstract stream handle, and base for provider-backed sources via Anchor | Not started |
| 9 | Library Browse/Search: artists, albums, songs, safe folders, playlists, genres, and browse/search | Not started |
| 10 | Library Filters, Activity and Favorites: filters, sorting, recently added, recently played, favorites, and library readiness/health badges | Not started |
| Audit 8-10 | Media Source/Library Audit | Not started |
| 11 | Queue Foundation: `QueueState`, `QueueService`, repeat/shuffle, predictable queue behavior, and multiple queues explicitly as a supported contract direction | Not started |
| 12 | Now Playing Foundation: `NowPlayingState`, current track summary, playback availability, resumable state, and unavailable media state | Not started |
| 13 | Playback, Renderer and Automation Intents: play/pause/skip/seek intents, renderer selection intents, public automation intents, and blocked/unavailable playback handling | Not started |
| Audit 11-13 | Queue/Now Playing/Intents Audit | Not started |
| 14 | Offline, Cache and Storage Policy: offline availability, cache policy, cache cleanup, storage pressure, pending sync/cache states, and safe confirmation states | Not started |
| 15 | Stream Quality, Transcoding and Network Policy: stream quality policy, transcoding capability/policy, network quality policy, and offline quality policy | Not started |
| 16 | Playback Capability Models: gapless capability, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, and output/device capability state | Not started |
| Audit 14-16 | Offline/Quality/Capabilities Audit | Not started |
| 17 | Profiles, Preferences, Backup and Restore: user profiles, preferences, backup/restore for Aria config/state, and no destructive real music library mutation | Not started |
| 18 | Smart Playlists: smart playlists, smart mixes, saved filters, and rule-based playlists inspired by Symfonium | Not started |
| 19 | State Snapshots and End-to-End Fake Flows: state snapshots, API snapshot behavior, and fake source -> library -> queue -> now playing intent -> diagnostics flows | Not started |
| Audit 17-19 | Profiles/Smart/Snapshots Audit | Not started |
| 20 | Provider Extension Readiness: generic provider/source abstractions, no direct Jellyfin/Emby/Navidrome integrations, no assumption that Anchor already supports multiple providers, and future providers through public boundaries/adapters exposed by Anchor or another approved integration layer | Not started |
| 21 | Android Real Integration Planning: real media controls, lock-screen controls, notification controls, Bluetooth/headset, Android Auto, foreground service, and widgets planning | Not started |
| 22 | Android Shell Handoff: handoff for future Android app/UI; UI consumes Aria Core and does not own heavy logic | Not started |
| Audit 20-22 | Providers/Android Handoff Audit | Not started |
| 23 | Post-core Release Prep: checklist, release notes, backlog update, docs, handoff, and release preparation for the post-core phase | Not started |

## Backlog Resources Covered

The post-core roadmap includes these required feature families:

- Library browse/search for artists, albums, songs, safe folders, playlists, and genres.
- Recently added, recently played, favorites, filters, sorting, and readiness/health badges.
- Queue, repeat/shuffle, predictable queue behavior, and safe queue errors.
- Multiple queues as a supported contract direction.
- Now playing, playback availability, resumable state, and unavailable media state.
- Playback intents for play, pause, skip, and seek.
- Renderer selection intents and public/core automation intents.
- Offline/cache policy, cache cleanup, pending sync/cache state, safe confirmations, and storage pressure.
- Stream quality, transcoding capability/policy, network quality policy, and offline quality policy.
- Real Android media controls, lock-screen controls, notification controls, Bluetooth/headset events, Android Auto, foreground service, and widgets as future Android/platform work.
- Gapless, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, and output/device capability state.
- Profiles, preferences, backup/restore for Aria config/state.
- Smart playlists, smart mixes, saved filters, and rule-based playlist planning.
- State snapshots, API snapshot behavior, and fake end-to-end flows.
- Provider extension readiness through generic provider/source abstractions and provider capability models.

## Boundary Clarifications

- Stream quality/transcoding means policy and capability first, not a real transcoder.
- Bit-perfect means capability/readiness/intention first, not low-level audio implementation.
- Renderer selection means intent/boundary first, not a real renderer.
- Backup/restore means Aria config/state first, not destructive music library mutation.
- Provider extension readiness does not mean real multi-provider support through current Anchor. Current Anchor-backed integration remains Navidrome-focused; future additional providers depend on public boundaries/adapters exposed by Anchor or another approved integration layer.
- Automation intents are public/core intents, not UI automation scripts.

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
7. Future additional providers come through public boundaries/adapters exposed by Anchor or another approved integration layer, not direct provider internals.
8. Android app/UI remains separate and consumes Aria Core.
9. Repository hygiene and scope boundaries must be preserved.
