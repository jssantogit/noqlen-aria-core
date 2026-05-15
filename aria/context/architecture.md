# Architecture Context

Aria Core should expose an app-facing API facade while keeping UI adapters thin.

Anchor integration belongs behind an `AnchorClient` boundary in a future block. Aria must use Anchor through public API/client contracts and must not call Navidrome directly, import Anchor provider internals, or use Anchor CLI as the integration layer.

Development is fake-first: define contracts, fakes, and local validation before real integration. Tests must not require network, real music libraries, Anchor, or Navidrome.

App-facing state models should be stable, explicit, and independent from UI frameworks.

No Android SDK is allowed in early blocks. Android-specific concepts must remain future adapter boundaries until explicitly specified.

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
