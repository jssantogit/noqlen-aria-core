# Review

## Status

Stub — implementation not started. This review will be completed after Bloco 2 implementation.

## Summary

(To be filled after implementation.)

## Requirements coverage

(To be filled after implementation.)

| FR | Requirement | Status |
|----|-------------|--------|
| FR01 | `ResultMappingService` normalizes raw results | Not started |
| FR02 | `StatusService` composes server state | Not started |
| FR03 | `DiagnosticsService` collects warnings | Not started |
| FR04 | `LifecycleIntentService` validates/previews | Not started |
| FR05 | `ReadinessService` produces composite readiness | Not started |
| FR06 | Constructor injection of `ControlClient` | Not started |
| FR07 | All returns are `AriaResult`-wrapped | Not started |
| FR08 | Services work with `FakeControlClient` | Not started |
| FR09 | `FakeControlClient` failure-injection hooks | Not started |
| FR10 | `ResultMappingService` factory helpers | Not started |
| FR11 | `LifecycleIntentPreview` without execution | Not started |
| FR12 | `DiagnosticsService` warning thresholds | Not started |
| FR13 | Dedicated module under `src/noqlen_aria/` | Not started |
| FR14 | No network/filesystem/external process calls | Not started |

## Non-functional requirements

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | No extra deps beyond Python 3.11+ stdlib | Not started |
| NFR02 | Testable with `FakeControlClient` only | Not started |
| NFR03 | Simple attribute-assignment hooks | Not started |
| NFR04 | Bloco 1 contract types as I/O | Not started |
| NFR05 | Stable, documented public names | Not started |
| NFR06 | Importable without side effects | Not started |
| NFR07 | Deterministic tests | Not started |

## Files changed

(To be filled after implementation.)

## Validation performed

(To be filled after implementation.)

## Non-goals check

| Non-goal | Status |
|---|---|
| No real Anchor adapter | (to verify) |
| No media source integration | (to verify) |
| No Navidrome/Jellyfin/Emby integration | (to verify) |
| No playback engine | (to verify) |
| No queue implementation | (to verify) |
| No now playing implementation | (to verify) |
| No cache/offline implementation | (to verify) |
| No Android SDK or UI | (to verify) |
| No CLI expansion | (to verify) |
| No real music library access | (to verify) |

## Known limitations

(To be filled after implementation.)

## Follow-up items

- Bloco 3: `AnchorControlClient` adapter (offline/dry-run only).
- Bloco 3+: Real `ControlClient` integration with Anchor public API.
- Bloco 4: Android boundary contracts.
- Future: `MediaSourceClient` boundary for library/search/stream/playlists.
- Future: Lifecycle intent execution with explicit apply-mode protection (currently preview-only).

## Aria context updates needed

(To be filled during implementation if any context files need updating.)

## Spec approval

- [ ] Spec reviewed and approved for implementation.
