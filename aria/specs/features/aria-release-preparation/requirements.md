# Requirements

## Status

Draft for Bloco 7 — Aria Core Release Preparation. This is spec/planning only. Do not create a release tag, publish a package, or implement product behavior in this task.

## Problem

Aria Core has completed Blocos 0-6 including bootstrap/audit, core contracts, fake-first control services, dry-run Anchor adapter, Android/player boundary contracts, minimal UI shell planning, and MVP hardening. The Blocos 4-6 formal audit has passed. The project needs a documented, repeatable release preparation process before the first MVP release can be tagged and published.

Without a release preparation spec, the project risks:
- tagging a release with inconsistent version metadata, docs, or package data;
- publishing a package with unreviewed public API surface;
- releasing without confirmed safety, hygiene, and validation evidence;
- leaving future contributors without a changelog, release notes, or post-core backlog summary;
- creating a release that implies future/backlog features are implemented;
- missing repository hygiene checks that could expose local artifacts in the release;
- publishing without a clear handoff for the next phase of work.

## Goal

Define an implementation-ready spec for preparing the Aria Core MVP release. The future implementation should produce:
- a release readiness checklist;
- version consistency verification;
- package metadata review;
- README and public documentation review;
- public API surface summary;
- safety summary for release artifacts;
- test/validation matrix that proves release readiness;
- repository hygiene check results;
- changelog or release notes draft;
- handoff document for the next development phase;
- post-core backlog summary;
- tag/release steps for later execution;
- final stop conditions before tagging or publishing.

## Non-goals

- No release tag is created in this task.
- No package is published in this task.
- No product behavior is implemented.
- No version bump, `pyproject.toml` modification, or package metadata changes.
- No README.md or public documentation rewrites.
- No source code changes to `src/noqlen_aria/**`.
- No test changes.
- No Android SDK, Kotlin, Java, Gradle, Compose, Activity/Fragment, navigation, or UI implementation.
- No playback engine, Media3/ExoPlayer, MediaSession, Android Auto, queue, now playing, offline/cache/download, or storage mutation implementation.
- No provider internals, Anchor CLI as integration, direct Navidrome calls, Jellyfin, Emby, or real music-library access.
- No dependency additions.
- No private/local tooling files.
- Post-core resources remain backlog unless separately spec'd.

## Actors

- Aria Core maintainer preparing the MVP release.
- Future implementation agent executing Bloco 7 release preparation tasks.
- Future reviewer verifying release readiness.
- Future downstream consumers of the released Aria Core package.
- Next-phase contributors consuming the handoff document and post-core backlog.

## Functional requirements

### FR-10: Release Readiness Checklist

- FR-10a: Define a release readiness checklist covering all required checks before tagging.
- FR-10b: Checklist must include verification steps for version, docs, API surface, safety, tests, hygiene, and stop conditions.
- FR-10c: Checklist must produce a clear pass/fail result for each item.
- FR-10d: Checklist must be the final gate before any tag or publish action.

### FR-20: Version Consistency

- FR-20a: Verify `__version__` in `src/noqlen_aria/__init__.py` matches `pyproject.toml` version field.
- FR-20b: Verify version follows a consistent scheme for the MVP release.
- FR-20c: Document the version resolution order and expected single source of truth.
- FR-20d: Confirm no hardcoded version strings exist elsewhere in docs or code that would conflict.

### FR-30: Package Metadata Review

- FR-30a: Review `pyproject.toml` for correct package name, description, Python requirement, dependencies, entry points, license, and authors.
- FR-30b: Confirm package metadata is consistent with MVP scope — no references to unimplemented features.
- FR-30c: Confirm optional dependencies or extras are documented correctly if applicable.
- FR-30d: Confirm build system and packaging configuration is valid for the release.

### FR-40: README Review

- FR-40a: Review README.md for accuracy against current MVP behavior.
- FR-40b: Confirm README does not promise future/backlog features as implemented.
- FR-40c: Confirm README references the correct installation, usage, and development instructions.
- FR-40d: Confirm README includes or links to the license file.

### FR-50: Documentation Consistency Review

- FR-50a: Review all public docs (`docs/architecture.md`, `docs/safety.md`, `docs/anchor-integration.md`, `docs/android-boundary.md`, `docs/ui-shell-boundary.md`, `docs/handoff.md`, `docs/aria-core-handoff.md`, `docs/workflow-vnext.md`) for consistency with current MVP behavior.
- FR-50b: Ensure docs that mention future UI/player/provider/cache/queue/now-playing/playback features mark them as future/backlog and not implemented.
- FR-50c: Ensure docs describe Anchor as one `ControlClient` adapter, not the center of Aria.
- FR-50d: Ensure docs do not promise real Navidrome, provider, Android, playback, queue, now playing, or cache behavior in the MVP.

### FR-60: Public API Surface Summary

- FR-60a: Create or reference a public API surface summary listing all intentional stable exports.
- FR-60b: Confirm all public exports are source-agnostic and do not expose provider internals, Anchor internals, Android SDK types, UI types, or playback engine types.
- FR-60c: Confirm export decisions are covered by existing tests.
- FR-60d: Document any internal or unstable names that exist in public modules but are not part of the stable API.

