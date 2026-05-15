# Safety

Bloco 0 safety boundaries:

- No real music libraries are read or modified.
- No Navidrome process is started or called.
- No direct Navidrome calls are implemented.
- No Anchor internals are imported or called.
- No Anchor CLI is used as an integration layer.
- No Android SDK, Kotlin, Gradle, UI, navigation, player UI, media controls, or Android Auto code is added.
- No playback engine, queue behavior, now playing behavior, cache, or offline behavior is implemented.
- No secrets, credentials, logs, local configs, or workflow artifacts are committed.

Tests must remain local, offline, fake-first, and safe.
