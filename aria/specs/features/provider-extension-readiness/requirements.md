# Requirements

## Status

Approved for Bloco 21 implementation.

## Problem

Aria needs a provider-agnostic foundation for future provider extensions without pretending current Anchor-backed integration already supports multiple providers. Existing provider-facing behavior is intentionally fake-first and boundary-driven. Bloco 21 must model descriptors, capabilities, compatibility, readiness, registry state, and adapter planning boundaries only.

## Goal

Add provider extension readiness contracts and deterministic local services so future provider work can be planned through public boundaries/adapters while Aria remains UI-independent, offline, and provider-agnostic.

## Non-goals

- No real provider integration.
- No provider authentication.
- No direct Navidrome, Jellyfin, Emby, Plex, Subsonic, or other provider integration.
- No Anchor provider internals.
- No assumption that Anchor is already multi-provider.
- No network calls.
- No provider mutation.
- No streaming.
- No playback.
- No Android/UI.
- No Bloco 22 Android real planning implementation.
- No filesystem traversal.

## Actors

- Aria Core service evaluating declared provider-extension descriptors.
- Future UI/app/player consuming Aria Core models only.
- Future provider adapter implementer using public boundaries/adapters.
- Tests using deterministic fake provider-extension scenarios.

## Functional requirements

- Define provider extension identity, references, summaries, kinds, status, warnings, requirements, unavailable reasons, capability summaries, readiness state, compatibility state, boundary policy, adapter descriptors, adapter readiness, discovery preview, discovery issues, and registry state.
- Implement `ProviderExtensionReadinessService` to validate descriptors, evaluate readiness, evaluate compatibility, enforce boundary policy, and build registry state from provided descriptors only.
- Implement `ProviderCapabilityDiscoveryService` to build preview-only capability discovery from declarations without opening network connections or touching provider internals.
- Support deterministic fake provider scenarios for current Anchor/Navidrome-focused boundary, future public-boundary provider, missing public boundary, provider requiring authentication, degraded capability, unsupported media capability, network discovery requirement, and invalid descriptor.
- Invalid descriptors must return safe `AriaResult` failures or unavailable readiness states with app-facing reasons.
- Authentication, network discovery, provider mutation, streaming, playback, and Android/UI requirements must be represented as unsupported/future requirements in this block.
- Current Anchor-backed integration must be represented as Navidrome-focused and not multi-provider.

## Non-functional requirements

- Deterministic, local, offline, stdlib-only implementation.
- Public API expansion limited to intentional provider extension readiness names.
- Safe serialized output through existing Aria contracts.
- No new dependencies.
- Tests must remain fake-first and must prove boundary preservation.

## Canonical Examples

- Given a future provider descriptor declares library and playlist capability, When readiness is evaluated, Then Aria returns a normalized provider capability summary.
- Given a provider descriptor is missing required public boundary information, When readiness is evaluated, Then Aria returns unavailable with a safe reason.
- Given current Anchor remains Navidrome-focused, When provider extension readiness is documented, Then Aria must not claim Anchor already supports multiple providers.
- Given a future Jellyfin-like provider is represented as a descriptor, When Aria evaluates it, Then Aria does not import or call Jellyfin APIs.
- Given a provider capability is degraded, When discovery preview runs, Then Aria returns warnings without opening network connections.
- Given UI needs provider information later, When it consumes provider readiness, Then it uses Aria Core models and does not call provider internals directly.
- Given a provider requires authentication, When readiness is evaluated in this block, Then Aria reports unsupported/future requirement and does not handle credentials.

## Edge cases

- Empty provider id, display name, adapter name, or boundary contract.
- Descriptor declares no capabilities.
- Descriptor declares authentication, network discovery, mutation, streaming, playback, or Android/UI requirements.
- Descriptor has degraded capability declarations.
- Descriptor uses current Anchor boundary wording that is Navidrome-focused only.
- Registry receives duplicate provider extension ids.
- Compatibility requires capabilities not declared by a provider.

## Acceptance criteria

- Spec contains context package used, Canonical Examples, Behavior Budget, Test Risk Matrix, and Delta update checklist.
- Provider extension contracts and adapter descriptor contracts are implemented.
- Readiness and discovery services are deterministic and descriptor-only.
- Fake provider-extension scenarios cover required cases.
- Tests cover descriptor validation, capability summaries, unavailable/degraded readiness, compatibility, registry behavior, boundary policy, no direct provider integration, and no auth/network/mutation/streaming/playback/Android behavior.
- Current Anchor limitation is represented honestly.
- No Bloco 22 behavior is implemented.

## Open questions

- Which public adapter protocol will a future real provider implementation use? Deferred.
- Whether Anchor will expose public provider boundaries beyond current Navidrome-focused integration. Deferred.
- Future credential handling model. Deferred and out of scope for this block.