### FR-70: Safety Summary

- FR-70a: Produce a release safety summary covering the key safety boundaries preserved in the MVP.
- FR-70b: Summary must confirm: no real music-library access; no Navidrome calls; no Anchor internals; no Android/UI/playback/queue/cache implementation; no provider hard coupling; no secrets or credentials in release artifacts.
- FR-70c: Summary must confirm optional Anchor dependency behavior is safe and documented.
- FR-70d: Summary must confirm lifecycle apply remains blocked or unavailable.
- FR-70e: Summary must confirm serialized output is sanitized and safe for display.

### FR-80: Test/Validation Matrix

- FR-80a: Produce a test/validation matrix confirming all high-risk, medium-risk, and low-risk areas are covered.
- FR-80b: Matrix must reference the Test Risk Matrix from `aria/context/test-risk-matrix.md`.
- FR-80c: Matrix must confirm all existing tests pass (currently 368 tests).
- FR-80d: Matrix must confirm CLI smoke commands (`--help`, `doctor`) succeed.
- FR-80e: Matrix must confirm Python compilation succeeds for all source files.

### FR-90: Repository Hygiene Check

- FR-90a: Run the canonical contamination check and confirm no forbidden files are tracked.
- FR-90b: Confirm no private/local/tooling artifacts are staged or committed.
- FR-90c: Confirm no `.opencode/`, `.skills/`, `opencode.json`, `docs/development/`, audit reports, model-routing, `.env`, `credentials.json`, or `.secrets` files are tracked.
- FR-90d: Confirm `git add .` was not used for any release-related commit.

### FR-100: Changelog or Release Notes Draft

- FR-100a: Define the structure and content expectations for release notes or a changelog entry.
- FR-100b: Release notes must summarize completed Blocos 0-6 and the MVP scope.
- FR-100c: Release notes must distinguish implemented features from future/backlog.
- FR-100d: Release notes must include safety boundaries, known limitations, and version information.

### FR-110: Handoff Document for Next Phase

- FR-110a: Define or reference a handoff document that describes the project state after the MVP release.
- FR-110b: Handoff must summarize what is complete, what is next, and what remains backlog.
- FR-110c: Handoff must reference the existing `docs/aria-core-handoff.md` roadmap and any post-release adjustments.
- FR-110d: Handoff must reference relevant ADRs if any exist.

### FR-120: Post-Core Backlog Summary

- FR-120a: Produce a summary of post-core features that remain backlog (library, playlists, queues, now playing, offline, stream quality, output, playback policies, Android boundaries, backup, public API, snapshots, final E2E flows).
- FR-120b: Backlog summary must distinguish between planned future blocks and features not yet spec'd.
- FR-120c: Backlog summary must note that future features require dedicated specs before implementation.

### FR-130: Tag/Release Steps for Later Implementation

- FR-130a: Define the git tag format and version convention for when tagging is executed.
- FR-130b: Define the expected release creation steps.
- FR-130c: Define the expected package build and publish steps for reference.
- FR-130d: Define the final stop conditions — all checklist items must pass before any tag or publish action.

### FR-140: Final Stop Conditions

- FR-140a: Define the mandatory conditions that must all pass before a release tag can be created.
- FR-140b: Define what is NOT a stop condition (e.g., full next-phase implementation, backlog feature completion).
- FR-140c: Ensure stop conditions reference all prior functional requirements (version, docs, API, safety, tests, hygiene, changelog).
- FR-140d: Ensure stop conditions explicitly forbid tagging if any contamination, unsafe output, or scope violation exists.

## Canonical Examples

### CE-01: Release checklist blocks incomplete releases

Given the release readiness checklist has incomplete or failed items,
When release preparation is executed later,
Then tagging and publishing must be blocked,
And the failing items must be documented with the reason for failure.

### CE-02: Future docs stay out of MVP release scope

Given public documentation mentions future UI/player/cache/queue features,
When the release docs consistency review runs,
Then those features must be explicitly marked as future/backlog and not implemented,
And the release notes must not imply they are part of the MVP release.

### CE-03: Repository hygiene blocks contaminated releases

Given the repository hygiene check finds tracked local tooling artifacts or forbidden files,
When release preparation is executed later,
Then the release must be blocked until the contamination is cleaned,
And no tag or publish action may proceed.

### CE-04: Validation failure blocks release

Given any validation command fails (tests, compilation, CLI smoke, contamination check),
When release preparation is executed later,
Then no tag or publish action occurs,
And the validation failure is recorded in the release checklist.

### CE-05: Version metadata mismatch blocks release

Given `__version__` in `__init__.py` and `version` in `pyproject.toml` disagree,
When release preparation is executed later,
Then the mismatch must be fixed before any release tag or publish action,
And all hardcoded version strings elsewhere must be reconciled.

### CE-06: Public API surface is documented and safe

