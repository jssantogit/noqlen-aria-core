# Project Context

Noqlen Aria Core is the app/interface orchestration core in the Noqlen ecosystem.

Aria Core is the product. Aria Workflow is the development method and is not the product.

Strategic position:

`Flux -> Forge -> Anchor -> Aria`

Expected future flow:

`Future UI/App -> Aria Core -> Anchor Client -> Anchor Core API -> Navidrome`

## Non-Goals

Bloco 0 does not implement Android UI, Android SDK code, screens, navigation, player UI, playback engine, queue behavior, now playing behavior, offline/cache behavior, Android media controls, Android Auto, real Anchor integration, direct Navidrome calls, or real music-library access.

## Future Product Context

These directions are planning context only and are not Bloco 0 implementation scope:

- Anchor control, status, and diagnostics.
- Library navigation and search.
- Queues.
- Now playing.
- Playback refinement.
- Future cache/offline behavior.
- Android media controls as a future boundary.
- Android Auto as a future boundary.
- Permissions and storage UX as a future boundary.

Each direction requires a spec before implementation. They must remain behind Aria Core boundaries. UI must stay thin. Aria must not bypass Anchor.

## Android Music Player Reference Analysis

These references are product inspiration only, not permission to implement UI or playback in Bloco 0.

- Poweramp: audio polish, customization, EQ/DSP. Lesson: advanced audio capabilities may matter later. Bloco 0 boundary: do not implement EQ/DSP/audio engine.
- Musicolet: local/offline UX and queues. Lesson: queue and offline UX matter. Bloco 0 boundary: do not implement queues or offline behavior.
- Symfonium: server-client model, cache/offline, mature Android UX. Lesson: Anchor integration should be client/adapter-based. Bloco 0 boundary: do not call Navidrome directly and do not implement cache.
- Plexamp: now playing polish, gapless, loudness, pre-cache. Lesson: polished playback state matters later. Bloco 0 boundary: do not implement now playing/playback/pre-cache.
- VLC: robustness and compatibility. Lesson: robust failure handling matters. Bloco 0 boundary: do not expand into codecs/video/broad playback.
- AIMP, foobar2000, Neutron: playlists, ReplayGain, hi-res, DSP. Lesson: audio capability vocabulary may matter later. Bloco 0 boundary: do not implement ReplayGain/hi-res/DSP.
