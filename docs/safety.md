# Safety

Current safety boundaries:

- No real music libraries are read or modified.
- No Navidrome process is started or called.
- No direct Navidrome calls are implemented.
- No Anchor internals are imported or called.
- No Anchor CLI is used as an integration layer.
- No Android SDK, Kotlin, Java, Gradle, UI, navigation, player UI, media controls, or Android Auto code is added.
- No Media3/ExoPlayer, playback engine, queue behavior, now playing behavior, destructive cache/download behavior, offline mutation, MediaSession, real audio driver, bit-perfect driver, or DSP/EQ is implemented without explicit future scope.
- Aria Core may model requirements for a future custom/exclusive audio output layer.
- Aria Core must not implement an audio driver.
- A future Android Player phase may research or implement an exclusive USB/audio output bridge if feasible.
- No provider hard coupling or real provider integration is added without a dedicated spec.
- No secrets, credentials, logs, local configs, or workflow artifacts are committed.
- App-facing errors, warnings, and serialized output must be sanitized before display. Raw exceptions, stack traces, credentials, local paths, provider internals, and personal library details must not be exposed.
- Anchor remains optional. If optional Anchor dependencies are missing, Aria returns safe degraded/error results instead of raw import failures.

Tests must remain local, offline, fake-first, and safe.
