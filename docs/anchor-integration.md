# Anchor Integration

Anchor is a future dependency boundary, not a Bloco 0 implementation dependency.

Aria Core will later consume Anchor through a public API/client boundary. It must not import Anchor provider internals, call provider internals, use Anchor CLI as the integration layer, or call Navidrome directly.

Bloco 0 documents this boundary only. Any future Anchor integration requires an Aria spec before implementation.
