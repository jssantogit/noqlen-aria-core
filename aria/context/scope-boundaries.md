# Scope Boundaries

This file is the canonical permanent scope boundary for Aria Core.

- Aria Core is not UI.
- Aria Core is not an Android app.
- Aria Core is an app/player-facing orchestration core.
- Future UI must be a thin adapter over Aria Core.
- Early blocks must not implement Android SDK, UI, screens, navigation, or player UI.
- Do not implement playback, queues, now playing, cache/offline, Android Auto, or MediaSession without a dedicated spec.
- During Bloco 1, do not implement playback, UI, Android SDK, cache/offline, queues, now playing, MediaSession, Android Auto, or storage/permission UX.
- Do not call Navidrome directly.
- Do not call Anchor provider internals.
- Do not use Anchor CLI as the integration layer.
- Do not touch a real music library.
- Do not run real Navidrome without an explicit block/spec.
- Do not implement Bloco 1 contracts during workflow-only tasks.
- Product behavior requires a spec and explicit block scope.
