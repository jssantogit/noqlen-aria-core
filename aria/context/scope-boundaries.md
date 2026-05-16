# Scope Boundaries

This file is the canonical permanent scope boundary for Aria Core.

- Aria Core is the modular app/player-facing core of a music player.
- Aria Core is not UI.
- Aria Core is not an Android app shell.
- Future UI must be a thin adapter over Aria Core.
- Do not implement Android UI, Compose, Activity/Fragment, Android SDK, Kotlin, Java, Gradle, screens, navigation, or player UI without explicit future scope.
- Do not implement Media3/ExoPlayer, a real playback engine, a real audio driver, bit-perfect driver behavior, real MediaSession, real Android Auto, or DSP/EQ without a dedicated spec.
- Do not implement destructive cache/download behavior, offline mutation, playback cache, queue engine, now playing engine, or storage/permission UX without a dedicated spec.
- Do not implement provider hard coupling or real provider integration without a dedicated spec.
- Do not call Navidrome directly.
- Do not call Anchor provider internals.
- Do not use Anchor CLI as the integration layer.
- Do not touch a real music library.
- Do not run real Navidrome without an explicit block/spec.
- Product behavior requires a spec and explicit block scope.
- Blocos 0-7 are the Aria Core MVP and are complete. Blocos 8-20 are post-core feature expansion. Final release audit and tag decision are next. Do not start post-core features without a dedicated spec.
