# Architecture

Noqlen Aria Core is core-first. It owns app/interface orchestration boundaries and exposes behavior to future UI adapters without becoming a UI itself.

Future flow:

`Future UI/App -> Aria Core -> Anchor Client -> Anchor Core API -> Navidrome`

Aria Core must not bypass Anchor. Anchor integration is expected to happen through a public Anchor client/API boundary in a later block.

Bloco 0 only creates repository structure, workflow context, and a safe local doctor command. It does not implement product contracts, playback, queues, now playing, offline/cache, Android integration, or Anchor integration.

Future UI must be thin and must not contain core business behavior.
