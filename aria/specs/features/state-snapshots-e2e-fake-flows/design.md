# Design

## Summary

Bloco 20 adds a local-only snapshot module with structured state snapshots, conservative redaction, structural diffs, and deterministic fake end-to-end flow traces. The implementation uses in-memory models and existing fake/local services only.

## Context package

Standard.

## Context files read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `aria/specs/_template/**`
- Bloco 18 and 19 review files
- Relevant `src/noqlen_aria/**` and `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core uses dataclass model contracts, `AriaResult` safety wrappers, deterministic local services, fake scenario classes, and explicit top-level public exports. Blocos 18 and 19 added local profile/preference/backup and smart playlist foundations. Bloco 20 completes the Profiles/Smart/Snapshots group before Audit 18-20.

## Files to create

- `src/noqlen_aria/state_snapshots.py`
- `tests/test_state_snapshots_e2e_fake_flows.py`
- `aria/specs/features/state-snapshots-e2e-fake-flows/requirements.md`
- `aria/specs/features/state-snapshots-e2e-fake-flows/design.md`
- `aria/specs/features/state-snapshots-e2e-fake-flows/tasks.md`
- `aria/specs/features/state-snapshots-e2e-fake-flows/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Provider adapters beyond public exports.
- Android, Kotlin, Java, Gradle, UI, player, background job, private/local tooling, package publishing, or tag files.
- Bloco 21 provider extension readiness files or behavior.

## Data flow

Snapshot flow: caller-provided state objects -> section selection -> safe serialization -> redaction policy -> validation -> `AriaStateSnapshot` inside `AriaSnapshotResult`.

Diff flow: two `AriaStateSnapshot` instances -> section key comparison -> structural value comparison -> ordered `AriaSnapshotDiffEntry` values -> `AriaSnapshotDiff`.

Fake flow: `FakeFlowRunner.run(scenario)` -> existing fake/local service composition -> ordered `FakeFlowStepResult` values -> `FakeFlowTrace` -> `FakeFlowResult`.

## Snapshot model design

Proposed names:
- `AriaSnapshotId`
- `AriaSnapshotScope`
- `AriaSnapshotMetadata`
- `AriaSnapshotSection`
- `AriaStateSnapshot`
- `AriaSnapshotRedactionPolicy`
- `AriaSnapshotValidationIssue`
- `AriaSnapshotResult`
- `AriaSnapshotDiff`
- `AriaSnapshotDiffEntry`
- `AriaSnapshotUnavailableReason`

`AriaSnapshotScope` includes section labels such as `PROFILE`, `PREFERENCES`, `LIBRARY`, `QUEUE`, `NOW_PLAYING`, `DIAGNOSTICS`, `SMART_PLAYLISTS`, `RADIO`, `OFFLINE_CACHE`, `QUALITY`, and `CAPABILITIES`. `AriaStateSnapshot` stores metadata, sections, validation issues, unavailable reasons, and flags showing sanitization occurred.

## Snapshot redaction/sanitization rules

- Exclude secret-like keys containing password, token, secret, credential, authorization, api_key, or apikey.
- Redact raw personal paths including `/home/`, `/Users/`, `C:\Users`, and path-labeled values.
- Redact raw logs, tracebacks, multiline exception text, and credential-like values.
- Convert unsupported objects to a safe unavailable placeholder.
- Preserve app-facing dataclass, enum, tuple, list, dict, string, numeric, bool, and null structures after sanitization.

## Snapshot diff rules

- Compare sanitized structural values only.
- Report missing, added, and changed sections.
- Preserve deterministic ordering by section name.
- Do not perform provider, semantic, fuzzy, playback, or filesystem comparisons.

## Fake flow model design

Proposed names:
- `FakeFlowId`
- `FakeFlowScenario`
- `FakeFlowStep`
- `FakeFlowStepKind`
- `FakeFlowStepResult`
- `FakeFlowTrace`
- `FakeFlowResult`
- `FakeFlowValidationIssue`
- `FakeFlowUnavailableReason`

`FakeFlowRunner` accepts a `FakeFlowScenario` and runs one of the approved deterministic scenarios. Step results include payloads and explicit safety booleans for provider, network, filesystem, playback, Android, provider mutation, and real queue mutation boundaries.

## Fake flow trace/reporting rules

- Step order is fixed per scenario.
- Each step has a deterministic index, kind, label, status, payload, issues, and unavailable reasons.
- Failures are represented as blocked or degraded step results, not exceptions for expected fake state limitations.
- Flow result summarizes success, degraded state, and trace.

## Error handling

Invalid snapshot input, invalid scopes, unsupported flow ids, and failed local service composition return `AriaResult(ok=False, error=AriaError(...))` or safe result models with issues where partial output is useful. No raw exception details are exposed.

## Security considerations

Snapshots and traces must not preserve secrets, credentials, raw paths, raw logs, private music-library details, provider internals, or personal paths. Sanitization is conservative and may redact safe-looking values if they match unsafe markers.

## Provider boundary considerations

Fake flows use existing fake/local data and services only. They do not call real providers, Anchor provider internals, direct Navidrome/Jellyfin/Emby integrations, Anchor CLI, provider playlist creation, provider mutation, stream resolution, or Bloco 21 provider extension behavior.

## Deterministic execution rules

- Fixed snapshot metadata defaults unless caller provides metadata.
- Fixed fake scenario ids and step order.
- No wall-clock dependency for fake flow results.
- No randomization without deterministic seeds already present in existing services.
- No network, filesystem, playback, Android, background, or external process calls.

## Dependencies

None.

## Risks

- Redaction may miss future unsafe markers.
- Fake flows may be mistaken for real automation if boundaries are unclear.
- Snapshot models may become too broad if future blocks add provider extension behavior prematurely.

## Rollback strategy

Remove `state_snapshots.py`, tests, public exports, and the Bloco 20 spec/context updates. No durable data migration is needed because no persistence is added.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/state-snapshots-e2e-fake-flows aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Required repository contamination and boundary searches from the task prompt.

## Behavior Budget

- New behaviors: state snapshot models; snapshot redaction/sanitization policy; snapshot validation and diff models; deterministic fake flow models; fake flow runner for in-memory/local service composition; fake flow trace/result reporting.
- Public API changes: expose only intentional snapshot/fake-flow names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, this spec directory, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: snapshot creation, redaction, validation, diff, required fake flows, safe failure/degraded fake flow, and no provider/network/filesystem/playback/Android behavior.
- Dependencies: none.
- Stop if: real provider integration, filesystem persistence, playback, UI/demo app, Android, background scheduling, or Bloco 21 behavior becomes necessary.
