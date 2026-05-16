# Design

## Summary

Bloco 22 creates planning documentation for future real Android integration. It does not implement Android SDK calls, MediaSession, Media3/ExoPlayer, Android Auto, foreground services, widgets, playback engines, audio drivers, UI screens, provider calls, network behavior, or filesystem/device behavior.

The planned integration model is:

`Android UI/surfaces -> Android app/platform adapter -> Aria Core states/intents -> approved platform-neutral contracts/adapters -> future platform implementations`

Aria Core remains the owner of heavy state, policy, validation, readiness, safety, provider/source abstractions, queue/now-playing contracts, playback intents, capability models, snapshots, and sanitized output. The future Android app/platform layer owns platform callbacks, OS lifecycle, native permissions, foreground-service wiring, MediaSession/notification/lock-screen integration, Android Auto surfaces, widgets, and playback-engine adapter wiring.

## Context Package

Standard.

## Context Files Read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/future-product-context.md`
- `aria/context/android-player-reference.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/android-boundary.md`
- `docs/ui-shell-boundary.md`
- `docs/handoff.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/provider-extension-readiness/review.md`
- `aria/review/validation-checklist.md`

## Existing Project Context

Aria Core MVP v0.1.0 is complete. Blocos 8-21 are implemented; Audit 18-20 and Audit 21-23 are deferred to the final post-core/core audit unless explicitly requested. Bloco 21 Provider Extension Readiness is complete. Future custom audio output/driver work is documented as a future Android Player phase outside Aria Core.

Existing Android/player boundary contracts are abstract vocabulary and deterministic fakes, not Android SDK integration. Existing UI shell planning requires UI to remain thin over Aria Core.

## Files To Create

- `aria/specs/features/android-real-integration-planning/requirements.md`
- `aria/specs/features/android-real-integration-planning/design.md`
- `aria/specs/features/android-real-integration-planning/tasks.md`
- `aria/specs/features/android-real-integration-planning/review.md`
- `docs/android-real-integration-plan.md`

## Files To Modify

- `docs/android-boundary.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/handoff.md`
- `aria/context/current.md`
- `aria/context/delta.md`

Only modify these docs if alignment is needed; keep updates concise.

## Files That Must Not Be Touched

- `src/noqlen_aria/**`
- `tests/**`
- `pyproject.toml`
- Android/Kotlin/Java/Gradle files
- UI/screen/navigation/player code
- Provider integration code
- Network behavior
- Filesystem/device behavior
- Private/local tooling files

## Android Integration Boundary Map

Future Android app/platform layer owns:

- OS callbacks, app process lifecycle, activity/service/widget receivers, and platform lifecycle registration.
- Platform permission requests and platform storage access calls.
- MediaSession registration and metadata projection.
- Notification, lock-screen, Bluetooth/headset, Android Auto, and widget platform wiring.
- Foreground-service lifecycle, notification channel policy, and OS compliance.
- Playback-engine adapter wiring to a future Android Player playback layer.
- Translating platform events into Aria-safe intents.
- Translating Aria state into platform-specific display/session models.

Aria Core owns:

- Playback intents and validation.
- Queue, now-playing, renderer, capability, profile/preference, offline/cache/storage policy, provider/source readiness, snapshots, and sanitized results.
- Heavy policy and safety decisions.
- Platform-neutral models and app-facing state.
- Approved platform-neutral service contracts and fake-first behavior.

UI/platform code must never duplicate:

- Queue state machines.
- Now-playing policy.
- Playback availability validation.
- Provider/source readiness decisions.
- Storage/cache/offline policy.
- Permission/storage interpretation beyond platform result collection.
- Safety rules, dry-run/apply boundaries, confirmation policy, or sanitization.
- Audio capability/readiness policy.

Expected Aria models/intents to consume include app-facing result envelopes, now-playing state, playback intents, renderer selection intents, automation intents, library/source/provider readiness models, permission/storage states, playback capability/readiness models, and snapshots as approved by future specs.

## Media Controls Planning

Future real Android media controls should be a surface over Aria playback intents and now-playing state. Play, pause, stop, skip, seek, renderer selection, and related transport actions must become Aria intents first. Android must not own playback state machines or queue mutation logic.

## Lock-screen/Notification Planning

Lock-screen and notification controls are platform projections of the same Aria intent/state model. Future notification actions must map to Aria-safe intents. Future notification metadata must be derived from Aria now-playing/library/source models and sanitized app-facing state.

The platform layer may own notification channels, compact actions, artwork projection, pending intents, and OS-specific lifecycle. It must not bypass Aria Core for provider calls, playback decisions, queue mutation, or safety validation.

