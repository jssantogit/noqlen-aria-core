# Noqlen Aria Core

Noqlen Aria Core is the modular app/player-facing core of a music player. It owns contracts, states, services, fakes, adapters, snapshots, safe serialization, and tests.

Aria Core is not UI and is not an Android app. Future UI must remain a thin adapter over Aria Core.

Aria Workflow is the development method used in this repository. Aria Workflow is not the product.

## What Is Implemented (MVP)

- Control-plane contracts and fake-first services.
- Dry-run/offline Anchor adapter.
- Android/player boundary contracts (abstract vocabulary and fakes, not Android SDK).
- Minimal UI shell planning artifacts (documentation only).
- Safe serialization and sanitized output helpers.
- Intentional public API exports.
- 368 tests, all passing.

For details, see `docs/release-notes.md` and `docs/api-surface.md`.

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
- `docs/post-core-backlog.md` — post-core features roadmap.
- `docs/handoff.md` — current project status and handoff.
