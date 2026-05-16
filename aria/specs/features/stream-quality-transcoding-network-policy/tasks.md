# Tasks

## Preparation checklist

- [x] Read required Standard context package and requested docs.
- [x] Create `requirements.md`.
- [x] Create `design.md`.
- [x] Initialize `tasks.md`.
- [x] Initialize `review.md`.
- [x] Verify canonical examples are present.
- [x] Verify Behavior Budget is present.
- [x] Verify Test Risk Matrix is present.

## TDD classification

- Required for stream quality decision behavior.
- Required for transcoding unavailable behavior.
- Required for network quality policy behavior.
- Required for offline quality fallback behavior.
- Required for invalid bitrate/bandwidth validation.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|------|------|-------------------|
| Negative bitrate/bandwidth validation | High | Safe `AriaResult` failures |
| Transcoding unavailable behavior | High | Unsupported source/input/output/bitrate and disabled policy |
| Network quality policy behavior | High | Offline/poor/degraded/good/excellent from explicit snapshots |
| Source unavailable/degraded quality behavior | High | Decision reasons and warnings, no crashes |
| No network/stream/transcoding/provider/Android behavior | High | Boundary tests/search validation |
| Stream quality preference mapping | Medium | High/medium/low/original/automatic decisions |
| Offline quality fallback | Medium | Offline preference without download/cache mutation |
| Model defaults and serialization | Medium | Defaults and `safe_serialize` compatibility |

## Behavior Budget check

- [x] New behavior limited to Bloco 16 policy-only decisions.
- [x] Public API expansion limited to intentional Bloco 16 names.
- [x] Allowed files only.
- [x] Tests planned for all required areas.
- [x] No dependencies.
- [x] Stop conditions not triggered.

## Implementation tasks

- [x] Add stream quality models/contracts.
- [x] Add transcoding policy models/contracts.
- [x] Add network quality models/contracts.
- [x] Add deterministic `QualityPolicyService`.
- [x] Add deterministic `TranscodingPolicyService`.
- [x] Add deterministic `NetworkQualityPolicyService`.
- [x] Add deterministic fake/policy scenarios.
- [x] Export intentional public names.
- [x] Add/update tests.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/stream-quality-transcoding-network-policy aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Required boundary searches.

## Review checklist

- [x] Spec created.
- [x] Implementation matches Bloco 16 spec.
- [x] No Bloco 17 behavior implemented.
- [x] No real transcoding exists.
- [x] No transcoder library added.
- [x] No network probing/calls exist.
- [x] No real streaming/playback exists.
- [x] No provider integration or provider internals added.
- [x] No Android/UI code added.
- [x] No audio driver/USB output work added.
- [x] Behavior Budget and Test Risk Matrix present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` concise.
- [x] No private/local/tooling files tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 16 complete status.
- [x] Update `aria/context/delta.md` with concise implementation and validation evidence.
- [x] Keep next step as Bloco 17 only after Bloco 16 is complete; do not start Bloco 17.
