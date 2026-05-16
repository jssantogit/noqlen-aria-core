# Post-Core Backlog

Aria Core MVP is Blocos 0-7 and local tag `v0.1.0` exists. The following features are planned post-core work after `v0.1.0` and are not implemented in the MVP. Every future feature requires a dedicated spec before implementation.

## Final Post-Core Roadmap

The roadmap in `docs/aria-core-handoff.md` defines Aria Core MVP as Blocos 0-7. The following Blocos 8-24 are post-core feature expansion and are not implemented in the MVP.

| Bloco | Feature | Status |
|-------|---------|--------|
| 8 | Media Source Foundation: `MediaSourceClient`, `FakeMediaSourceClient`, source capabilities, abstract stream handle, and base for provider-backed sources via Anchor | Implemented and audited |
| 9 | Library Browse/Search: artists, albums, songs, safe folders, playlists, genres, and browse/search | Implemented and audited |
| 10 | Library Filters, Activity and Favorites: filters, sorting, recently added, recently played, favorites, and library readiness/health badges | Implemented and audited |
| Audit 8-10 | Media Source/Library Audit | Complete |
| 11 | Queue Foundation: `QueueState`, `QueueService`, repeat/shuffle, predictable queue behavior, and multiple queues explicitly as a supported contract direction | Implemented and audited |
| 12 | Now Playing Foundation: `NowPlayingState`, current track summary, playback availability, resumable state, and unavailable media state | Implemented and audited |
| 13 | Playback, Renderer and Automation Intents: play/pause/skip/seek intents, renderer selection intents, public automation intents, and blocked/unavailable playback handling | Implemented and audited |
| Audit 11-13 | Queue/Now Playing/Intents Audit | Complete |
| 14 | Offline, Cache and Storage Policy: offline availability, cache policy, cache cleanup, storage pressure, pending sync/cache states, and safe confirmation states | Implemented and audited |
| 15 | Internet Radio Foundation: radio station identity/reference models, RadioStationSummary, radio directory/import/manual station concepts, radio stream handle abstraction, radio source capability, radio playback availability, ICY/live metadata state, station artwork/thumbnail metadata if provided, radio favorites/read state, safe unavailable/degraded radio behavior, no real streaming, no real player, no HLS/DASH/Shoutcast client implementation, no provider direct integration | Implemented and audited |
| 16 | Stream Quality, Transcoding and Network Policy: stream quality policy, transcoding capability/policy, network quality policy, and offline quality policy | Implemented and audited |
| 17 | Playback Capability Models: gapless capability, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, USB DAC capability, exclusive output capability, audio output route state, sample-rate support, bit-depth support, output/device readiness, playback quality preferences, and driver bridge vocabulary for a future Android player | Implemented and audited |
| Audit 14-17 | Offline/Radio/Quality/Capabilities Audit | Complete |
| 18 | Profiles, Preferences, Backup and Restore: user profiles, preferences, backup/restore for Aria config/state, and no destructive real music library mutation | Implemented |
| 19 | Smart Playlists: smart playlists, smart mixes, saved filters, and rule-based playlists inspired by Symfonium | Implemented |
| 20 | State Snapshots and End-to-End Fake Flows: state snapshots, API snapshot behavior, and fake source -> library -> queue -> now playing intent -> diagnostics flows | Implemented |
| Audit 18-20 | Profiles/Smart/Snapshots Audit | Deferred to final post-core/core audit |
| 21 | Provider Extension Readiness: generic provider/source abstractions, no direct Jellyfin/Emby/Navidrome integrations, no assumption that Anchor already supports multiple providers, and future providers through public boundaries/adapters exposed by Anchor or another approved integration layer | Implemented |
| 22 | Android Real Integration Planning: real media controls, lock-screen controls, notification controls, Bluetooth/headset, Android Auto, foreground service, and widgets planning | Planning complete |
| 23 | Android Shell Handoff: handoff for future Android app/UI; UI consumes Aria Core and does not own heavy logic | Not started |
| Audit 21-23 | Providers/Android Handoff Audit | Deferred to final post-core/core audit unless explicitly requested |
| 24 | Post-core Release Prep: checklist, release notes, backlog update, docs, handoff, and release preparation for the post-core phase | Not started |

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
- Internet radio station identity, stream handles, ICY/live metadata, radio favorites, and safe unavailable/degraded radio behavior.
- Real Android media controls, lock-screen controls, notification controls, Bluetooth/headset events, Android Auto, foreground service, and widgets as future Android/platform work.
- Gapless, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, USB DAC capability, exclusive output capability, audio output route state, sample-rate support, bit-depth support, output/device readiness, playback quality preferences, and driver bridge vocabulary for a future Android player.
- Profiles, preferences, backup/restore for Aria config/state.
- Smart playlists, smart mixes, saved filters, and rule-based playlist planning.
- State snapshots, API snapshot behavior, and fake end-to-end flows.
- Provider extension readiness through generic provider/source abstractions and provider capability models.

