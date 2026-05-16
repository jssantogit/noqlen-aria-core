# Tasks

## Preparation checklist

- [x] Read required Standard context.
- [x] Review scope boundaries and repository hygiene.
- [x] Review Bloco 14-16 review patterns.
- [x] Review existing source/test/export patterns.
- [x] Create spec before implementation.

## Test Risk Matrix

| Area | Risk | TDD classification | Required coverage |
|------|------|--------------------|-------------------|
| Bit-perfect readiness behavior | High | Required | Available, blocked by non-exclusive/system audio, unsupported sample rate, degraded/unavailable exclusive output |
| USB DAC/exclusive output capability behavior | High | Required | USB DAC route declared available, exclusive unavailable blocks/degrades readiness |
| Sample-rate/bit-depth compatibility | High | Required | Matching, mismatch, invalid negative values |
| Unavailable/degraded output route behavior | High | Required | Route unavailable/degraded, device unavailable/degraded warnings |
| No real driver/playback/API behavior | High | Required | Source inspection/search tests and validation searches |
| Fade and bit-perfect signal-processing conflict | High | Required | Fade-in, fade-out, invalid timing, unavailable state, signal-processing disabled reason |
| Gapless/crossfade/loudness defaults and serialization | Medium | Recommended | Available/unavailable defaults, ReplayGain present/missing, safe serialization |
| Public exports | Medium | Recommended | Module `__all__` and top-level export set updated intentionally |
| Spec/docs/context updates | Low | N/A | Review checklist and concise current/delta updates |

## Behavior Budget check

- [x] Budget defined in `design.md`.
- [x] No dependencies allowed.
- [x] Only allowed files planned.
- [x] Stop conditions documented.
- [x] Re-check after implementation.

## Implementation tasks

- [x] Add `src/noqlen_aria/playback_capabilities.py`.
- [x] Implement playback capability enums/dataclasses.
- [x] Implement fade-in/fade-out capability and timing models.
- [x] Implement audio output readiness enums/dataclasses.
- [x] Implement `PlaybackCapabilityService`.
- [x] Extend `PlaybackCapabilityService` for fade and signal-processing conflict evaluation.
- [x] Implement `AudioOutputCapabilityService`.
- [x] Implement deterministic `FakePlaybackCapabilityScenarios`.
- [x] Update public exports in `src/noqlen_aria/__init__.py`.
- [x] Add tests in `tests/test_playback_capability_models.py`.
- [x] Update `tests/test_mvp_hardening.py` expected exports.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/playback-capability-models aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] repository contamination check
- [x] required Android/audio/provider/network/filesystem/DSP boundary searches

## Review checklist

- [x] Spec created.
- [x] Implementation matches Bloco 17 spec.
- [x] No Audit 14-17 work started.
- [x] No Bloco 18 behavior implemented.
- [x] No real playback exists.
- [x] No real audio driver/USB output code exists.
- [x] No Android/JNI/NDK/AAudio/Oboe code exists.
- [x] No Media3/ExoPlayer/MediaSession exists.
- [x] No real bit-perfect/sample-rate switching/DAC control exists.
- [x] No DSP/EQ exists.
- [x] No provider integration or provider internals added.
- [x] No network/filesystem/device behavior exists.
- [x] Behavior Budget and Test Risk Matrix present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` concise.
- [x] No private/local/tooling files tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 17 complete status.
- [x] Update `aria/context/delta.md` with concise implementation/evidence.
- [x] Keep Audit 14-17 as next step and not started.
- [x] Do not start Bloco 18.
