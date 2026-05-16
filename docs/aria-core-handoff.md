# Noqlen Aria Core Handoff

## Status

- Bloco 0 is complete.
- Bloco 1 is complete.
- Bloco 1.5 ControlClient refinement is complete.
- Bloco 2 is complete.
- Bloco 3 is complete.
- Bloco 4 Android/player boundary contracts are complete.
- Bloco 5 minimal UI shell planning artifacts are complete.
- Bloco 6 Aria MVP hardening is complete.
- Bloco 7 Aria Core Release Preparation is complete. Release artifacts are documented under `docs/release-checklist.md`, `docs/release-notes.md`, `docs/api-surface.md`, `docs/safety-summary.md`, and `docs/post-core-backlog.md`.
- Aria Core MVP scope is Blocos 0-7. Local tag `v0.1.0` exists and marks the MVP tag as complete.
- Post-core feature expansion starts after `v0.1.0` and is tracked as Blocos 8-24.
- Advanced library/player features are post-core backlog, not MVP blockers.
- Aria Workflow vNext context compression is active for future tasks. Start with `aria/context/current.md`, `aria/context/delta.md`, and `aria/context/context-packages.md` before escalating to this full handoff.
- This document is the canonical local repository handoff and source of truth for the current Aria direction.
- Blocos 8-13 are implemented and audited. Audit 8-13 is complete.
- Blocos 14-17 are implemented and audited. Audit 14-17 is complete. Do not start Bloco 18 or publish without dedicated scope.

## Product Definition

Noqlen Aria Core is the modular core of a music player.

Aria Core MVP models and orchestrates control-plane contracts, fake-first services, Android/player boundary vocabulary, UI shell planning boundaries, safe serialization, release artifacts, and safety documentation.

Post-core Aria work will expand the core to model and orchestrate:

- control plane;
- media providers;
- media sources;
- sync;
- library browse/search;
- user library states;
- playlists;
- smart playlists;
- multiple queues;
- now playing;
- playback intents;
- playback availability;
- offline/cache/download policy;
- internet radio station/stream metadata;
- stream quality/transcoding policy;
- output/renderers/audio capabilities;
- playback transition/loudness policies;
- Android media boundaries;
- backup/restore;
- profiles/preferences;
- automation intents;
- state snapshots;
- safe errors/warnings.

Android real integration and the Android app/UI shell remain separate from Aria Core. They consume Aria Core through contracts and future adapters; they are not implemented in the MVP.

Aria is:

- contracts;
- states;
- services;
- policies;
- capabilities;
- fakes;
- mappers;
- adapters;
- snapshots;
- safe serialization;
- tests.

Aria must not implement now:

- Android UI;
- Compose;
- Activity/Fragment;
- Android SDK code;
- Media3/ExoPlayer;
- real playback engine;
- real MediaSession;
- real Android Auto;
- real destructive cache/download;
- real audio driver;
- bit-perfect driver;
- DSP/EQ;
- provider-specific hard coupling.

Aria Workflow is the development method. Aria Core is the product.

## Architecture Model

Aria Core is organized around these layers:

- Public API / Snapshot Layer: stable exports, automation intents, safe serialization, compatibility, and `AriaStateSnapshot`.
- Control Plane: status, diagnostics, readiness, lifecycle preview, and control-plane capabilities.
- Media Provider Layer: provider identity, accounts, connection/auth state, capabilities, and registry.
- Media Source Layer: source clients, normalized IDs, metadata, stream handles, and source capabilities.
- Library Layer: browse, search, filters, sorting, pagination, and normalized library views.
- Sync Layer: full/incremental sync orchestration, summaries, imported/scanned counts, and safe sync errors.
- Playlist / Smart Playlist Layer: playlists, playlist items, smart rules, saved filters, and mixes.
- Queue / Now Playing Layer: multiple queues, active queue state, now playing state, position, and playback intents.
- Offline / Cache / Download Policy Layer: offline inventory, download queue state, cache policy, and storage-pressure behavior.
- Internet Radio / Live Stream Layer: radio station identity, stream handles, live metadata, availability, and safe degraded states.
- Stream Quality / Transcoding Layer: original/max bitrate policy, provider transcoding capability, network policy, and offline quality policy.
- Output / Renderer / Audio Capability Layer: renderers, output routes, route state, format capability metadata, and diagnostics.
- Playback Policy Layer: transitions, gapless/crossfade/fade, ReplayGain/loudness, and bit-perfect conflicts without EQ/DSP.
- Android Boundary Layer: MediaSession, notification controls, lock-screen controls, Android Auto browse model, foreground service intent, widget boundary, and headset/Bluetooth events as boundaries.
- Backup / Profiles / Preferences Layer: backup manifest, restore plan, encrypted-backup requirements, provider-bound backup data, profiles, and preferences.