## Bluetooth/Headset Planning

Bluetooth/headset button events are platform events. Future platform adapters should normalize them into Aria-safe playback intents and let Aria return success, unavailable, blocked, or warning states. Unsupported, duplicate, or stale events remain platform inputs, not direct playback commands.

## Android Auto Planning

Android Auto is a future platform surface and must consume Aria browse/playback models through an app/platform adapter. Browse trees, playable items, now-playing metadata, search results, and playback actions must be backed by Aria library/source/provider/queue/now-playing state. The Android Auto layer must not call providers directly or implement its own library policy.

## Foreground Service Planning

Foreground service lifecycle is future Android platform work. The service may host long-running playback/session wiring and OS-visible notification policy, but Aria Core remains the source of policy, readiness, state, intents, and validation. Service restart/recovery must rehydrate from Aria-approved state or snapshots instead of inventing platform-only truth.

## Widget Planning

Widgets are optional future platform surfaces. They should display Aria state and submit Aria intents through the Android app/platform adapter. Widgets must not call providers, playback engines, storage APIs, or Aria bridge implementations directly.

## Permission/Storage UX Planning

Future Android permission/storage UX should display Aria boundary state and delegate platform calls to Android code. Aria Core owns platform-neutral `PermissionState`, `StorageAccessState`, offline/cache/storage policy, confirmation policy, and safe explanation text. Android owns permission dialogs, storage access framework calls, OS result callbacks, and native error mapping.

## Playback Engine Adapter Planning

A future playback engine adapter belongs to the Android Player phase or a future dedicated Android implementation spec. The adapter should translate Aria playback intents and stream/renderer/output readiness into calls to the selected platform playback engine while reporting safe, normalized results back to Aria-facing state.

The adapter must not destabilize Aria Core contracts. It must not be implemented in Bloco 22.

## Audio Output/Driver Research Boundary

Bit-perfect, custom USB output, exclusive output, sample-rate switching, DAC control, JNI/NDK, AAudio, Oboe, and audio-driver work remain in the documented future Android Player audio output phases. Aria Core may model requirements and readiness but must not implement real audio drivers or USB output.

## Error Handling

Future Android adapters should translate platform errors into sanitized Aria-facing errors/warnings or platform-neutral unavailable states. UI and platform surfaces must not display raw stack traces, credentials, raw paths, provider internals, or platform exception objects. Stale or unsupported platform events should produce safe blocked/unavailable results through Aria intent validation.

## Security Considerations

- Platform permission prompts must be initiated only by future Android code.
- Aria Core must not store Android permission tokens or raw platform handles.
- Notifications, lock-screen, Android Auto, and widgets must display only sanitized app-facing state.
- Future Android Auto and widget surfaces must avoid leaking private provider details, credentials, local paths, or raw library paths.
- Foreground service logs and diagnostics must remain sanitized.

## Dependencies

None for Bloco 22.

Future implementation dependencies are intentionally undecided and require separate specs.

## Risks

- Future Android code could duplicate Aria queue/now-playing/playback policy.
- Future MediaSession or Android Auto code could call providers directly.
- Future foreground service recovery could create platform-only truth not represented in Aria.
- Future playback engine adapter could leak engine concepts into Aria Core public APIs.
- Future audio output research could accidentally be treated as Aria Core driver work.

## Rollback Strategy

Revert the Bloco 22 documentation/spec commit. No runtime behavior, source code, tests, dependencies, or public APIs are changed.

## Validation Plan

- `pwd`
- `git status --short --branch`
- `find docs aria/specs/features/android-real-integration-planning aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
- `grep -R "android\.|androidx\.|Media3|ExoPlayer|MediaSession|Activity|Fragment|Compose|Kotlin|Gradle" -n src tests || true`
- `grep -R "JNI\|NDK\|AAudio\|Oboe\|UsbManager\|AudioTrack\|AudioManager" -n src tests || true`
- `grep -R "Android implementation\|implemented Android\|real MediaSession implemented\|Android Auto implemented" -n docs aria/context aria/specs/features/android-real-integration-planning || true`

## Behavior Budget

- New behaviors: documentation/planning only.
- Public API changes: none.
- Files allowed: `aria/specs/features/android-real-integration-planning/**`, `docs/**`, `aria/context/current.md`, `aria/context/delta.md`.
- Tests required: no new tests required unless existing docs validation demands it.
- Dependencies: none.
- Stop if: Android implementation becomes necessary; source code changes become necessary; playback engine implementation becomes necessary; audio driver implementation becomes necessary; UI/app shell implementation becomes necessary.
