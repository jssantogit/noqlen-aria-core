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

Next block: define the first product contract/spec before implementation. Do not start it from Bloco 0.

Repository-local handoff: `docs/aria-core-handoff.md` is the local source of truth for future Aria work. Future prompts should not reference chat-only handoff files. If Bloco 0 audit passed, the next step is Bloco 1 spec, not implementation.
