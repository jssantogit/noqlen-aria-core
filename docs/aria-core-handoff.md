# Noqlen Aria Core Handoff

## Status

- Bloco 0 is complete.
- Bloco 1 is complete.
- Bloco 1 ControlClient refinement is complete.
- Bloco 2 is complete.
- Bloco 3 is complete.
- Bloco 4 Android/player boundary contracts are complete.
- Bloco 5 minimal UI shell planning artifacts are complete.
- Bloco 6 Aria MVP hardening is complete.
- Bloco 7 Aria Core Release Preparation is complete. Release artifacts are documented under `docs/release-checklist.md`, `docs/release-notes.md`, `docs/api-surface.md`, `docs/safety-summary.md`, and `docs/post-core-backlog.md`.
- Aria Workflow vNext context compression is active for future tasks. Start with `aria/context/current.md`, `aria/context/delta.md`, and `aria/context/context-packages.md` before escalating to this full handoff.
- This document is the canonical local repository handoff and source of truth for the current Aria direction.
- The next product step is final release audit and tag decision. Do not create a release tag or publish until the release checklist passes and the maintainer approves.

## Product Definition

Noqlen Aria Core is the modular core of a music player.

Aria must model and orchestrate:

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
- stream quality/transcoding policy;
- output/renderers/audio capabilities;
- playback transition/loudness policies;
- Android media boundaries;
- backup/restore;
- profiles/preferences;
- automation intents;
- state snapshots;
- safe errors/warnings.

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

## Anchor Position

- Anchor is not the center of Aria.
- Anchor is a `ControlClient` adapter/control-plane backend.
- Aria must depend on contracts, not Anchor internals.
- Aria must not call Anchor provider internals.
- Aria must not use Anchor CLI as an integration API.
- Aria must not call Navidrome directly through provider internals.
- Future provider/media support should be capability-driven and adapter-based.

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

### Fase 1 — Base / Control Plane

- Bloco 0 — Bootstrap / Workflow
- Bloco 1 — Core Contracts
- Bloco 2 — Control Services Fake-First
- Bloco 3 — Anchor Adapter Dry-Run
- Bloco 1–3 Audit

### Fase 2 — Android Boundaries / UI Planning / MVP Hardening

- Bloco 4 — Android/player boundary contracts
- Bloco 5 — Minimal UI shell planning artifacts
- Bloco 6 — Aria MVP hardening
- Bloco 4–6 Audit

### Fase 3 — Library / Search / Playlists

- Bloco 7 — Library Browse/Search
- Bloco 8 — User Library States
- Bloco 9 — Playlists / Smart Playlists
- Bloco 7–9 Audit

### Fase 4 — Queue / Now Playing / Playback Intents

- Bloco 10 — Multiple Queues
- Bloco 11 — Now Playing / Playback Intents
- Bloco 12 — Playback Availability
- Bloco 10–12 Audit

### Fase 5 — Offline / Stream Quality / Output

- Bloco 13 — Offline / Cache / Download Policy
- Bloco 14 — Stream Quality / Transcoding
- Bloco 15 — Output / Renderers / Audio Capabilities
- Bloco 13–15 Audit

### Fase 6 — Playback Policies / Android Boundaries / Backup

- Bloco 16 — Transitions / Loudness Policies
- Bloco 17 — Android Media Boundaries
- Bloco 18 — Backup / Restore / Profiles / Preferences
- Bloco 16–18 Audit

### Fase 7 — API / Snapshot / Release

- Bloco 19 — Public API / Automation Intents
- Bloco 20 — State Snapshots / API Hardening
- Bloco 21 — End-to-End Fake Flows / Release Prep
- Bloco 19–21 Final Audit

## Block Summaries

Bloco 0 establishes repository bootstrap and Aria Workflow, including context, review templates, docs, minimal package structure, CLI doctor, validation posture, and repository hygiene.

Bloco 1 defines core contracts and safe result/state primitives, including `ControlClient`, `FakeControlClient`, safe errors/warnings, view states, lifecycle intents, permission/storage abstractions, and fake-first testing boundaries.

