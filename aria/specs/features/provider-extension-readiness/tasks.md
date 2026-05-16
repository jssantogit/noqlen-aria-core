# Tasks

## Preparation checklist

- [x] Read required Standard context package and requested docs.
- [x] Inspect existing source and test patterns.
- [x] Create and review spec before implementation.
- [x] Implement only the approved spec.

## TDD classification

- Required for descriptor validation.
- Required for unavailable/degraded readiness behavior.
- Required for boundary policy behavior.
- Required for Anchor-not-multi-provider assumption guard.
- Required for no direct provider import/call behavior.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|---|---|---|
| Descriptor validation | High | Invalid id/name/boundary fields return safe errors or unavailable readiness |
| Boundary policy enforcement | High | Direct provider calls, internals, auth, network, mutation, streaming, playback, Android/UI are blocked |
| Anchor limitation honesty | High | Current Anchor scenario remains Navidrome-focused and not multi-provider |
| No direct provider import/call | High | Source inspection and tests show no Jellyfin/Emby/Navidrome provider calls |
| Readiness and compatibility | High | Available, unavailable, degraded, unsupported, future requirement behavior |
| Discovery preview | High | Descriptor-only warnings/issues, no network |
| Registry state | Medium | Deterministic aggregation, duplicate ids, unavailable ids |
| Model defaults and serialization | Medium | Defaults serialize safely and exports are intentional |
| Spec/context updates | Low | Review and delta checklist |

## Behavior Budget check

- [x] New behaviors limited to Bloco 21 provider extension readiness foundations.
- [x] Public API expansion limited to intentional names.
- [x] No new dependencies.
- [x] Allowed files only.
- [x] Stop conditions not triggered during design.

## Implementation tasks

- [x] Implement provider extension readiness contracts.
- [x] Implement provider adapter descriptor contracts.
- [x] Implement `ProviderExtensionReadinessService`.
- [x] Implement `ProviderCapabilityDiscoveryService`.
- [x] Add deterministic fake provider-extension scenarios.
- [x] Update public exports.
- [x] Add/update tests for required behaviors and boundaries.

## Subagent packages

- None used.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/provider-extension-readiness aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Required provider/auth/network/Android/playback boundary searches.

## Review checklist

- [x] Spec created.
- [x] Implementation matches the Bloco 21 spec.
- [x] No Bloco 22 behavior implemented.
- [x] No real provider integration exists.
- [x] No direct provider imports/calls exist.
- [x] No Anchor provider internals are used.
- [x] No assumption that current Anchor is multi-provider was introduced.
- [x] No provider auth/network/streaming/playback behavior exists.
- [x] No Android/UI code was added.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 21 completion and active spec status.
- [x] Update `aria/context/delta.md` with concise implementation and validation evidence.
- [x] Confirm Audit 18-20 remains deferred and Bloco 22 was not started.