### Boundary Roles

`ControlClient` represents control-plane behavior: status, diagnostics, readiness, lifecycle preview, and control-plane capability. It is not a media library, provider, playback engine, or Android API.

`MediaSourceClient` is a future media-source boundary for library browse/search, playlists, metadata, stream handles, normalized IDs, and source capabilities. Fake source clients must come before real integrations.

`PlaybackRenderer` and `OutputRoute` are future output boundaries for phone output, USB DAC, Bluetooth, remote renderer, and route/capability state. They model renderer availability and capabilities; they do not implement real audio drivers.

`PlaybackEngine` is a future real audio engine boundary. It is not part of the current core implementation and must not be implemented without a dedicated spec.

Android app/UI remains separate. Future Android real integration, app shell, media controls, notification/lock-screen controls, Bluetooth/headset handling, Android Auto, widgets, and foreground service wiring must be planned and implemented outside the core MVP through future dedicated specs.

## Anchor Position

- Anchor is not the center of Aria.
- Anchor is a `ControlClient` adapter/control-plane backend.
- Aria must depend on contracts, not Anchor internals.
- Aria must not call Anchor provider internals.
- Aria must not use Anchor CLI as an integration API.
- Aria must not call Navidrome directly through provider internals.
- Future provider/media support should be capability-driven and adapter-based.
- Future additional providers depend on public boundaries/adapters exposed by Anchor or another approved integration layer, not direct provider internals. Current Anchor-backed integration remains Navidrome-focused.

Expected adapter direction:

`Future UI/App/Player -> Aria Core -> ControlClient/MediaSourceClient contracts -> adapters -> providers/backends`

## Provider Scope

Provider concepts are future/core-domain concerns for capability-driven normalization:

- local device;
- Navidrome / OpenSubsonic / Subsonic;
- Plex;
- Emby;
- Jellyfin;
- AudioBookShelf;
- Kodi;
- OneDrive;
- Box;
- Google Drive;
- Dropbox;
- future providers through adapters/Anchor.

Provider real integrations are not implemented by this documentation update. Aria should normalize provider differences through provider and source capabilities, and the provider capability matrix matters for every future provider-facing block.

Third-party product and provider names in Aria docs are factual research references only. Noqlen is not affiliated with, endorsed by, sponsored by, or associated with those products or companies. Do not copy logos, screenshots, icons, UI assets, branding, or long text from third-party products. Use generic Aria domain names such as `MediaProviderRegistry`, `SmartPlaylist`, `MultipleQueue`, `OutputProfile`, and `BitPerfectCapability`; do not use brand-based class or feature names.

## Roadmap

### Aria Core MVP

- Bloco 0 — Bootstrap: repository, Aria Workflow, base docs, minimal CLI, hygiene and local handoff.
- Bloco 0 Audit — Bootstrap Audit: initial audit of repository, workflow, docs, CLI, hygiene and scope.
- Bloco 1 — Core Contracts: `AriaResult`, `AriaError`, `AriaWarning`, view states, lifecycle intents, permission/storage and `ControlClient`.
- Bloco 1.5 — ControlClient Refinement: remove Anchor from the conceptual center; `ControlClient` is generic, Anchor is one future adapter.
- Bloco 2 — Fake Control State Mapping: `FakeControlClient`, `StatusService`, `DiagnosticsService`, `ReadinessService`, `LifecycleIntentService` and `ResultMappingService`.
- Bloco 3 — Anchor Dry-Run Adapter: `AnchorControlClient` using Anchor public API, offline/dry-run only, no real apply and no provider internals.
- Audit 1-3 — Formal Audit: architecture, safety, tests, modularity, Anchor adapter and repository hygiene.
- Bloco 4 — Android/Player Boundary Contracts: abstract contracts for permission/storage, lifecycle, `PlaybackEngine` boundary, `MediaSessionBridge`, `AndroidStorageBridge` and Android Auto boundary.
- Bloco 5 — Minimal UI Shell Planning: plan future UI as a thin adapter over Aria Core, without implementing UI.
- Bloco 6 — MVP Hardening: public API, intentional exports, safe serialization, sanitized errors, docs, tests and safety.
- Audit 4-6 — Formal Audit: Android/player boundaries, UI planning, hardening, docs, tests, scope and safety.
- Bloco 7 — Release Preparation: checklist, release notes, API summary, safety summary, post-core backlog, handoff and version preparation.
- Final Release Audit — Release Gate: final audit before release tag.
- Pre-tag Cleanup — If needed: clean working tree, reconcile docs/workflow and ensure repository is clean.
- Tag v0.1.0 — Aria Core MVP: create the MVP tag only after release gate is green and working tree is clean.

