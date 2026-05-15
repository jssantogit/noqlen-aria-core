# Code Review Spec

Review implementations for:

- Active spec compliance.
- Non-goals compliance.
- Changed files match the spec.
- Validation evidence is present and appropriate.
- No private, local, generated, cache, log, or secret artifacts.
- No `git add .` usage.
- No Anchor internals.
- No direct Navidrome calls.
- No Android UI/SDK.
- No playback, queue, now playing, or cache/offline implementation in Bloco 0.
- No unrelated refactors or invented business rules.

Findings must be ordered by severity and include file/line references where possible.
