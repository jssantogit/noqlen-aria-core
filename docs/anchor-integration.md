# Anchor Integration

Anchor is not the center of Aria. Anchor is one `ControlClient` adapter/control-plane backend.

Aria Core must depend on contracts, not Anchor internals. It must not import Anchor provider internals, call provider internals, use Anchor CLI as the integration layer, call Navidrome directly, or call Navidrome through provider internals.

Future provider/media support should be capability-driven and adapter-based. Any future Anchor or provider integration requires an Aria spec before implementation.
