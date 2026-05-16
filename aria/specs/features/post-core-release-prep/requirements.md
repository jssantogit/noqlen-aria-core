# Requirements

## Status

Bloco 24 spec for Post-core Release Prep. Context package used: Standard.

## Problem

Aria Core MVP `v0.1.0` is complete, and post-core Blocos 8-23 are implemented, audited, or documented according to the roadmap. Before any post-core tag or publish decision, the repository needs release-preparation artifacts that summarize implemented foundation work, public API surface, safety boundaries, known limitations, validation expectations, repository hygiene, and handoffs to final audit and future Android/app phases.

## Goal

Prepare documentation and readiness artifacts for the final Post-core/Core Audit. Bloco 24 is release preparation only.

## Non-goals

- No tag creation.
- No package publishing.
- No source feature implementation.
- No Android app implementation.
- No Future Android Player implementation.
- No real provider integration.
- No real playback.
- No real audio driver.
- No destructive operations.
- No package version changes.
- No source or test changes.

## Actors

- Maintainer deciding whether the final post-core/core audit can start.
- Final audit reviewer using the release-prep docs as audit inputs.
- Future Android Player implementer consuming handoff notes.
- Future app/UI implementer consuming thin-shell boundaries.

## Functional requirements

- Create post-core release-prep spec files under `aria/specs/features/post-core-release-prep/`.
- Create or update post-core release checklist, release notes, API surface summary, safety summary, handoff, known limitations, and future Android Player handoff docs.
- Update `docs/handoff.md` and `docs/post-core-backlog.md` status/next-step wording.
- Update `README.md` only for stale status/roadmap wording.
- Update `aria/context/current.md` and `aria/context/delta.md` concisely.
- Distinguish implemented Aria Core models/services from future real Android/player/provider/audio implementation.
- State that final audit is required before any post-core tag or publish action.
- Document tag/release decision criteria and blockers.
- Preserve repository hygiene and confirm no private/local tooling files are tracked.

## Non-functional requirements

- Documentation must be accurate, concise, and audit-ready.
- Release notes must not claim final audit has passed.
- Release notes must not claim a post-core tag exists.
- Release notes must not claim Android app, real player, custom audio driver, real provider integration, Media3/ExoPlayer, MediaSession, Android Auto, UI implementation, real streaming, real transcoding, or bit-perfect output exists.
- Public API summary must list existing implemented exports only.
- Safety summary must keep provider, Android, playback, audio-driver, network, filesystem, secret, and destructive-operation boundaries explicit.
- Validation evidence must be recorded in review and delta docs.

## Canonical Examples

Given post-core release notes mention a feature, When the docs are reviewed, Then they must distinguish implemented core models/services from future real Android/player implementation.

Given future Android Player work is referenced, When release prep runs, Then it must be marked as future and not implemented.

Given validation fails, When release prep is evaluated, Then tag readiness must be blocked.

Given private/local tooling files are present, When repository hygiene runs, Then release readiness must be blocked.

Given public API summary lists a name, When compared to actual exports, Then it should match existing implemented API only.

Given post-core docs mention bit-perfect/custom audio output, When reviewed, Then they must say Aria models readiness/capability only and does not implement a driver.

Given post-core docs mention providers, When reviewed, Then they must not claim current Anchor is multi-provider.

## Edge cases

- Existing MVP release docs remain historical; post-core docs must not overwrite their meaning.
- Documentation can mention forbidden technologies as future or explicitly not implemented without implying implementation.
- Validation-command text can contain forbidden terms; audit should separate command references from implementation claims.
- README can be updated for status wording, but must not become a full post-core release note.

## Acceptance criteria

- Spec files exist and include Behavior Budget, Test Risk Matrix, Canonical Examples, and Delta update checklist.
- Post-core release checklist, release notes, API surface summary, safety summary, handoff, known limitations, and future Android Player handoff exist.
- `docs/handoff.md`, `docs/post-core-backlog.md`, `README.md`, `aria/context/current.md`, and `aria/context/delta.md` reflect Bloco 24 readiness status accurately.
- No source, tests, package metadata version, Android, player, provider, network, filesystem/device, tag, or publish changes occur.
- Required validation commands pass or documented blockers prevent release readiness.
- Final Post-core/Core Audit is listed as the next gate before any tag or publish action.

## Open questions

- Final audit will decide whether the post-core foundation is ready for a tag.
- Maintainer still needs to decide whether and when package publishing is appropriate.