Given a downstream consumer inspects the release,
When they reference the public API surface summary,
Then the summary lists only intentional stable exports,
And internal names, provider internals, Anchor internals, Android types, and playback types are absent,
And safety boundaries are clearly documented.

### CE-07: Release notes accurately describe MVP scope

Given a release consumer reads the release notes,
When they evaluate what is included,
Then the notes summarize completed Blocos 0-6 scope,
And future/backlog features are clearly separated,
And known limitations and safety boundaries are stated.

### CE-08: Handoff enables next-phase work

Given the MVP release is published,
When the next-phase contributor reads the handoff document,
Then they understand what is complete, what is next (Bloco 7+ library/search), and what requires new specs,
And they understand where context files, specs, and roadmap live.

## Non-functional requirements

- NFR01: This task is spec/planning only and creates no runtime behavior.
- NFR02: Future release preparation implementation must be local, offline, deterministic, and safe.
- NFR03: Future release preparation must not add runtime dependencies.
- NFR04: Future release preparation must not modify source code, tests, or package metadata unless a version bump is approved.
- NFR05: All release artifacts (checklist, notes, handoff, backlog summary) must remain within the repository.
- NFR06: Release preparation must produce audit-ready evidence for all checklist items.
- NFR07: All release-facing text must be English, concise, and sanitized.
- NFR08: Release preparation must not require network access, external services, or remote publication.
- NFR09: Release preparation must be repeatable — the checklist must produce the same result when re-run under the same repository state.

## Edge cases

- EC01: Version is still `0.0.0` at the time of release preparation — decide whether to treat as pre-release or require a version decision.
- EC02: README.md references features that exist only in the backlog roadmap — must be flagged or marked.
- EC03: A public doc mentions a Bloco or feature as "future" but the language could be misinterpreted as implemented.
- EC04: A tracked file exists with a local path or tooling artifact that was accidentally committed earlier.
- EC05: `pyproject.toml` lists optional dependencies or extras that don't exist or are not available.
- EC06: The changelog draft mentions a feature that was spec'd but not implemented — must be corrected.
- EC07: The public API summary includes a name that was intentionally exported but is known to be unstable — must be documented.
- EC08: Test count changes between release preparation and tagging — the matrix must reference the current count at time of release.
- EC09: The handoff document references future blocks that have since been renumbered or re-scoped.
- EC10: A dependency check reveals a transitive dependency that is not explicitly listed.

## Acceptance criteria

- AC01: `aria/specs/features/aria-release-preparation/` contains `requirements.md`, `design.md`, `tasks.md`, and `review.md`.
- AC02: Spec covers release readiness checklist with pass/fail items and stop conditions.
- AC03: Spec covers version consistency, package metadata review, and README review.
- AC04: Spec covers documentation consistency review across all public docs.
- AC05: Spec covers public API surface summary and safety summary.
- AC06: Spec covers test/validation matrix referencing Test Risk Matrix.
- AC07: Spec covers repository hygiene check with canonical contamination patterns.
- AC08: Spec covers changelog/release notes draft structure.
- AC09: Spec covers handoff document and post-core backlog summary.
- AC10: Spec covers tag/release steps for later implementation and final stop conditions.
- AC11: Spec states clearly: no tag is created, no package is published, no product behavior is implemented in this task.
- AC12: Canonical Examples use Given / When / Then and cover the five expected scenarios plus additional release-specific scenarios.
- AC13: Behavior Budget is present.
- AC14: Test Risk Matrix is present.
- AC15: Context package used is documented as Standard.
- AC16: Delta update checklist is present.
- AC17: No source code, tests, `pyproject.toml`, README.md, Android/UI/playback/queue/cache/provider implementation, dependency, version change, tag, release, or publish action is taken.
- AC18: Requested validation commands pass or any failure is recorded.
- AC19: Spec is committed with `docs(spec): add Aria release preparation spec`.

## Open questions

- OQ01: Should the MVP release version be `0.1.0` (first MVP), `1.0.0` (first stable), or remain `0.0.0` until a later decision? Proposed default: leave as `0.0.0` until a version decision is made in the implementation task.
- OQ02: Should release notes live in a dedicated `CHANGELOG.md` file, a `docs/release-notes` section, or a GitHub release description? Proposed default: `CHANGELOG.md` for the repository plus a GitHub release body derived from it.
- OQ03: Should the release checklist be a Markdown file, a runnable script, or both? Proposed default: Markdown checklist with canonical CLI invocation examples.
- OQ04: Should the post-core backlog summary differentiate between spec'd future blocks (Blocos 7-21) and entirely unspec'd features? Proposed default: yes, using the roadmap from `docs/aria-core-handoff.md` as the primary reference.
- OQ05: Should the release notes mention the Blocos 4-6 formal audit result? Proposed default: yes, as a quality gate.
- OQ06: Should the handoff document be the existing `docs/handoff.md` or a new `docs/release-handoff.md`? Proposed default: update the existing `docs/handoff.md` with post-release status.
- OQ07: Should release preparation require a signed/anonymous git tag or an unsigned one? Proposed default: unsigned lightweight git tag unless a signing policy is adopted later.
