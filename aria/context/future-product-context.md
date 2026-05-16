# Future Product Context

This file records future music-player-core product planning context only. The canonical roadmap and block summaries live in `docs/aria-core-handoff.md`.

Planned product areas:

- Control plane.
- Media providers and provider capability matrix.
- Media sources and source capabilities.
- Sync.
- Library browse/search.
- User library states.
- Playlists and smart playlists.
- Multiple queues.
- Now playing and playback intents.
- Playback availability.
- Offline/cache/download policy.
- Stream quality/transcoding policy.
- Output/renderers/audio capabilities.
- Playback transition/loudness policies.
- Android media boundaries.
- Backup/restore.
- Profiles/preferences.
- Automation intents.
- State snapshots and safe serialization.

These notes are not permission to implement UI, Android SDK code, playback, queues, now playing, cache/offline/download, MediaSession, Android Auto, DSP/EQ, provider integration, or storage/permission UX. Each feature family requires its own spec before implementation.

Current next step: formal audit for Blocos 1-3. Do not start Bloco 4 until that audit passes.
