# Design

## Summary

Bloco 23 creates documentation handoff for a future Android shell/app. It defines how Android should consume Aria Core state/results/intents, how Android platform events should become Aria-safe intents, and how responsibilities split across Android shell, Aria Core, Android platform adapters, and the future Android Player/audio layer.

Bloco 23 does not implement Android SDK calls, Kotlin, Java, Gradle, Compose, Activity, Fragment, UI screens, MediaSession, Media3/ExoPlayer, Android Auto, notifications, lock-screen controls, Bluetooth/headset controls, widgets, playback engines, audio drivers, USB output, provider integrations, network behavior, filesystem/device behavior, source code, or tests.

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
- `docs/android-real-integration-plan.md`
- `docs/ui-shell-boundary.md`
- `docs/handoff.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/android-real-integration-planning/review.md`
- `aria/review/validation-checklist.md`

## Existing Project Context

Aria Core MVP v0.1.0 is complete. Blocos 8-21 are implemented. Bloco 22 Android Real Integration Planning is complete as planning/docs only. Audit 18-20 and Audit 21-23 are deferred to the final post-core/core audit unless explicitly requested. Future custom audio output/driver work is documented as a future Android Player phase outside Aria Core.

## Files To Create

- `aria/specs/features/android-shell-handoff/requirements.md`
- `aria/specs/features/android-shell-handoff/design.md`
- `aria/specs/features/android-shell-handoff/tasks.md`
- `aria/specs/features/android-shell-handoff/review.md`
- `docs/android-shell-handoff.md`

## Files To Modify

- `docs/android-real-integration-plan.md`
- `docs/ui-shell-boundary.md`
- `docs/android-boundary.md`
- `docs/post-core-backlog.md`
- `docs/handoff.md`
- `docs/aria-core-handoff.md`
- `aria/context/current.md`
- `aria/context/delta.md`

Only modify alignment docs where useful; keep context updates concise.

## Files That Must Not Be Touched

- `src/noqlen_aria/**`
- `tests/**`
- `pyproject.toml`
- Android/Kotlin/Java/Gradle files
- Compose/Activity/Fragment/UI implementation files
- MediaSession, Media3/ExoPlayer, Android Auto, notification, lock-screen, Bluetooth/headset, or widget implementation files
- Playback engine, audio driver, USB output, JNI/NDK/AAudio/Oboe implementation files
- Provider integration files
- Network behavior
- Filesystem/device behavior
- Private/local tooling files

## Android Shell Ownership Map

The future Android shell owns:

- App composition and navigation decisions in a future Android codebase.
- Rendering app-facing Aria state and results.
- Capturing user actions and expressing them as Aria intents.
- Holding Android screen-level state only when it is presentation state.
- Delegating platform callbacks and platform-specific calls to Android platform adapters.
- Delegating real playback/audio work to the future Android Player/audio layer.

The Android shell must not own queue state machines, now-playing policy, playback validation, provider readiness, offline/cache policy, permission/storage policy, backup/restore safety, result mapping, diagnostics safety, or heavy orchestration.

## Aria Core Ownership Map

Aria Core owns:

- App-facing contracts, results, errors, warnings, and safe serialization.
- Status, diagnostics, readiness, lifecycle previews, and result mapping.
- Media source, library, search, filter, activity, favorite, provider readiness, and capability models.
- Queue and now-playing contracts and services.
- Playback, renderer, and automation intents.
- Offline/cache/storage policy, radio models, stream quality/network/transcoding policy, and playback capability/readiness models.
- Profiles, preferences, backup/restore safety, snapshots, and fake end-to-end flows.
- Safety policies, validation, readiness, and platform-neutral orchestration.

Aria Core must never be bypassed for provider calls, policy decisions, safety decisions, lifecycle/apply decisions, queue/playback business rules, provider capability rules, or sanitized diagnostics/support data.

## Platform Adapter Ownership Map

Future Android platform adapters own:

- Android SDK calls.
- Permission dialogs and storage access calls.
- MediaSession, notifications, lock-screen, Bluetooth/headset, foreground service, Android Auto, widgets, lifecycle callbacks, and device integration.
- Mapping platform events into Aria-safe intents.
- Mapping Aria state into platform display/session metadata.
- Normalizing platform errors into safe Aria-facing or app-facing states.

Platform adapters must not call providers directly, call Anchor provider internals, use Anchor CLI as integration, duplicate Aria policy, or treat platform state as core truth.

## Android Player/Audio Ownership Map

Future Android Player/audio layer owns:

- Real playback execution.
- Playback engine choice, such as Media3/ExoPlayer or an alternative engine.
- Audio output routing implementation.
- Future playback engine adapter implementation.
- Possible custom/exclusive audio output research and prototypes.
- Any future JNI/NDK/AAudio/Oboe/USB audio bridge work approved by a separate spec.

It must report capability/readiness/results back through Aria models and keep driver logic out of Aria Core.

## Startup/Readiness Flow

Future flow:

```text
Android shell starts
  -> requests Aria status/readiness/app snapshot
  -> renders Aria readiness/status state
  -> delegates platform permission prompts only when Aria state indicates need
```

The shell must not call Anchor, providers, provider internals, or backend health endpoints directly.

## Diagnostics/Support Snapshot Flow

Future flow:

```text
User opens support/diagnostics
  -> Android shell requests Aria diagnostics and safe snapshot data
  -> Aria returns sanitized diagnostics/snapshot output
  -> Android displays or exports approved safe data only
```

The shell must not read raw logs, stack traces, credentials, raw paths, provider exceptions, or platform exception objects for display.

## Library/Search Flow

Future flow:

```text
User browses or searches
  -> Android shell calls Aria app-facing library/search services or models
  -> Aria applies source/provider capability and readiness rules
  -> Android renders success, empty, degraded, unavailable, or warning states
```

The shell must not query providers directly or implement provider capability rules.

## Queue/Now-playing Flow

Future flow:

```text
Android needs queue or now-playing state
  -> requests Aria queue/now-playing state
  -> renders immutable app-facing state
  -> sends queue/playback-related user actions as Aria intents
```

The shell must not maintain a separate queue truth, now-playing state machine, or playback availability policy.

## Playback Intent Flow

Future flow:

```text
UI action or platform control event
  -> Android shell/platform adapter maps action to an Aria playback intent
  -> Aria validates and returns preview/result/blocked/unavailable state
  -> future Android Player adapter acts only when allowed by a future spec
```

The shell must not call playback engines, MediaSession, Android Auto, notifications, lock-screen controls, Bluetooth/headset handlers, or audio APIs directly from UI screens.

## Offline/Cache/Radio/Quality/Capability Flow

Future flow:

```text
Android needs offline/cache/radio/quality/capability state
  -> consumes Aria policy/readiness/capability models
  -> renders state and safe explanations
  -> routes user requests back as Aria intents or future approved app-facing calls
```

Android shell must not implement destructive cache/download behavior, radio streaming, transcoding, network probing, playback engine behavior, or audio capability policy.

## Provider Readiness Flow

Future flow:

```text
Android needs provider/source availability
  -> consumes Aria provider/source readiness and capability models
  -> renders degraded/unavailable/compatible states
  -> routes account/provider actions through future approved adapter specs
```

Android shell must not call providers directly, call Anchor provider internals, or assume current Anchor supports multiple providers.

## Permission/Storage UX Flow

Future flow:

```text
Android screen needs permission/storage state
  -> consumes Aria platform-neutral permission/storage boundary state
  -> Android platform adapter performs OS permission/storage calls
  -> adapter reports result back through approved Aria-facing state
```

Aria owns policy consequences and safe explanation text. Android owns OS prompts and native result callbacks.

## Media Controls/Android Auto Handoff

Media controls, MediaSession, notifications, lock-screen controls, Bluetooth/headset controls, Android Auto, foreground service, and widgets are future platform surfaces. They should consume Aria state and emit Aria intents through Android platform adapters. They must not become independent sources of truth or direct provider/playback policy layers.

## Future Audio Output/Driver Boundary

Future bit-perfect/custom USB output, exclusive output, sample-rate switching, DAC control, JNI/NDK, AAudio, Oboe, and driver work remain in the Android Player/audio phase outside Aria Core. Android Player may research or implement these only under future dedicated specs. Aria Core may model capability/readiness/preference/conflict state but must not contain driver logic.

## Security Considerations

- Android UI must display only sanitized Aria errors, warnings, diagnostics, and snapshots.
- Android shell must not expose secrets, credentials, raw paths, raw logs, provider internals, stack traces, or personal library details.
- Platform adapters must sanitize or normalize native errors before UI display.
- Permission/storage prompts must be executed by Android platform code, not Aria Core.
- Android Auto, widgets, notifications, and lock-screen surfaces must use approved app-facing state only.

## Dependencies

None for Bloco 23.

Future Android implementation dependencies require separate specs.

## Risks

- Future Android UI could duplicate Aria policy or state machines.
- Future platform adapters could bypass Aria and call providers or playback engines directly.
- Future diagnostics/support flows could expose raw logs, paths, or provider exceptions.
- Future Android Player/audio work could leak driver or engine concepts into Aria Core.
- Future permission/storage UX could treat Android platform state as policy instead of input to Aria state.

## Rollback Strategy

Revert the Bloco 23 documentation/spec commit. No runtime behavior, source code, tests, dependencies, or public APIs are changed.

## Validation Plan

- `pwd`
- `git status --short --branch`
- `find docs aria/specs/features/android-shell-handoff aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
- `grep -R "android\.|androidx\.|Media3|ExoPlayer|MediaSession|Activity|Fragment|Compose|Kotlin|Gradle" -n src tests || true`
- `grep -R "JNI\|NDK\|AAudio\|Oboe\|UsbManager\|AudioTrack\|AudioManager" -n src tests || true`
- `grep -R "Android implementation\|implemented Android\|real MediaSession implemented\|Android Auto implemented\|Compose screen\|Activity implementation" -n docs aria/context aria/specs/features/android-shell-handoff || true`

## Behavior Budget

- New behaviors: documentation/handoff only.
- Public API changes: none.
- Files allowed: `aria/specs/features/android-shell-handoff/**`, `docs/**`, `aria/context/current.md`, `aria/context/delta.md`.
- Tests required: no new tests required unless existing validation requires it.
- Dependencies: none.
- Stop if: Android implementation becomes necessary; source code changes become necessary; playback engine implementation becomes necessary; UI/app shell implementation becomes necessary; provider integration becomes necessary.
