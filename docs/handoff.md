# Bloco 0 Handoff

Bloco 0 state: repository bootstrap, Aria Workflow context, spec templates, review templates, docs, minimal package, CLI doctor, and CLI tests.

Implemented scope:

- Repository structure and workflow contract.
- Public docs for architecture and safety boundaries.
- Aria context files for project, architecture, conventions, tools, forbidden patterns, context hygiene, and mistakes.
- Spec, agent, prompt, and review templates.
- Minimal safe local CLI with `doctor`.

Not implemented:

- Aria Core product contracts.
- Anchor integration.
- Android UI or SDK code.
- Playback, queues, now playing, cache/offline, media controls, Android Auto, or real music-library access.

Bloco 1 status: complete. Aria Core contracts implemented in `src/noqlen_aria/contracts.py` with source-agnostic `ControlClient`/`FakeControlClient`, plus comprehensive tests in `tests/test_contracts.py`. Anchor is a future adapter only. All 48 tests pass.

Bloco 2 status: complete. Five services implemented in `src/noqlen_aria/services.py` (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) plus `LifecycleIntentPreview`. `FakeControlClient` extended with 14 failure-injection/value-override hooks in `contracts.py`. `tests/test_services.py` has 76 tests. All 126 tests pass. No real Anchor, Navidrome, Android, playback, queue, or cache code exists. Next block: Bloco 3 (AnchorControlClient adapter, offline/dry-run only).

Bloco 3 status: complete. `AnchorControlClient` adapter implemented in `src/noqlen_aria/anchor_adapter.py` with `AnchorResultMapper` mapping layer. Adapter implements all seven `ControlClient` protocol methods using lazy optional `noqlen_anchor` import and constructor dependency injection. `send_lifecycle_intent` uses dry-run helpers only; apply-mode blocked with `APPLY_MODE_BLOCKED` error. `tests/test_anchor_adapter.py` has 103 tests using `unittest.mock`. All 229 tests pass. No real Anchor, Navidrome, Android, playback, queue, or cache code exists. Anchor public API callable names are based on planning-context candidates; confirmation against real `noqlen_anchor` pending. Next: formal Blocos 1–3 audit, then Bloco 4 (Android boundary contracts).

Repository-local handoff: `docs/aria-core-handoff.md` is the local source of truth for future Aria work. Future prompts should not reference chat-only handoff files. If Bloco 0 audit passed, the next step is Bloco 1 spec, not implementation.
