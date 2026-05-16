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

Repository direction updated: Aria Core is now documented as Aria Music Player Core, the modular app/player-facing core of a music player. The canonical local handoff is `docs/aria-core-handoff.md`.

Third-party names in research docs are factual references only. They do not imply Noqlen affiliation, endorsement, sponsorship, association, official support, or compatibility.

Next step after this commit: formal audit for Blocos 1-3. Do not start Bloco 4 until that audit passes.
