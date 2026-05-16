# Tasks

## Preparation Checklist

- [x] Read required Standard context package files.
- [x] Read behavior budget and test risk matrix context.
- [x] Read handoff, backlog, architecture, safety, templates, prior review, relevant source, and relevant tests.
- [x] Create Bloco 15 spec before implementation.
- [x] Confirm Bloco 16 and Bloco 17 remain out of scope.

## TDD Classification

- Required for manual station validation.
- Required for unsupported stream kind behavior.
- Required for unavailable/degraded radio behavior.
- Required for favorite mutation blocking/read-only behavior.
- Required for no-network behavior.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|------|------|-------------------|
| Manual station validation | High | Valid, invalid URL, empty name, missing URL, local-only behavior |
| Unsupported stream kind behavior | High | HLS/DASH/Shoutcast unavailable with safe reason |
| Unavailable/degraded radio behavior | High | Unavailable reason, degraded warnings, deterministic fake scenarios |
| Favorite mutation blocking/read-only | High | Read state available; mutation unsupported/future-intent-only |
| No-network/no-streaming boundary | High | Source inspection and behavior tests for no requests/httpx/aiohttp/urllib/socket/playback/provider/Android |
| Metadata and ICY data-only state | Medium | Caller-provided metadata preserved, no parsing/network refresh |
| Artwork metadata state | Medium | Optional artwork preserved as metadata only |
| Model defaults and serialization | Medium | Defaults, safe serialization, public exports |

## Behavior Budget Check

- [x] New behavior limited to internet radio foundation models, deterministic service behavior, and fake scenarios.
- [x] Public API expansion limited to intentional radio names.
- [x] No dependencies added.
- [x] Tests planned for all required budget areas.
- [x] Stop conditions reviewed.

## Implementation Tasks

- [x] Add `src/noqlen_aria/internet_radio.py` with radio contracts and service.
- [x] Add deterministic fake radio scenarios.
- [x] Add top-level public exports.
- [x] Add tests for model defaults, validation, stream handles, availability, metadata, artwork, favorites, fake scenarios, and boundaries.
- [x] Update public export hardening test.
- [x] Update review and context state.

## Validation Checklist

- [x] Run `pwd`.
- [x] Run `git status --short --branch`.
- [x] Run required file listing.
- [x] Run `git diff --check`.
- [x] Run `python3 -m py_compile src/noqlen_aria/*.py`.
- [x] Run CLI help.
- [x] Run CLI doctor.
- [x] Run full pytest.
- [x] Run repository contamination check.
- [x] Run all required boundary search checks.

## Review Checklist

- [x] Spec created.
- [x] Implementation matches Bloco 15 spec.
- [x] No Bloco 16 behavior implemented.
- [x] No Bloco 17 behavior implemented.
- [x] No real radio streaming exists.
- [x] No HLS/DASH/Shoutcast client exists.
- [x] No ICY network parsing exists.
- [x] No network behavior exists.
- [x] No real playback or stream session exists.
- [x] No provider integration or mutation was added.
- [x] No Android/UI code was added.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta Update Checklist

- [x] Update `aria/context/current.md` with Bloco 15 completion and next-step guard.
- [x] Update `aria/context/delta.md` with concise change/evidence notes.