Bloco 2 builds fake-first control services over `ControlClient`, including status, diagnostics, readiness, lifecycle preview, result mapping, failure injection, and safe orchestration behavior without real backends.

Bloco 3 adds the dry-run Anchor adapter for the control plane, mapping Anchor-style results into Aria contracts while blocking apply-mode behavior and avoiding Anchor internals, Anchor CLI integration, Navidrome direct calls, Android, playback, queue, and cache code.

Bloco 4 defines Android/player boundary contracts as abstract vocabulary only, including playback, MediaSession, storage, Android Auto, foreground service, lifecycle, notification, lock-screen, and headset bridge protocols plus deterministic fakes.

Bloco 5 defines minimal UI shell planning artifacts for a future thin adapter over Aria Core. It is documentation only and does not implement UI, navigation, playback, queue, now playing, cache, Android SDK, or provider integration.

Bloco 6 hardens the MVP surface with intentional exports, safe serialization/sanitization helpers, optional Anchor absence behavior, dry-run/apply safety tests, documentation consistency, and audit readiness.

Bloco 7 implements Aria Core Release Preparation: release checklist, release notes, public API surface summary, safety summary, post-core backlog, handoff update, and README refresh.

Bloco 8 defines user library states including recently added, recently played, favorites, play count, last played, resume points, unavailable/missing media, and health badges.

Bloco 9 defines playlists, playlist items, playlist availability, smart playlist rules, saved filters, and smart mixes.

Bloco 10 defines multiple queues, active queue selection, queue history, add/remove/move/clear operations, play next, replace queue, and repeat/shuffle per queue.

Bloco 11 defines `NowPlayingState`, current track summary, playback position, playback intents, and commands such as play, pause, skip, seek, and play item.

Bloco 12 defines `PlaybackAvailabilityState`, unavailable reasons, source unavailable, stream unavailable, permission denied, unsupported format, and provider errors.

Bloco 13 defines offline inventory, download queue state, offline rules, automatic offline rules, playback cache, permanent cache, rolling cache, provider offline cache, and storage-pressure policy without destructive cache/download implementation.

Bloco 14 defines stream quality policy, original quality, max bitrate, transcoding capability, network quality policy, and offline quality policy.

Bloco 15 defines playback renderer, output routes, USB DAC, Bluetooth, remote route, high-res, bit-perfect capability, sample rate, bit depth, DSD/MQA capability metadata, and processing bypass state without real driver implementation.

Bloco 16 defines fade, crossfade, smart fade, gapless, ReplayGain/loudness, and conflicts with bit-perfect output without implementing EQ/DSP.

Bloco 17 defines the Android media boundary for MediaSession, notification controls, lock-screen controls, Bluetooth/headset events, Android Auto browse model, foreground service intent, and widget boundary without Android SDK implementation.

Bloco 18 defines backup manifest, restore plan, encrypted backup requirement, provider-bound backup data, application profiles, and preferences.

Bloco 19 defines core automation intents for sync, playback commands, start media, settings, queue load, backup, cache cleanup, provider connection, and renderer selection.

Bloco 20 defines `AriaStateSnapshot`, safe serialization, compatibility rules, public API surface, and stable exports.

Bloco 21 defines the full fake flow from provider to sync to library to queue to now playing to cache/output/diagnostics/backup, plus release preparation and final hardening.

## Safety Rules

- Fake-first development.
- Dedicated spec before each non-trivial product implementation.
- No Android UI, Android app shell, Compose, Activity/Fragment, Android SDK, Kotlin, Java, or Gradle code in the current Python core.
- No Media3/ExoPlayer, real playback engine, real MediaSession, real Android Auto, real audio driver, bit-perfect driver, DSP/EQ, queue engine, or destructive cache/download implementation without explicit future scope.
- No real provider integration, provider hard coupling, Anchor internals, Anchor CLI integration API, direct Navidrome calls, real music library mutation, secrets, raw logs, or personal paths.
- No broad git add; commit only allowlisted files.

## Current Next Step

Bloco 7 Aria Core Release Preparation is complete. Final release audit and tag decision are next. Do not create a release tag or publish until the release checklist passes and the maintainer approves.