## Boundary Clarifications

- Stream quality/transcoding means policy and capability first, not a real transcoder.
- Bit-perfect means capability/readiness/intention first, not low-level audio implementation.
- USB DAC capability means modeling readiness/capability state and future driver bridge vocabulary, not a real USB driver or Android USB Host API.
- Exclusive output capability means modeling intent/readiness state for a future custom audio output layer, not a real exclusive audio driver.
- Renderer selection means intent/boundary first, not a real renderer.
- Backup/restore means Aria config/state first, not destructive music library mutation.
- Provider extension readiness does not mean real multi-provider support through current Anchor. Current Anchor-backed integration remains Navidrome-focused; future additional providers depend on public boundaries/adapters exposed by Anchor or another approved integration layer.
- Automation intents are public/core intents, not UI automation scripts.
- Internet radio means modeling station identity, stream handles, metadata, availability, and favorites/read state. It does not mean real streaming, a real player, Shoutcast/HLS/DASH parsing, or provider direct integration.
- Aria Core may model requirements for a future custom/exclusive audio output layer.
- Aria Core must not implement an audio driver.
- A future Android Player phase may research or implement an exclusive USB/audio output bridge if feasible.
- Bloco 22 planning for real Android integration lives in `docs/android-real-integration-plan.md`. It is documentation only; Android app/platform code still requires future dedicated specs.

## Still Out of Scope Without Future Specs

- Real Anchor apply-mode integration.
- Direct provider integrations or provider internals.
- Real radio playback, streaming clients, Shoutcast/HLS/DASH parsing, or radio provider direct integration.
- `PlaybackEngine` real audio engine implementation.
- Real output/renderer/audio driver implementation.
- DSP/EQ audio processing.
- Real bit-perfect audio driver behavior.
- Real sample-rate switching or real DAC control.
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

## Future Android Player Audio Output Phase (Outside Aria Core)

The following phases are not part of Aria Core. They represent a future Android Player project that may consume Aria Core and research or implement an exclusive USB/audio output bridge if feasible. No Aria Core block implements these.

- **Future Android Player Phase A — Audio Output Research:** survey Android audio output APIs (AAudio, Oboe), USB DAC accessibility, exclusive mode feasibility, and sample-rate/bit-depth negotiation on target Android versions. No implementation.
- **Future Android Player Phase B — Playback Engine Adapter:** design and prototype a playback engine adapter that can route Aria Core playback intents to a real audio output layer. Keep Aria Core contracts stable; adapter lives in the Android Player.
- **Future Android Player Phase C — Exclusive USB Output Prototype:** prototype exclusive USB audio output for a targeted set of USB DACs. Validate stability, latency, and sample-rate switching. Prototype only; not production.
- **Future Android Player Phase D — Bit-perfect Validation:** validate that the prototype achieves bit-perfect or bit-transparent output under test conditions. Document limitations and device-specific behavior.
- **Future Android Player Phase E — Production Audio Driver/Bridge Decision:** decide whether to build a production audio driver/bridge, adopt an existing solution, or keep the playback engine adapter as a stable boundary without a custom driver. Aria Core remains driver-free regardless of this decision.
