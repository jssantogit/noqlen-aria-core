# Study Local Repositories Prompt

Inspect nearby Noqlen repositories read-only and return sanitized workflow lessons.

Rules:

- Read-only only.
- Do not modify inspected repositories.
- Do not run tests, builds, formatters, installers, or commands that write artifacts.
- Do not stage, commit, publish, merge, or refactor inspected repositories.
- Do not include absolute local paths in the final report.
- Do not copy secrets, private data, personal paths, lyrics, fingerprints, real music-library paths, or full local configs.
- Recommend workflow improvements only; do not perform retrofit work unless a separate task explicitly requests it.

Inspect:

- Top-level structure.
- Docs, context, specs, ADRs, tests, CI, release files, audits, and handoffs.
- CLI/core, service/core, provider/core, app/core, or player/core boundaries.
- Fake-first, dry-run-first, validation, audit, and repository hygiene signals.

Return:

- Repositories found.
- Sanitized structure summary.
- Workflow strengths.
- Workflow gaps.
- Risks.
- Suggested Aria workflow updates.
