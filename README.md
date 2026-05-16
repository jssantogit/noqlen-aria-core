# Noqlen Aria Core

Noqlen Aria Core is the modular app/player-facing core of a music player. It owns contracts, states, services, fakes, adapters, snapshots, safe serialization, and tests.

Aria Core is not UI and is not an Android app. Future UI must remain a thin adapter over Aria Core.

Aria Workflow is the development method used in this repository. Aria Workflow is not the product.

## What Is Implemented

MVP scope is Blocos 0-7. Local tag `v0.1.0` exists. Post-core foundation Blocos 8-24 are implemented, documented, or release-prepared according to the roadmap. Final Post-core/Core Audit is still required before any post-core tag or publish decision.

- Control-plane contracts and fake-first services.
- Dry-run/offline Anchor adapter.
- Android/player boundary contracts (abstract vocabulary and fakes, not Android SDK).
- Minimal UI shell planning artifacts (documentation only).
- Safe serialization and sanitized output helpers.
- Intentional public API exports.
- Post-core media source, library, queue, now playing, playback intent, offline/cache, radio, quality, capability, profile/preference, smart playlist, snapshot, provider-readiness, Android planning, and release-prep foundations.
- Existing tests pass as recorded in the post-core release checklist.

For MVP details, see `docs/release-notes.md` and `docs/api-surface.md`. For post-core release-prep details, see `docs/post-core-release-notes.md` and `docs/post-core-api-surface.md`.

## Architecture

`Future UI/App/Player -> Aria Core -> contracts/adapters -> providers/backends`

Anchor is one optional `ControlClient` adapter, not the center of Aria. Aria depends on contracts, not Anchor internals.

Full architecture and roadmap: `docs/aria-core-handoff.md`.

## Safety

See `docs/safety.md` and `docs/safety-summary.md` for the current safety boundaries.

## Development

Python 3.11+ is required.

Install locally for development:

```bash
python3 -m pip install -e .
```

CLI smoke examples:

```bash
noqlen-aria --help
noqlen-aria doctor
```

Without installation:

```bash
PYTHONPATH=src python3 -m noqlen_aria.cli --help
PYTHONPATH=src python3 -m noqlen_aria.cli doctor
```

Run tests:

```bash
python3 -m pytest
```

## Release Artifacts

- `docs/release-checklist.md` — release readiness checklist.
- `docs/release-notes.md` — release notes for the MVP.
- `docs/api-surface.md` — public API surface summary.
- `docs/safety-summary.md` — verified safety boundaries.
- `docs/post-core-release-checklist.md` — post-core release-prep checklist and final audit gate.
- `docs/post-core-release-notes.md` — post-core release-prep notes.
- `docs/post-core-api-surface.md` — post-core public API surface summary.
- `docs/post-core-safety-summary.md` — post-core safety and boundary summary.
- `docs/post-core-handoff.md` — handoff to final audit and future phases.
- `docs/future-android-player-handoff.md` — future Android Player handoff outside Aria Core.
- `docs/post-core-backlog.md` — post-core features roadmap.
- `docs/handoff.md` — current project status and handoff.
