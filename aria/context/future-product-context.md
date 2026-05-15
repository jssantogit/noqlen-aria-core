# Future Product Context

This file records future app/player-facing product planning context only.

These are not Bloco 0 implementation scope:

- Anchor control/status/diagnostics.
- Library navigation and search.
- Queues.
- Now playing.
- Playback refinement.
- Future cache/offline behavior.
- Android media controls as a future boundary.
- Android Auto as a future boundary.
- Permissions/storage UX as a future boundary.

These notes are not permission to implement UI, playback, queue, now playing, cache/offline, MediaSession, Android Auto, or storage/permission UX during Bloco 1. Each feature family requires its own spec before implementation. Aria must not bypass Anchor. Future UI must remain thin.

## Future Architecture Vocabulary

These are future architectural boundary names only:

- `PlaybackEngine`
- `MediaSessionBridge`
- `AndroidStorageBridge`
- `QueueService`
- `LibraryPresentationService`
- `OfflineCachePolicyService`
- `AudioCapabilitiesService`

They are not Bloco 0 implementation targets. They must not appear as source code classes or services yet.
