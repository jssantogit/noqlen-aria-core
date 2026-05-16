# Safety Summary

Aria Core MVP safety boundaries, verified at release preparation time. All boundaries hold in the current codebase and test suite (368 tests passing).

## No Real Music-Library Access

- No code reads, writes, lists, or mutates real music files or directories.
- No real music-library paths are hardcoded or configured.
- `FakeControlClient` and deterministic fake classes simulate all music library behavior.

## No Direct Navidrome Calls

- No Navidrome process is started or stopped.
- No Navidrome API endpoints are called.
- No Navidrome client library is imported.
- Navidrome is mentioned only in architecture docs as a future provider concept.

## No Anchor Provider Internals

- `AnchorControlClient` depends on the `ControlClient` contract, not Anchor internals.
- No Anchor provider-specific classes, modules, or functions are imported.
- Anchor is one optional `ControlClient` adapter, not the center of Aria.

## No Anchor CLI as Integration Layer

- No shell subprocess calls to Anchor CLI.
- No `noqlen-anchor` command execution.
- All Anchor interaction is through the `ControlClient` protocol only.

## No Android/UI/Playback/Queue/Cache Implementation

- No Android SDK, Kotlin, Java, Gradle, Compose, Activity, Fragment, or UI code.
- No Media3, ExoPlayer, MediaSession, or Android Auto implementation.
- No real playback engine, queue, now playing, offline, cache, or storage mutation.
- Android/player boundary contracts are abstract vocabulary and fakes only.
- UI shell planning is documentation only.

## No Provider Hard Coupling

- No direct provider integrations with Navidrome, Jellyfin, Emby, Plex, etc.
- No provider-specific API calls, configurations, or credentials.
- All provider concepts are future/core-domain abstractions.

## No Secrets or Credentials

- No `.env` files, `credentials.json`, or `.secrets` are tracked.
- No API keys, tokens, passwords, or auth credentials exist in source, tests, or docs.
- Repository contamination check returns clean on every commit.

## Optional Anchor Dependency Is Safe

- `AnchorControlClient` uses lazy, optional import of `noqlen_anchor`.
- If Anchor is unavailable, `AriaResult` returns safe degraded/error states, not raw `ImportError`.
- Core imports (`noqlen_aria`) work without Anchor installed.
- CLI `--help` and `doctor` work without Anchor installed.

## Lifecycle Apply Is Blocked

- Lifecycle intents support dry-run preview only.
- `send_lifecycle_intent` in `AnchorControlClient` uses dry-run helpers.
- Apply-mode helpers are not available on the public API surface.
- Real lifecycle mutation (startup, shutdown, reset) is blocked in MVP.

## Sanitized Output Is Safe for Display

- `safe_serialize` produces only JSON-compatible, stdlib-types output.
- No raw exception objects, stack traces, or local paths in serialized output.
- `sanitize_text` redacts unsafe content from user-facing messages.
- `AriaError` and `AriaWarning` messages are stable and sanitized.
- Diagnostics warnings are display-safe with no raw logs, credentials, or provider exception text.

## Tests Are Local, Offline, Fake-First, Deterministic

- All 368 tests run without network, real services, or real music libraries.
- All tests use `FakeControlClient` or deterministic fake implementations.
- No test reaches a real Anchor, Navidrome, provider, filesystem path, or external process.
- Tests are repeatable and produce the same result every run.
