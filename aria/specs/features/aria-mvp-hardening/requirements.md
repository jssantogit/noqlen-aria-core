# Requirements

## Status

Draft for Bloco 6 — Aria MVP Hardening. This is spec/planning only. Do not implement hardening in this task.

## Problem

Aria Core has completed the bootstrap/control-plane base, fake-first services, dry-run Anchor adapter, Android/player boundary contracts, and minimal UI shell planning artifacts. Before release preparation, the MVP needs a hardening pass that confirms the currently shipped surface is intentional, safe, documented, testable, and still inside the scope boundaries.

Without a formal hardening spec, the project risks:
- exposing accidental public names as stable API;
- serializing raw error, warning, exception, path, or provider details;
- treating optional dependencies as required runtime dependencies;
- allowing lifecycle apply behavior to leak through the MVP surface;
- drifting toward Anchor/provider internals, CLI-as-integration, real Navidrome execution, real music-library access, Android SDK code, UI code, playback, queue, now playing, or cache implementation;
- entering formal audit with inconsistent docs or unclear validation evidence.

## Goal

Define an implementation-ready hardening spec for the Aria Core MVP before release preparation. The future implementation should review and, if needed, adjust the existing MVP surface so that:
- public exports are intentional and documented;
- safe serialization produces sanitized outputs only;
- errors and warnings are safe for user-facing display;
- optional dependency behavior is deterministic and degraded-safe;
- Anchor adapter dry-run/apply safety is verified;
- forbidden provider, Android, UI, playback, queue, now playing, cache, and real-library integrations remain absent;
- documentation and tests are consistent with implemented behavior;
- the repository is ready for Bloco 4-6 formal audit.

## Non-goals

- No hardening implementation in this task.
- No source code changes to `src/noqlen_aria/**` in this task.
- No test changes in this task.
- No `pyproject.toml` changes.
- No Android SDK, Kotlin, Java, Gradle, Compose, Activity/Fragment, navigation, or UI implementation.
- No playback engine, Media3/ExoPlayer, MediaSession, Android Auto, queue, now playing, offline/cache/download, or storage mutation implementation.
- No real Anchor provider internals.
- No Anchor CLI as integration.
- No direct Navidrome, Jellyfin, Emby, provider, or real music-library access.
- No dependency additions.
- No private/local tooling files.

## Actors

- Aria Core maintainer preparing MVP release readiness.
- Future implementation agent executing Bloco 6 hardening tasks.
- Future reviewer performing Bloco 4-6 formal audit.
- Future UI/app shell implementer relying on a stable, sanitized MVP surface.
- Future adapter implementer relying on clear optional dependency and dry-run/apply contracts.

## Functional requirements

### FR-10: Public API Surface Review

- FR-10a: Inventory all public module exports intended for MVP use.
- FR-10b: Identify accidental public names that should remain internal and are not stable.
- FR-10c: Confirm `__all__` or equivalent export documentation exposes only intentional stable names.
- FR-10d: Confirm public names are source-agnostic and do not expose provider internals, Anchor internals, Android SDK types, UI types, or playback engine types.
- FR-10e: Document any proposed public API change before implementation.

### FR-20: Intentional Exports

- FR-20a: Public exports must include stable contract/state/result/service/adapter names that are already within MVP scope.
- FR-20b: Public exports must not include private helper classes, mapper internals, fake-only implementation details unless explicitly intended, or accidental imported names.
- FR-20c: Public export decisions must be covered by tests in the future implementation task.
- FR-20d: Public export decisions must be reflected in docs and handoff notes.

### FR-30: Safe Serialization Review

- FR-30a: Review all serialization-capable states and results for stdlib-only, JSON-compatible, deterministic output.
- FR-30b: Ensure serialization never includes raw exception objects, stack traces, credentials, local paths, provider internals, or music-library contents.
- FR-30c: Ensure sanitized error and warning messages remain display-safe after serialization.
- FR-30d: Ensure degraded/default states serialize safely when dependencies or adapters are unavailable.
- FR-30e: Future implementation must add or update tests for safe serialization and negative unsafe-detail cases.

### FR-40: Sanitized Errors and Warnings

