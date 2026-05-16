# Requirements

## Status

Approved for Bloco 20 implementation. Context package used: Standard.

## Problem

Aria Core has local models for source, library, queue, now-playing, playback intents, radio, offline/cache, quality, capabilities, profiles, preferences and smart playlists, but it does not yet expose a structured way to build sanitized app-facing state snapshots or deterministic fake end-to-end flows that compose those foundations safely.

## Goal

Add in-memory state snapshot contracts and deterministic fake flow foundations for debug, support, test, and future UI consumption. Snapshots must be sanitized structured Aria Core models. Fake flows must compose only fake/local service behavior and produce ordered traces without side effects.

## Non-goals

- No real provider calls.
- No real network behavior.
- No real filesystem persistence, snapshot files, filesystem traversal, or real music library access.
- No real playback, stream resolution, renderer control, transcoding, downloads, or cache mutation.
- No Android, UI, Kotlin, Java, Gradle, screen, navigation, or demo app implementation.
- No background automation, scheduler, external orchestration, or scripts.
- No provider mutation or provider playlist creation.
- No destructive behavior.
- No Bloco 21 Provider Extension Readiness implementation.

## Actors

- Future UI/app debug surface consuming sanitized snapshots.
- Core tests and demos using deterministic fake traces.
- Support/diagnostics tooling consuming structured state only.
- Core developers validating safety boundaries.

## Functional requirements

- FR-01 Define snapshot identities, scopes, metadata, sections, redaction policy, validation issues, results, diffs, diff entries, and unavailable reasons.
- FR-02 Build snapshots only from caller-provided in-memory Aria state objects or dictionaries.
- FR-03 Apply redaction/sanitization for secret-like keys, credential-like values, raw personal paths, raw logs, tracebacks, and unsupported objects.
- FR-04 Validate snapshot scopes and sections and return safe result objects for invalid input.
- FR-05 Compute structural snapshot diffs across sections without semantic/provider comparison.
- FR-06 Define fake flow ids, scenarios, steps, step kinds, step results, traces, results, validation issues, and unavailable reasons.
- FR-07 Run deterministic source -> library -> queue -> now-playing intent -> diagnostics fake flow.
- FR-08 Run deterministic profile/preferences -> smart playlist preview -> queue preview fake flow.
- FR-09 Run deterministic radio station -> availability -> playback intent preview fake flow.
- FR-10 Run deterministic offline/cache policy -> quality decision -> capability summary fake flow.
- FR-11 Represent degraded/unavailable fake flow steps safely without provider/network/playback side effects.
- FR-12 Expose only intentional snapshot and fake-flow public API names.
- FR-13 Preserve boundaries: no providers, network, filesystem, playback, Android, UI, background jobs, destructive operations, or Bloco 21 behavior.

## Non-functional requirements

- Deterministic output for the same inputs.
- JSON-compatible output after existing `safe_serialize` handling.
- Local-only, dependency-free implementation.
- Conservative sanitization over raw fidelity.
- Tests must cover success, redaction, validation, diffs, deterministic traces, degraded flows, and safety boundaries.

## Canonical Examples

- Given Aria has profile, library, queue and now-playing states, When a snapshot is built, Then Aria returns a sanitized structured snapshot.
- Given snapshot input contains secret-like values or raw personal paths, When snapshot redaction runs, Then sensitive data is excluded or redacted.
- Given two snapshots differ only in queue order, When diff is computed, Then Aria reports a structural queue section difference.
- Given fake media source data exists, When the source -> library -> queue -> now-playing intent -> diagnostics flow runs, Then Aria returns a deterministic trace without provider/network/playback calls.
- Given a smart playlist preview produces items, When the fake flow adds previewed items to a queue preview, Then no provider playlist or real queue mutation outside local flow state occurs.
- Given a radio station is unavailable, When the radio fake flow reaches playback intent preview, Then Aria returns blocked/unavailable state safely.
- Given offline/cache and quality policies are evaluated together, When the fake flow runs, Then it returns policy decisions without downloads, network probes or transcoding.
- Given UI needs a debug/support snapshot later, When it consumes snapshot data, Then it gets sanitized Aria Core models only.

## Edge cases

- Empty snapshot state returns a valid snapshot with no sections and a validation issue only when requested scopes are invalid.
- Unknown sections are blocked and reported as validation issues.
- Secret-like section keys are excluded, not preserved as raw values.
- Raw paths and multiline/raw logs are redacted.
- Unsupported objects are converted to safe unavailable placeholders.
- Identical snapshots produce an empty diff.
- Queue order changes produce a queue-section diff.
- Fake source unavailability produces a degraded partial trace and a safe result.
- Unsupported fake flow ids return safe errors.

## Acceptance criteria

- Spec files exist under `aria/specs/features/state-snapshots-e2e-fake-flows/`.
- Snapshot contracts and services are implemented in allowed source files.
- Fake flow contracts, runner, and required scenarios are implemented.
- Tests cover the required snapshot, redaction, diff, fake flow, degraded, and boundary cases.
- Behavior Budget, Test Risk Matrix, Canonical Examples, and Delta update checklist are present.
- Validation passes and evidence is recorded in `review.md`.
- `aria/context/current.md` and `aria/context/delta.md` are concise and updated.
- Spec and implementation are committed together.

## Open questions

- Future durable snapshot export/import format remains undefined.
- Future UI presentation of snapshots and traces remains outside this block.
- Future provider-backed flow readiness remains Bloco 21+ scope and is not implemented here.
