# Safety

Current safety boundaries:

- No real music libraries are read or modified.
- No Navidrome process is started or called.
- No direct Navidrome calls are implemented.
- No Anchor internals are imported or called.
- No Anchor CLI is used as an integration layer.
- No Android SDK, Kotlin, Java, Gradle, UI, navigation, player UI, media controls, or Android Auto code is added.
- No Media3/ExoPlayer, playback engine, queue behavior, now playing behavior, destructive cache/download behavior, offline mutation, MediaSession, real audio driver, bit-perfect driver, or DSP/EQ is implemented without explicit future scope.
- No provider hard coupling or real provider integration is added without a dedicated spec.
- No secrets, credentials, logs, local configs, or workflow artifacts are committed.

Tests must remain local, offline, fake-first, and safe.
