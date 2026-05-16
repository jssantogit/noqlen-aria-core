# Fake Hostility Checklist

Use this checklist to prevent `FakeControlClient` and future fake clients from becoming happy-path-only simulators.

Check relevant fake scenarios for:

- Helper unavailable.
- Payload partial.
- Enum/value unknown.
- Warning with sensitive/raw path data.
- Empty report.
- Timeout/latency-like failure.
- Unexpected type.
- Incompatible version/capability.
- Duplicated/conflicting data.
- Apply-like signal must be blocked.
- No fake scenario may require network or a real music library.

Expected reaction:

- No crash.
- Safe degraded state.
- Sanitized output.
- User-safe warning/error.
- Deterministic test behavior.
