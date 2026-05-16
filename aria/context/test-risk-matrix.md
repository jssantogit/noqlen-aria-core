# Test Risk Matrix

Use this matrix to choose proportional validation for each task.

## High risk

- Safety rules.
- Dry-run/apply boundaries.
- Sanitization.
- Result mapping.
- Lifecycle intents.
- Permission/storage state.
- Integration adapter behavior.
- Missing dependency behavior.

Expectations:

- Requires negative tests.
- Should use TDD where practical.
- Must prove failure paths are safe and deterministic.

## Medium risk

- View-state defaults.
- Fake scenarios.
- Readiness/diagnostics service mapping.
- Public exports.

Expectations:

- Needs deterministic unit tests.
- Should cover representative success and failure/default behavior.

## Low risk

- Docs.
- Comments.
- Mechanical renames.
- CLI smoke text.

Expectations:

- Needs proportional validation.
- May use docs checks, smoke commands, or targeted tests when source behavior is unaffected.
