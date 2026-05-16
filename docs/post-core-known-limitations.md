# Post-core Known Limitations

These limitations are intentional at Bloco 24 release-prep time.

## Release Status

- Final Post-core/Core Audit has not been run by Bloco 24.
- No post-core release tag exists yet.
- No package publish has been attempted.
- `v0.1.0` remains the local MVP tag.

## Android And UI

- No Android app exists.
- No Android SDK, Kotlin, Java, Gradle, Compose, Activity, Fragment, screens, navigation, or app shell code exists.
- Android real integration planning and Android shell handoff are documentation only.
- UI implementation remains future work.

## Playback And Audio

- No real playback engine exists.
- No Media3/ExoPlayer implementation exists.
- No MediaSession implementation exists.
- No Android Auto implementation exists.
- No notification, lock-screen, Bluetooth/headset, foreground service, or widget implementation exists.
- No audio driver exists.
- No bit-perfect output path exists.
- No custom/exclusive USB output exists.
- No JNI/NDK/AAudio/Oboe bridge exists.
- Playback capability models describe readiness/capability/preferences only.

## Providers, Network, And Streaming

- No real provider integration exists.
- No provider auth exists.
- Current Anchor-backed integration remains Navidrome-focused and is not multi-provider.
- No direct Navidrome, Jellyfin, Emby, Plex, or other provider calls exist.
- No real streaming exists.
- No real radio streaming exists.
- No Shoutcast/HLS/DASH client or parser exists.
- No network probing exists.
- No real transcoding exists.

## Storage, Cache, Backup, And Restore

- No real music library access exists.
- No filesystem traversal exists.
- No device storage inspection exists.
- No real download/cache write/delete behavior exists.
- No destructive cache cleanup exists.
- Backup/restore remains structured, in-memory, local state modeling with preview-first restore results.

## Product Maturity

- Services are deterministic and fake/local-first.
- The CLI remains a minimal smoke/doctor entry point.
- Future provider/player/platform adapters require dedicated specs, implementation, and tests.
- Final audit must verify docs, API surface, safety, tests, repository hygiene, and release readiness before tag decisions.
