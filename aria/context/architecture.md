# Architecture Context

Aria Core should expose an app/player-facing API facade while keeping UI adapters thin.

Repository-local handoff and broader architecture context live in `docs/aria-core-handoff.md`.

Core control-plane integration belongs behind a source-agnostic `ControlClient` boundary. Anchor is one future adapter (`AnchorControlClient`), not the conceptual center of Aria Core. Aria must use the control client through public API/client contracts and must not call Navidrome directly, import Anchor provider internals, or use Anchor CLI as the integration layer.

Development is fake-first: define contracts, fakes, and local validation before real integration. Tests must not require network, real music libraries, Anchor, or Navidrome.

App-facing state models should be stable, explicit, and independent from UI frameworks.

No Android SDK, playback, UI, cache/offline, or queue implementation is allowed in Bloco 1. Android-specific concepts must remain future adapter boundaries until explicitly specified.

## Future Vocabulary

Future boundary/service vocabulary is canonical in `aria/context/future-product-context.md`. Do not implement these names in Bloco 0.

- `PlaybackEngine`
- `MediaSessionBridge`
- `AndroidStorageBridge`
- `QueueService`
- `LibraryPresentationService`
- `OfflineCachePolicyService`
- `AudioCapabilitiesService`

They must not appear as source code classes or services yet.