- FR-40a: Review `AriaError` and `AriaWarning` construction paths.
- FR-40b: Ensure user-facing messages are sanitized and stable.
- FR-40c: Ensure internal codes do not leak provider secrets or raw backend data.
- FR-40d: Ensure diagnostics warnings do not include raw logs, stack traces, filesystem paths, credentials, or provider exception text.
- FR-40e: Future implementation must include representative negative tests for unsafe input details.

### FR-50: Optional Dependency Behavior

- FR-50a: Verify optional `noqlen_anchor` behavior is lazy, deterministic, and safe when unavailable.
- FR-50b: When Anchor is unavailable, readiness/status/diagnostics should return safe degraded states or safe failures through `AriaResult`, not import errors or raw exceptions.
- FR-50c: Optional dependency absence must not change importability of core contracts, services, fakes, CLI help, or CLI doctor.
- FR-50d: No new dependency may be added for hardening.

### FR-60: Anchor Adapter Dry-Run/Apply Safety

- FR-60a: Verify `AnchorControlClient` uses contract-level behavior only and does not call Anchor provider internals.
- FR-60b: Verify dry-run lifecycle previews remain available where currently supported.
- FR-60c: Verify lifecycle apply operations are blocked, unavailable, or return a safe failure on the MVP surface.
- FR-60d: Verify no Anchor CLI command is used as an integration API.
- FR-60e: Verify no direct Navidrome execution or direct provider calls exist.

### FR-70: Forbidden Integration Boundary Checks

- FR-70a: Verify no provider internals are imported or called.
- FR-70b: Verify no CLI-as-integration pattern exists.
- FR-70c: Verify no real Navidrome execution exists.
- FR-70d: Verify no real music-library path is read or mutated.
- FR-70e: Verify no Android SDK dependency exists.
- FR-70f: Verify no UI implementation exists.
- FR-70g: Verify no playback, queue, now playing, offline/cache/download, or storage mutation implementation exists.

### FR-80: Documentation Consistency

- FR-80a: Review `docs/architecture.md`, `docs/safety.md`, `docs/anchor-integration.md`, `docs/android-boundary.md`, `docs/ui-shell-boundary.md`, `docs/handoff.md`, and `docs/aria-core-handoff.md` for consistency with current MVP behavior.
- FR-80b: Ensure future UI/player/provider/cache features are marked as future/backlog and not implemented.
- FR-80c: Ensure docs describe Anchor as one `ControlClient` adapter, not the center of Aria.
- FR-80d: Ensure docs do not promise real provider, Android, playback, queue, now playing, or cache behavior in MVP.

### FR-90: Test Coverage Review

- FR-90a: Inventory existing test coverage for public exports, safe serialization, sanitized errors/warnings, optional dependency absence, dry-run/apply safety, and boundary non-goals.
- FR-90b: Identify missing tests required before release preparation.
- FR-90c: Future implementation must add tests only for behavior within the approved hardening budget.
- FR-90d: Test coverage must remain local, offline, fake-first, deterministic, and safe.

### FR-100: Repository Hygiene and Audit Readiness

- FR-100a: Verify no private/local/tooling files are tracked.
- FR-100b: Verify no source/test changes occur in this spec task.
- FR-100c: Future implementation must update `aria/context/delta.md` with validation evidence.
- FR-100d: Prepare review evidence for Bloco 4-6 formal audit.

## Canonical Examples

### CE-01: Serialized user-facing error is sanitized

Given a user-facing error contains raw details
When it is serialized
Then output is sanitized
And no stack trace, credential, local path, provider exception object, or music-library detail appears

### CE-02: Anchor unavailable returns degraded state

Given Anchor is unavailable
When Aria readiness is requested
Then Aria returns a safe degraded state
And the result uses `AriaResult` or existing safe state primitives
And no raw import error is exposed

### CE-03: Public exports are intentional

Given a caller inspects public exports
When using Aria Core
Then only intentional stable names are exposed
And private helpers, provider internals, accidental imports, and backend-specific internals are absent

### CE-04: Lifecycle apply remains unavailable

Given a lifecycle apply operation is attempted
When using the MVP surface
Then it is blocked or unavailable
And the caller receives a safe failure or explicit non-availability state
And no real lifecycle mutation is performed

### CE-05: Future docs stay out of MVP scope

Given docs describe future UI/player features
When checking MVP scope
Then docs mark them as future/backlog and not implemented
And no UI, Android SDK, playback, queue, now playing, or cache implementation is implied

### CE-06: Optional dependency absence does not break core imports

