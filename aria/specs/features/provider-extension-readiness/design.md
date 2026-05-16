# Design

## Summary

Bloco 21 adds provider extension readiness as descriptor/readiness modeling only. Aria evaluates caller-provided descriptors, capability declarations, and boundary policy flags locally. It does not integrate with providers, authenticate, discover over the network, call Anchor provider internals, or claim current Anchor is multi-provider.

## Context package

Standard.

## Context files read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/anchor-integration.md`
- `aria/specs/_template/**`
- Relevant files under `src/noqlen_aria/**` and `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core MVP v0.1.0 is complete. Blocos 18-20 are implemented. Audit 18-20 is deferred. Current Anchor-backed integration is optional, dry-run/offline, and Navidrome-focused. Future providers must be consumed through public boundaries/adapters.

## Files to create

- `aria/specs/features/provider-extension-readiness/requirements.md`
- `aria/specs/features/provider-extension-readiness/design.md`
- `aria/specs/features/provider-extension-readiness/tasks.md`
- `aria/specs/features/provider-extension-readiness/review.md`
- `src/noqlen_aria/provider_extensions.py`
- `tests/test_provider_extension_readiness.py`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Android/Kotlin/Java/Gradle files.
- UI/screen/navigation/player code.
- Anchor internals or provider packages.
- Private/local tooling files.
- Files outside the allowed scope unless validation generates ignored cache files.

## Data flow

`ProviderAdapterDescriptor` is provided by tests or future callers. `ProviderExtensionReadinessService` validates descriptor fields and `ProviderBoundaryPolicy`, normalizes capability declarations into `ProviderExtensionCapabilitySummary`, evaluates readiness and compatibility, and can aggregate descriptors into `ProviderExtensionRegistryState`. `ProviderCapabilityDiscoveryService` produces `ProviderCapabilityDiscoveryPreview` from the same declarations only.

## Provider extension model design

- `ProviderExtensionId`: normalized string id newtype.
- `ProviderExtensionRef`: id and display name.
- `ProviderExtensionSummary`: app-facing summary including kind, status, capabilities, readiness, and adapter readiness.
- `ProviderExtensionKind`: `ANCHOR_BACKED`, `PUBLIC_ADAPTER`, `LOCAL_DECLARATION`, `FUTURE_PROVIDER`.
- `ProviderExtensionStatus`: `READY`, `DEGRADED`, `UNAVAILABLE`, `UNSUPPORTED`, `PLANNED`.
- `ProviderExtensionCapabilitySummary`: supported/degraded/unsupported/future capabilities and helper membership checks.
- `ProviderExtensionReadinessState`: ready/degraded/status/reason/requirements/warnings/summary.
- `ProviderExtensionCompatibilityState`: compatible/missing/unsupported/future/degraded capabilities.
- `ProviderExtensionRequirement`: `PUBLIC_BOUNDARY`, `AUTHENTICATION`, `NETWORK_DISCOVERY`, `PROVIDER_MUTATION`, `STREAMING`, `PLAYBACK`, `ANDROID_UI`.
- `ProviderExtensionUnavailableReason`: safe blocked-state vocabulary.
- `ProviderExtensionWarning`: safe warning vocabulary.

## Provider adapter descriptor design

- `ProviderAdapterDescriptor`: declared provider extension metadata, capability sets, requirements, and boundary policy.
- `ProviderAdapterReadiness`: adapter-level readiness derived from descriptor validation and boundary policy.
- `ProviderBoundaryPolicy`: public boundary flags. It must require public boundary information and forbid direct provider calls, provider internals, Anchor provider internals, network discovery, authentication handling, mutation, streaming, playback, and Android/UI behavior in this block.
- `ProviderExtensionRegistryState`: deterministic aggregation of evaluated summaries, duplicate ids, warnings, and unavailable ids.
- `ProviderCapabilityDiscoveryIssue`: safe issue/warning record for preview-only discovery.

## Capability discovery preview rules

Discovery preview reads descriptor capability fields only. Degraded capabilities become warnings. Unsupported/future capabilities remain data. Requirements for authentication or network discovery become safe issues and never trigger credentials, network, provider calls, or filesystem traversal.

## Readiness/compatibility rules

Descriptors are ready only when identity, adapter name, public boundary contract, and required boundary policy are valid and no blocked requirements are present. Degraded capabilities produce degraded readiness but remain available. Missing public boundaries and blocked requirements produce unavailable or unsupported readiness. Compatibility compares requested capabilities with declared supported/degraded/unsupported/future sets only.

## Boundary policy rules

Boundary policy defaults to safe false/blocked values except direct provider calls and internals are represented as forbidden booleans. Readiness fails if public boundary information is missing or if the descriptor declares direct provider access, provider internals, Anchor provider internals, network discovery, authentication handling, mutation, streaming, playback, or Android/UI behavior.

## Error handling

Invalid descriptor structure returns `AriaResult(ok=False, AriaError(...))` where callers need a hard failure. Out-of-scope provider requirements return `AriaResult(ok=True, ProviderExtensionReadinessState(...))` with safe unavailable reasons and warnings.

## Security considerations

No credentials, tokens, passwords, endpoints, raw exceptions, paths, or provider internals are required or returned. Existing `AriaError`, `AriaWarning`, and `safe_serialize` keep app-facing data sanitized.

## Provider boundary considerations

Current Anchor-backed integration remains Navidrome-focused and optional. The Anchor scenario uses provider readiness language to record this limitation, not to claim multi-provider support. Future Jellyfin-like and Emby-like examples are descriptor names only and must not import or call those providers.

## Dependencies

None.

## Risks

- Accidentally implying current Anchor is multi-provider.
- Letting preview services become network/provider discovery.
- Naming future provider examples after real APIs in a way that suggests integration.
- Expanding into authentication or Android planning.

## Rollback strategy

Remove `provider_extensions.py`, its tests, public exports, spec directory, and concise context updates. No data migration is needed because this block adds local models/services only.

## Validation plan

- Run the requested full validation command set.
- Run provider/auth/network/Android/playback boundary searches.
- Run full pytest and compile checks.
- Confirm no private/local/tooling files are tracked.

## Behavior Budget

- New behaviors: provider extension readiness models; provider adapter descriptor models; provider capability discovery preview models; registry/readiness state models; deterministic local readiness/discovery services; explicit boundary policy checks.
- Public API changes: expose only intentional provider extension readiness names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/provider-extension-readiness/**`, `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` only if a tiny status note is needed.
- Tests required: descriptor validation; capability summary behavior; unavailable/degraded provider readiness; compatibility checks; registry state behavior; boundary policy checks; no direct provider integration; no network/provider mutation/streaming/playback/Android behavior.
- Dependencies: none.
- Stop if: real provider integration, provider authentication, direct Navidrome/Jellyfin/Emby calls, Anchor provider internals, network calls, streaming, or playback become necessary.