### Post-Core Feature Roadmap

- Bloco 8 — Media Source Foundation: `MediaSourceClient`, `FakeMediaSourceClient`, source capabilities, abstract stream handle and base for provider-backed sources via Anchor.
- Bloco 9 — Library Browse/Search: artists, albums, songs, safe folders, playlists and genres.
- Bloco 10 — Library Filters, Activity and Favorites: filters, sorting, recently added, recently played, favorites and library readiness/health badges.
- Audit 8-10 — Media Source/Library Audit: audit media source and library contracts before queue/now-playing work.
- Bloco 11 — Queue Foundation: `QueueState`, `QueueService`, repeat/shuffle state, predictable queue behavior and multiple queues as a supported contract direction.
- Bloco 12 — Now Playing Foundation: `NowPlayingState`, current track summary, playback availability, resumable state and unavailable media state.
- Bloco 13 — Playback, Renderer and Automation Intents: play/pause/skip/seek intents, renderer selection intents, public automation intents and blocked/unavailable playback handling.
- Audit 11-13 — Queue/Now Playing/Intents Audit: audit queue, now playing, renderer intent and automation intent boundaries.
- Bloco 14 — Offline, Cache and Storage Policy: offline availability, cache policy, cache cleanup, storage pressure, pending sync/cache states and safe confirmation states.
- Bloco 15 — Internet Radio Foundation: radio station identity/reference models, `RadioStationSummary`, radio directory/import/manual station concepts, radio stream handle abstraction, radio source capability, radio playback availability, ICY/live metadata state, station artwork/thumbnail metadata if provided, radio favorites/read state, safe unavailable/degraded radio behavior, no real streaming, no real player, no HLS/DASH/Shoutcast client implementation, and no provider direct integration.
- Bloco 16 — Stream Quality, Transcoding and Network Policy: stream quality policy, transcoding capability/policy, network quality policy and offline quality policy.
- Bloco 17 — Playback Capability Models: gapless capability, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, USB DAC capability, exclusive output capability, audio output route state, sample-rate support, bit-depth support, output/device readiness, playback quality preferences, and driver bridge vocabulary for a future Android player.
- Audit 14-17 — Offline/Radio/Quality/Capabilities Audit: audit offline/cache policy, internet radio capability models, quality/transcoding policy and playback capability models.
- Bloco 18 — Profiles, Preferences, Backup and Restore: user profiles, preferences, backup/restore for Aria config/state and no destructive real music library mutation.
- Bloco 19 — Smart Playlists: smart playlists, smart mixes, saved filters and Symfonium-inspired rule-based playlist planning.
- Bloco 20 — State Snapshots and End-to-End Fake Flows: state snapshots, API snapshot behavior and fake source -> library -> queue -> now playing intent -> diagnostics flows.
- Audit 18-20 — Profiles/Smart/Snapshots Audit: audit profiles, preferences, backup/restore, smart playlists, snapshots and fake end-to-end flows.
- Bloco 21 — Provider Extension Readiness: generic provider/source abstractions, no direct Jellyfin/Emby/Navidrome integrations, no assumption that Anchor already supports multiple providers, and future additional providers through public boundaries/adapters exposed by Anchor or another approved integration layer.
- Bloco 22 — Android Real Integration Planning: real media controls, lock-screen controls, notification controls, Bluetooth/headset, Android Auto, foreground service and widgets planning.
- Bloco 23 — Android Shell Handoff: handoff for the future Android app/UI to consume Aria Core without moving heavy logic into the interface.
- Audit 21-23 — Providers/Android Handoff Audit: audit provider boundaries and Android handoff boundaries.
- Bloco 24 — Post-core Release Prep: checklist, release notes, backlog update, docs, handoff and release preparation for the post-core phase.