Given optional Anchor packages are not installed
When a caller imports core contracts, services, fakes, CLI help, and CLI doctor
Then those imports and commands still work
And unavailable adapter behavior is explicit and safe

### CE-07: Diagnostics warnings hide raw backend details

Given diagnostics collects a warning from an unsafe backend detail
When the warning reaches app-facing output
Then the message is display-safe
And raw logs, stack traces, credentials, provider exception text, and local paths are absent

### CE-08: Hardening does not implement backlog features

Given the hardening implementation is executed later
When reviewing changed files
Then it contains no Android SDK, UI, playback, queue, now playing, offline/cache, direct provider integration, or real music-library access
And hardening remains an MVP safety/release-readiness pass only

## Non-functional requirements

- NFR01: This task is spec/planning only and creates no runtime behavior.
- NFR02: Future hardening must be local, offline, deterministic, and fake-first.
- NFR03: Future hardening must preserve source-agnostic contracts.
- NFR04: Future hardening must not add runtime dependencies.
- NFR05: Future hardening must prefer minimal source changes and avoid compatibility shims unless a concrete need exists.
- NFR06: Future hardening must produce reviewable validation evidence for Bloco 4-6 formal audit.
- NFR07: All new or updated user-facing text must be English, concise, and sanitized.
- NFR08: Documentation must distinguish implemented MVP behavior from future/backlog features.

## Edge cases

- EC01: `noqlen_anchor` is not installed and `AnchorControlClient` is imported or constructed.
- EC02: An adapter receives a raw exception containing a local path or credential-like token.
- EC03: A warning includes provider-specific output that should not be displayed.
- EC04: A public module imports a helper name that accidentally becomes visible to wildcard import.
- EC05: Lifecycle apply is requested by code that currently expects dry-run preview only.
- EC06: Docs mention future UI/player features and could be read as implemented.
- EC07: Serialization encounters nested state containing optional `None` values or enum values.
- EC08: Test coverage exists for happy paths but not unsafe-detail negative paths.
- EC09: Repository contains untracked or tracked local tooling files that must not be committed.
- EC10: Audit evidence needs to separate documentation/planning references from implementation code.

## Acceptance criteria

- AC01: `aria/specs/features/aria-mvp-hardening/` contains `requirements.md`, `design.md`, `tasks.md`, and `review.md`.
- AC02: Spec covers public API surface review and intentional exports.
- AC03: Spec covers safe serialization and sanitized errors/warnings.
- AC04: Spec covers optional dependency behavior.
- AC05: Spec covers Anchor adapter dry-run/apply safety verification.
- AC06: Spec covers no provider internals, no CLI-as-integration, no real Navidrome execution, and no real music-library access.
- AC07: Spec covers no Android SDK dependency, no UI implementation, and no playback/queue/cache implementation.
- AC08: Spec covers documentation consistency and test coverage review.
- AC09: Spec covers repository hygiene and readiness for Bloco 4-6 formal audit.
- AC10: Canonical Examples use Given / When / Then and include the five expected scenarios.
- AC11: Behavior Budget is present.
- AC12: Test Risk Matrix is present.
- AC13: Context package used is documented as Standard.
- AC14: Delta update checklist is present.
- AC15: No source code, tests, `pyproject.toml`, Android/UI/playback/queue/cache/provider implementation, dependency, or private/local tooling files are changed.
- AC16: Requested validation commands pass or any failure is recorded.
- AC17: Spec is committed with `docs(spec): add Aria MVP hardening spec`.

## Open questions

- OQ01: Should future hardening define `__all__` for every public module or only the top-level package? Proposed default: top-level package plus any modules already intended for direct import.
- OQ02: Should safe serialization use existing dataclass/asdict patterns or introduce dedicated helpers? Proposed default: reuse existing patterns unless tests reveal unsafe output.
- OQ03: Should optional Anchor absence be represented as failed `AriaResult`, degraded `ReadinessViewState`, or both depending on call site? Proposed default: safe degraded state for readiness, safe failure for adapter-specific calls.
- OQ04: Should apply-mode lifecycle operations remain permanently unavailable in MVP or be feature-flagged later? Proposed default: unavailable until a dedicated future spec.
- OQ05: Should documentation consistency fixes happen in the same hardening implementation block? Proposed default: yes, only for tiny clarifying updates directly tied to MVP safety.
