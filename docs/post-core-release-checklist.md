# Post-core Release Checklist

Bloco 24 prepares release-readiness artifacts for the post-core foundation. This checklist is not final audit approval. No tag is created and no package is published by this task.

## Release Gate Status

- [x] Post-core release-prep docs exist.
- [x] MVP tag `v0.1.0` exists historically.
- [ ] Final Post-core/Core Audit passed.
- [ ] Post-core release tag approved.
- [ ] Package publish approved.

Tag and publish remain blocked until final audit passes and the maintainer explicitly approves release actions.

## Documentation Status

- [x] Release notes: `docs/post-core-release-notes.md`.
- [x] Public API summary: `docs/post-core-api-surface.md`.
- [x] Safety summary: `docs/post-core-safety-summary.md`.
- [x] Known limitations: `docs/post-core-known-limitations.md`.
- [x] Post-core handoff: `docs/post-core-handoff.md`.
- [x] Future Android Player handoff: `docs/future-android-player-handoff.md`.
- [x] Handoff status updated: `docs/handoff.md`.
- [x] Backlog status updated: `docs/post-core-backlog.md`.
- [x] README status updated for post-core docs.

## Truthfulness Checks

- [x] Docs do not claim final audit has passed.
- [x] Docs do not claim a post-core tag exists.
- [x] Docs do not claim packages were published.
- [x] Docs do not claim an Android app exists.
- [x] Docs do not claim a real player exists.
- [x] Docs do not claim real playback exists.
- [x] Docs do not claim real streaming exists.
- [x] Docs do not claim real transcoding exists.
- [x] Docs do not claim real provider integration exists.
- [x] Docs do not claim current Anchor is multi-provider.
- [x] Docs do not claim a custom audio driver exists.
- [x] Docs do not claim bit-perfect/custom audio output is implemented.
- [x] Docs do not claim Media3/ExoPlayer, MediaSession, Android Auto, or UI implementation exists.

## Public API Summary Status

- [x] Summary exists at `docs/post-core-api-surface.md`.
- [x] Summary is based on existing top-level exports in `src/noqlen_aria/__init__.py`.
- [x] Summary groups implemented contracts, models, services, fakes, and helpers.
- [x] Summary does not list future-only Android/player/provider/driver/UI names as current API.

## Safety Summary Status

- [x] Summary exists at `docs/post-core-safety-summary.md`.
- [x] No provider internals or direct Navidrome/Jellyfin/Emby integration are claimed.
- [x] No network, real filesystem/device, real library access, playback, stream execution, transcoding, Android SDK, audio driver, destructive cache, or destructive restore behavior is claimed.
- [x] Secrets, raw paths, raw logs, and provider exception sanitization expectations are documented.

## Final Validation Matrix

| Check | Command | Required result | Status |
|-------|---------|-----------------|--------|
| Workspace | `pwd` | Repository root | Pass |
| Git state | `git status --short --branch` | Only expected release-prep changes before commit; clean after commit | Pass |
| File inventory | `find README.md docs aria/specs/features/post-core-release-prep aria/context aria/review -maxdepth 6 -type f | sort` | Expected docs/spec/context files visible | Pass |
| Whitespace | `git diff --check` | No whitespace errors | Pass |
| Compile | `python3 -m py_compile src/noqlen_aria/*.py` | No compile errors | Pass |
| CLI help | `PYTHONPATH=src python3 -m noqlen_aria.cli --help` | Help prints successfully | Pass |
| CLI doctor | `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` | Doctor runs successfully | Pass |
| Tests | `python3 -m pytest` | Existing suite passes | Pass |
| Tracked contamination | `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` | No tracked forbidden files | Pass |
| False claims | Required false-claim search | No implementation claims found | Pass |
| Android/player boundaries | Required `src`/`tests` searches | No forbidden implementation found | Pass |
| Provider boundaries | Required provider search | No forbidden implementation found | Pass |

## Repository Hygiene

- [x] No private/local artifacts tracked.
- [x] No local tooling files tracked.
- [x] No `.opencode/`, `.skills/`, `opencode.json`, `docs/development`, audit-report files, model routing files, `.env`, `credentials.json`, or `.secrets` tracked.
- [x] No uncommitted source or test changes.
- [x] No version changes.
- [x] `git add .` not used.
- [x] Explicit allowlist staging required for commit.
- [ ] Working tree clean after commit.

## Final Audit Inputs

The final Post-core/Core Audit should verify:

- Blocos 18-20 deferred audit items.
- Blocos 21-23 deferred audit items.
- Bloco 24 release-prep docs and claims.
- Public API summary against actual exports.
- Safety summary against source and tests.
- Repository hygiene and tracked-file contamination.
- Validation evidence and any expected search matches.

## Tag And Publish Decision Criteria

Tag readiness requires all of the following:

- Final Post-core/Core Audit passes.
- Required validation passes.
- Working tree is clean.
- No tracked private/local/tooling artifacts.
- No source/test/package metadata changes are pending from release-prep.
- Docs do not make false implementation claims.
- Maintainer explicitly approves tag creation.

Package publish readiness additionally requires explicit publish approval, package metadata review, build verification, and maintainer release decision.

## Blockers

Tag and publish are blocked if any of the following occur:

- Final audit fails or is not yet run.
- Validation fails.
- Private/local tooling files are tracked.
- Working tree has uncommitted changes at release decision time.
- Docs claim future Android/player/provider/audio behavior is implemented.
- Public API summary lists unimplemented names.
- Source, tests, version, Android/player/audio-driver/provider implementation, tag creation, or package publishing occurs during Bloco 24.
