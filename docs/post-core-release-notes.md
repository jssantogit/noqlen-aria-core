# Post-core Release Notes

Bloco 24 prepares release notes for the post-core foundation after Aria Core MVP `v0.1.0`. These notes are release-prep inputs only. No post-core tag exists yet, and no package has been published by this task.

## What Changed After v0.1.0

Post-core work expanded Aria Core from MVP control-plane contracts into a broader music-player core foundation. The implemented work is still core Python contracts, state models, policy services, deterministic fakes, and documentation. It is not a real Android app, real player, provider integration, or audio driver.

## Implemented Post-core Foundation Groups

- Media source foundation: source identity, abstract media IDs, source capabilities, stream handles, `MediaSourceClient`, `FakeMediaSourceClient`, and safe source results.
- Library browse/search: artists, albums, tracks, playlists, genres, safe folder metadata, browse requests/results, search queries/results, and deterministic services.
- Filters/activity/favorites: library filters, sort options, recently added, recently played, favorites read state, readiness badges, and health badges.
- Queue: queue IDs/items/state, repeat and shuffle state, queue operation intents/results, queue collection state, deterministic `QueueService`, and fake queue scenarios.
- Now playing: current item state, playback availability vocabulary, position snapshots, resumable state, unavailable media state, deterministic `NowPlayingService`, and fake scenarios.
- Playback/renderer/automation intents: playback command intents, seek/skip targets, command previews/results, renderer selection state/results, automation intent vocabulary, and deterministic intent services.
- Offline/cache/storage policy: offline availability, cache policy, cache eligibility, cache operation previews/results, pending operations, storage budgets/pressure, cache cleanup previews, and confirmation/blocking states.
- Internet radio foundation: radio station identity/reference models, directory/import/manual station concepts, stream handle abstraction, metadata/artwork/favorite/read state, availability, validation, and fake scenarios.
- Stream quality/transcoding/network policy: quality preferences/profiles/decisions, bitrate and bandwidth budgets, fallback policy, transcoding capability/policy/decisions, network condition snapshots, and network policy decisions.
- Playback capability models: gapless, loudness/ReplayGain, crossfade, fade, bit-perfect, USB DAC, exclusive output, route/device readiness, sample-rate support, bit-depth support, format support, playback quality preferences, and fake capability scenarios.
- Fade capability follow-up: fade availability, timing preference, mode, unavailable reasons, and capability integration with playback capability summaries.
- Profiles/preferences/backup/restore: profile state, preference state, in-memory backup bundles, manifests, backup plans/results, restore plans/previews/results, conflicts, safety checks, and local deterministic services.
- Smart playlists: smart playlist definitions, rule groups, operators, sort rules, limits, evaluation context/results, saved filters, smart mixes, previews, and deterministic local services.
- State snapshots/e2e fake flows: sanitized state snapshots, snapshot metadata/sections/redaction, snapshot diff service, fake flow scenarios/steps/traces/results, and deterministic fake flow runner.
- Provider extension readiness: generic provider adapter descriptors, boundary policy, readiness/capability/compatibility/registry state, discovery previews/issues, and deterministic readiness/discovery services. Current Anchor-backed integration remains Navidrome-focused and is not treated as multi-provider.
- Android real integration planning: documentation for future media controls, MediaSession, notifications, lock-screen controls, Bluetooth/headset, Android Auto, foreground service, widgets, permission/storage UX, playback engine adapters, and audio output boundaries.
- Android shell handoff: documentation for a future Android app/UI shell to consume Aria Core without moving heavy logic into UI/platform code.

## Intentionally Not Implemented

- Real Android app.
- Real Android UI, screens, navigation, Compose, Activity, or Fragment code.
- Real player engine.
- Real playback.
- Real streaming.
- Real radio streaming, Shoutcast parsing, HLS parsing, or DASH parsing.
- Real transcoding.
- Real provider integration.
- Provider auth.
- Direct Navidrome, Jellyfin, Emby, Plex, or other provider calls.
- Anchor provider internals or Anchor CLI integration.
- Real audio driver.
- Real bit-perfect output.
- Real custom/exclusive USB output.
- Media3/ExoPlayer implementation.
- MediaSession implementation.
- Android Auto implementation.
- Notification, lock-screen, Bluetooth/headset, foreground service, or widget implementation.
- UI implementation.
- Real cache/download mutation, destructive cleanup, filesystem traversal, or device storage inspection.
- Package publish.
- Post-core release tag.

## Known Limitations

See `docs/post-core-known-limitations.md` for the detailed limitation list. In short, Aria Core currently models app/player-facing readiness, capabilities, states, policies, services, fakes, and handoffs. Platform, provider, playback, Android, and audio-driver implementation remains future work outside this release-prep block.

## Next Phase

The next gate is the Final Post-core/Core Audit. The audit must verify Blocos 18-24, deferred audit inputs, public API summary, safety claims, validation evidence, and repository hygiene before any tag or publish decision.

After final audit passes, maintainers may decide whether to create a post-core release tag. Package publishing remains a separate explicit approval.