### Future Android Player Audio Output Phase (Outside Aria Core)

These phases are not part of Aria Core. They represent a future Android Player project that may consume Aria Core and research or implement an exclusive USB/audio output bridge if feasible.

- **Future Android Player Phase A — Audio Output Research:** survey Android audio output APIs (AAudio, Oboe), USB DAC accessibility, exclusive mode feasibility, and sample-rate/bit-depth negotiation on target Android versions. No implementation.
- **Future Android Player Phase B — Playback Engine Adapter:** design and prototype a playback engine adapter that can route Aria Core playback intents to a real audio output layer. Keep Aria Core contracts stable; adapter lives in the Android Player.
- **Future Android Player Phase C — Exclusive USB Output Prototype:** prototype exclusive USB audio output for a targeted set of USB DACs. Validate stability, latency, and sample-rate switching. Prototype only; not production.
- **Future Android Player Phase D — Bit-perfect Validation:** validate that the prototype achieves bit-perfect or bit-transparent output under test conditions. Document limitations and device-specific behavior.
- **Future Android Player Phase E — Production Audio Driver/Bridge Decision:** decide whether to build a production audio driver/bridge, adopt an existing solution, or keep the playback engine adapter as a stable boundary without a custom driver. Aria Core remains driver-free regardless of this decision.

## Block Summaries

Bloco 0 establishes repository bootstrap and Aria Workflow, including context, review templates, docs, minimal package structure, CLI doctor, validation posture, and repository hygiene.

Bloco 1 defines core contracts and safe result/state primitives, including `ControlClient`, `FakeControlClient`, safe errors/warnings, view states, lifecycle intents, permission/storage abstractions, and fake-first testing boundaries.

Bloco 2 builds fake-first control services over `ControlClient`, including status, diagnostics, readiness, lifecycle preview, result mapping, failure injection, and safe orchestration behavior without real backends.

Bloco 3 adds the dry-run Anchor adapter for the control plane, mapping Anchor-style results into Aria contracts while blocking apply-mode behavior and avoiding Anchor internals, Anchor CLI integration, Navidrome direct calls, Android, playback, queue, and cache code.

Bloco 4 defines Android/player boundary contracts as abstract vocabulary only, including playback, MediaSession, storage, Android Auto, foreground service, lifecycle, notification, lock-screen, and headset bridge protocols plus deterministic fakes.

Bloco 5 defines minimal UI shell planning artifacts for a future thin adapter over Aria Core. It is documentation only and does not implement UI, navigation, playback, queue, now playing, cache, Android SDK, or provider integration.

Bloco 6 hardens the MVP surface with intentional exports, safe serialization/sanitization helpers, optional Anchor absence behavior, dry-run/apply safety tests, documentation consistency, and audit readiness.

Bloco 7 implements Aria Core Release Preparation: release checklist, release notes, public API surface summary, safety summary, post-core backlog, handoff update, and README refresh.

Bloco 8 defines media source foundation work, including `MediaSourceClient`, `FakeMediaSourceClient`, source capabilities, abstract stream handles, and conceptual provider support through Anchor boundaries.

Bloco 9 defines library browse/search for artists, albums, songs, safe folders, playlists, genres, and search entry points.

Bloco 10 defines library filters and activity state, including sorting, recently added, recently played, favorites, and library readiness/health badges.

Bloco 11 defines queue foundation, including `QueueState`, `QueueService`, repeat/shuffle state, predictable queue behavior, safe queue errors, and multiple queues as a supported contract direction.

Bloco 12 defines now playing foundation, including `NowPlayingState`, current track summary, playback availability, resumable state, and unavailable media state.

Bloco 13 defines playback, renderer, and automation intents for play, pause, skip, seek, renderer selection, public/core automation, intent validation, and blocked/unavailable playback handling. Automation intents are public core intents, not UI automation scripts. Renderer selection is intent/boundary first, not a real renderer.

