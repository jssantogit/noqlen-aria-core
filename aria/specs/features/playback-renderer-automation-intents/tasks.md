# Tasks

## Preparation checklist

- [x] Read context files (current.md, delta.md, scope-boundaries.md, context-packages.md, future-product-context.md, behavior-budget.md, test-risk-matrix.md).
- [x] Read existing specs (media-source, library, queue, now-playing reviews).
- [x] Read existing source (contracts.py, queue.py, now_playing.py, __init__.py).
- [x] Read existing tests (test_queue_foundation.py, test_now_playing_foundation.py, test_mvp_hardening.py).
- [x] Create spec directory.
- [ ] Create spec files (requirements.md, design.md, tasks.md, review.md).

## TDD classification

- **Required** for playback intent validation (play, pause, resume, stop, skip, seek).
- **Required** for blocked/unavailable behavior.
- **Required** for seek validation (negative position, beyond duration).
- **Required** for renderer unavailable/unsupported behavior.
- **Required** for automation intent validation.
- **Recommended** for model defaults and serialization.

## Test Risk Matrix

| Risk Level | Area | Coverage Requirement |
|-----------|------|---------------------|
| High | Playback intent validation | Positive + negative tests for every intent type |
| High | Blocked/unavailable handling | All idle/unavailable/blocked state transitions |
| High | Seek validation | Negative position, beyond duration, at boundary |
| High | Renderer selection | Available, unavailable, unsupported capability |
| High | Automation intent validation | Safe, boundary, unsafe sources |
| Medium | Model defaults | Default values produce no side effects |
| Medium | Serialization | safe_serialize produces valid JSON |
| Medium | Public exports | __init__.py and __all__ expose only intentional names |

## Behavior Budget check

Confirms each task in this spec stays within the budget defined in `design.md`. Budget items reference `aria/context/behavior-budget.md`.

- [ ] New behaviors: 5 (playback models, renderer models, automation models, preview service, blocked/unavailable handling).
- [ ] Public API changes: ~25 new export names.
- [ ] Files allowed: `src/noqlen_aria/playback_intents.py`, `tests/test_playback_renderer_automation_intents.py`, spec files, context/doc updates.
- [ ] Tests required: covered by TDD classification above.
- [ ] Dependencies: none external.
- [ ] Stop: does not require real playback, stream resolution, Android, provider integration.

## Implementation tasks

1. Create `src/noqlen_aria/playback_intents.py` with:
   - Playback intent models (PlaybackIntent, PlaybackIntentType, PlaybackIntentResult, PlaybackCommandPreview, PlaybackIntentValidationIssue, PlaybackBlockedReason, SeekTarget, SkipDirection).
   - Renderer models (RendererId, RendererRef, RendererType, RendererAvailabilityState, RendererCapabilitySummary, RendererSelectionIntent, RendererSelectionResult).
   - Automation models (AutomationIntent, AutomationIntentType, AutomationIntentSource, AutomationIntentResult, AutomationSafetyLevel).
   - PlaybackIntentService with preview() and validate().
   - RendererIntentService with validate_selection().
   - AutomationIntentService with validate().
   - `__all__` exports.

2. Create `tests/test_playback_renderer_automation_intents.py` with tests for:
   - Play idle/unavailable/ready/paused/resumable for every intent type.
   - Blocked unavailable media.
   - Seek validation (negative, beyond duration, at boundary).
   - Skip next/previous with queue bounds.
   - Renderer available/unavailable/unsupported capability.
   - Automation intent validation (safe/unsafe sources).
   - Side-effect-free previews.
   - Model defaults and serialization.
   - No provider/network/filesystem/playback/Android dependency.

3. Update `src/noqlen_aria/__init__.py`: add new exports and `__all__` entries.

4. Update `tests/test_mvp_hardening.py`: add new expected export names.

5. Update `aria/context/current.md`: record Bloco 13 as the active spec.

6. Update `aria/context/delta.md`: record Bloco 13 completion.

7. Update `docs/handoff.md` if a tiny status note is needed.

8. Update `aria/specs/features/playback-renderer-automation-intents/review.md` after implementation.

## Validation checklist

- [ ] `pwd`
- [ ] `git status --short --branch`
- [ ] `find src/noqlen_aria tests aria/specs/features/playback-renderer-automation-intents aria/context -maxdepth 6 -type f | sort`
- [ ] `git diff --check`
- [ ] `python3 -m py_compile src/noqlen_aria/*.py`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [ ] `python3 -m pytest`
- [ ] Repository contamination check
- [ ] Provider integration search
- [ ] Network/filesystem search
- [ ] Android/Media3 search
- [ ] Offline/cache/smart-playlist search
- [ ] No real playback boundaries crossed

## Review checklist

- [ ] All 8 canonical examples have passing tests.
- [ ] All edge cases have test coverage.
- [ ] Behavior Budget not exceeded.
- [ ] No non-goals violated.
- [ ] All exports intentional.
- [ ] No provider/network/filesystem/Android/playback code.
- [ ] Tests pass.
- [ ] Context files updated.

## Delta update

- Update `aria/context/delta.md` after implementation.

## Subagent packages

Not needed. Single-file module with models and services.
