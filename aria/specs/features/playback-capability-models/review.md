# Review

## Summary

Bloco 17 (Playback Capability Models) spec and implementation are complete, including the fade capability follow-up. Implementation adds playback capability, fade-in/fade-out capability and timing preference, audio output route/device readiness, USB DAC/exclusive output, sample-rate/bit-depth/format support, bit-perfect readiness, playback quality preference, deterministic services, and fake capability scenarios in `src/noqlen_aria/playback_capabilities.py`.

No real playback, audio processing, volume automation, audio driver, USB driver, Android audio API, JNI/NDK, AAudio/Oboe, Media3/ExoPlayer, MediaSession, real bit-perfect output, sample-rate switching, DAC control, gain application, fade/crossfade/gapless execution, provider integration, network behavior, filesystem/device traversal, or DSP/EQ implementation was added.

## Requirements coverage

All functional requirements FR-01 through FR-16 are implemented.

| Area | Status |
|------|--------|
| Gapless/loudness/ReplayGain/crossfade models | Implemented |
| Fade-in/fade-out capability and timing models | Implemented |
| Bit-perfect conflict with signal-altering fade/crossfade | Implemented |
| Bit-perfect capability/readiness models | Implemented |
| Audio output route/device/readiness models | Implemented |
| USB DAC and exclusive output models | Implemented |
| Sample-rate/bit-depth/format support models | Implemented |
| Playback quality preference mapping | Implemented |
| Deterministic services | Implemented |
| Fake capability scenarios | Implemented |
| Boundary preservation | Verified |

## Context package used

Standard.

## Files changed

Spec created:
- `aria/specs/features/playback-capability-models/requirements.md`
- `aria/specs/features/playback-capability-models/design.md`
- `aria/specs/features/playback-capability-models/tasks.md`
- `aria/specs/features/playback-capability-models/review.md`

Source created:
- `src/noqlen_aria/playback_capabilities.py`

Tests created:
- `tests/test_playback_capability_models.py`

Source/tests modified:
- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`

Context updated:
- `aria/context/current.md`
- `aria/context/delta.md`

## Validation performed

- Targeted pre-validation: `python3 -m py_compile src/noqlen_aria/*.py && PYTHONPATH=src python3 -m pytest tests/test_playback_capability_models.py tests/test_mvp_hardening.py` — passed, 31 tests.
- `pwd` — passed.
- `git status --short --branch` — expected Bloco 17 follow-up changes only before commit.
- `find src/noqlen_aria tests aria/specs/features/playback-capability-models aria/context -maxdepth 6 -type f | sort` — files present.
- `git diff --check` — passed.
- `python3 -m py_compile src/noqlen_aria/*.py` — passed.
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — passed.
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — passed.
- `python3 -m pytest` — passed, 836 tests.
- Repository contamination check — clean.
- Required boundary searches — no forbidden implementation found.

## Validation notes

Boundary search matches for existing Bloco 16 transcoding vocabulary, generated ignored `__pycache__` files, and Bloco 17 test/spec boundary vocabulary are expected. No forbidden implementation was found.

## Non-goals check

| Non-goal | Status |
|---|---|
| No real playback | Pass |
| No real fade/audio processing or volume automation | Pass |
| No real audio/USB driver | Pass |
| No Android/JNI/NDK/AAudio/Oboe | Pass |
| No Media3/ExoPlayer/MediaSession | Pass |
| No real bit-perfect/sample-rate switching/DAC control | Pass |
| No gain/crossfade/gapless execution | Pass |
| No provider/network/filesystem/device behavior | Pass |
| No DSP/EQ implementation | Pass |
| No Audit 14-17 or Bloco 18 work | Pass |

## Behavior Budget result

All budget constraints respected.

| Constraint | Status |
|---|---|
| New behavior limited to capability/readiness/preference models/services | Pass |
| Public API expansion intentional | Pass |
| Files allowed | Pass |
| Tests required | Pass |
| Dependencies: none | Pass |
| Stop conditions | Not triggered |

## Risk/test coverage result

| Area | Classification | Result |
|------|----------------|--------|
| Bit-perfect readiness | High | Covered |
| Fade and bit-perfect signal-processing conflict | High | Covered |
| USB DAC/exclusive output | High | Covered |
| Sample-rate/bit-depth support | High | Covered |
| Unavailable/degraded output route | High | Covered |
| No real driver/playback/API behavior | High | Covered |
| Gapless/crossfade/loudness defaults and serialization | Medium | Covered |
| Public exports | Medium | Covered |

## Delta updated?

Yes. `aria/context/current.md` and `aria/context/delta.md` updated.

## Fake-hostility checks applied?

Yes. Fake scenarios are deterministic, local, explicit-data only, and do not call network, filesystem, providers, playback, Android/platform APIs, external processes, or devices.

## Risks remaining

- Future Android Player layers must continue treating Bloco 17 state as declarations/readiness only.
- Future real bit-perfect validation remains outside Aria Core.

## Required fixes

None.

## Optional improvements

None.

## Final status

Pass.

## Known limitations

- No real playback, audio output, bit-perfect output, sample-rate switching, USB driver, platform bridge, gain processing, crossfade execution, gapless execution, or provider integration is implemented.

## Follow-up tasks

- Audit 14-17 remains deferred until explicitly requested.
- Bloco 18 must not start in this task.

## Aria context updates needed

Completed.
