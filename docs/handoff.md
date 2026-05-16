# Bloco 0 Handoff

Bloco 0 state: repository bootstrap, Aria Workflow context, spec templates, review templates, docs, minimal package, CLI doctor, and CLI tests.

Implemented scope:

- Repository structure and workflow contract.
- Public docs for architecture and safety boundaries.
- Aria context files for project, architecture, conventions, tools, forbidden patterns, context hygiene, and mistakes.
- Spec, agent, prompt, and review templates.
- Minimal safe local CLI with `doctor`.

Not implemented:

- Android UI or SDK code.
- Playback engine, queues, now playing, cache/offline/download, media controls, Android Auto, or real music-library access.
- Provider hard coupling or real provider integrations.

Bloco 1 status: complete. Aria Core contracts implemented in `src/noqlen_aria/contracts.py` with source-agnostic `ControlClient`/`FakeControlClient`, plus comprehensive tests in `tests/test_contracts.py`.

Bloco 2 status: complete. Five services implemented in `src/noqlen_aria/services.py` (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) plus `LifecycleIntentPreview`. `FakeControlClient` extended with failure-injection/value-override hooks.

Bloco 3 status: complete. `AnchorControlClient` adapter implemented in `src/noqlen_aria/anchor_adapter.py` with `AnchorResultMapper` mapping layer. Adapter uses lazy optional `noqlen_anchor` import and constructor dependency injection. `send_lifecycle_intent` uses dry-run helpers only; apply-mode is blocked.

Bloco 4 status: complete. Android/player boundary contracts implemented in `src/noqlen_aria/android_boundaries.py` with 9 bridge protocols, supporting types, `AndroidBoundarySnapshot`, and 9 deterministic fake implementations. 129 tests in `tests/test_android_boundaries.py`; 358 total tests pass.

Bloco 5 status: planning artifacts complete. Minimal UI Shell boundary documentation created in `docs/ui-shell-boundary.md` and referenced from `docs/architecture.md` and `docs/android-boundary.md`. The docs define the future thin UI/app shell role, Aria Core role, platform adapter role, allowed state/intent flows, anti-coupling rules, and conceptual examples. No UI or source implementation exists.

Repository direction updated: Aria Core is now documented as Aria Music Player Core, the modular app/player-facing core of a music player. The canonical local handoff is `docs/aria-core-handoff.md`.

Workflow vNext status: future tasks should start from `aria/context/current.md`, `aria/context/delta.md`, and the context package policy before reading large handoff context.

Third-party names in research docs are factual references only. They do not imply Noqlen affiliation, endorsement, sponsorship, association, official support, or compatibility.

Next step after this commit: Bloco 6 spec. Do not implement UI, Android, playback, queue, now playing, cache, or provider integration without a dedicated future spec.