Bloco 14 defines offline/cache/storage policy, including offline availability, cache policy, cache cleanup, storage pressure, pending sync/cache states, and safe confirmation states without destructive cache/download implementation.

Bloco 15 defines internet radio foundation work, including radio station identity/reference models, `RadioStationSummary`, radio directory/import/manual station concepts, radio stream handle abstraction, radio source capability, radio playback availability, ICY/live metadata state, station artwork/thumbnail metadata if provided, radio favorites/read state, and safe unavailable/degraded radio behavior. Internet radio is a post-core Aria capability model/service area. Aria may model radio stations, stream handles, metadata, and availability, but must not implement real radio playback, Shoutcast/HLS/DASH parsing, provider direct integration, or a real player. Future Android/player phases may implement actual playback.

Bloco 16 defines stream quality, transcoding, and network policy, including stream quality policy, transcoding capability/policy, network quality policy, and offline quality policy. Transcoding is policy/capability first, not a real transcoder.

Bloco 17 defines playback capability models, including gapless capability, loudness/ReplayGain awareness, crossfade capability, bit-perfect capability, USB DAC capability, exclusive output capability, audio output route state, sample-rate support, bit-depth support, output/device readiness, playback quality preferences, and driver bridge vocabulary for a future Android player. Bloco 17 is capability/readiness/preference models only. It must not implement a real audio driver, USB driver, Android USB Host API, JNI/NDK, AAudio/Oboe, Media3/ExoPlayer, real bit-perfect output, real sample-rate switching, real DAC control, or DSP/EQ.

Bloco 18 defines profiles, preferences, backup, and restore for Aria config/state without destructive real music library mutation.

Bloco 19 defines smart playlists, smart mixes, saved filters, and rule-based playlist planning inspired by Symfonium.

Bloco 20 defines state snapshots, API snapshot behavior, and fake end-to-end flows from source to library to queue to now playing intent to diagnostics.

Bloco 21 defines provider extension readiness. Aria prepares generic provider/source abstractions and provider capability models, but does not implement Jellyfin, Emby, Navidrome, or other direct provider integrations. Current Anchor-backed integration remains Navidrome-focused; future additional providers depend on public boundaries/adapters exposed by Anchor or another approved integration layer.

Bloco 22 defines Android real integration planning for media controls, lock-screen controls, notification controls, Bluetooth/headset, Android Auto, foreground service, and widgets without implementing them in Aria Core.

Bloco 23 defines Android shell handoff for the future Android app/UI to consume Aria Core without moving heavy logic into the interface.

Bloco 24 defines post-core release preparation with checklist, release notes, backlog update, docs, handoff, and release preparation for the post-core phase.

## Safety Rules

- Fake-first development.
- Dedicated spec before each non-trivial product implementation.
- No Android UI, Android app shell, Compose, Activity/Fragment, Android SDK, Kotlin, Java, or Gradle code in the current Python core.
- No Media3/ExoPlayer, real playback engine, real MediaSession, real Android Auto, real audio driver, bit-perfect driver, DSP/EQ, queue engine, or destructive cache/download implementation without explicit future scope.
- No real radio playback, Shoutcast/HLS/DASH parsing, or radio provider direct integration without explicit future scope.
- Aria Core may model requirements for a future custom/exclusive audio output layer.
- Aria Core must not implement an audio driver.
- A future Android Player phase may research or implement an exclusive USB/audio output bridge if feasible.
- No real provider integration, provider hard coupling, Anchor internals, Anchor CLI integration API, direct Navidrome calls, real music library mutation, secrets, raw logs, or personal paths.
- No broad git add; commit only allowlisted files.
- Aria Core represents and orchestrates states, intents, policies, and boundaries.
- Aria Core does not become real UI, a real player engine, Media3/ExoPlayer, or Android SDK-coupled code.
- Android app/UI remains separate and consumes Aria Core.

## Current Next Step

Blocos 0-17 are complete. Aria Core MVP (Blocos 0-7) is tagged `v0.1.0`. Post-core media/library/queue/now-playing/playback-intent foundation (Blocos 8-13) is implemented and audited. Offline/radio/quality/playback-capability foundation (Blocos 14-17) is implemented and audited. Do not start Bloco 18 without explicit approval and a dedicated spec.
