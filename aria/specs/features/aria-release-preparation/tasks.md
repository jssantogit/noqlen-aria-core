# Tasks

## Preparation checklist

- [x] Read `AGENTS.md`.
- [x] Read `aria/context/current.md`.
- [x] Read `aria/context/delta.md`.
- [x] Read `aria/context/context-packages.md`.
- [x] Read `aria/context/scope-boundaries.md`.
- [x] Read `aria/context/repository-hygiene.md`.
- [x] Read `aria/context/behavior-budget.md`.
- [x] Read `aria/context/test-risk-matrix.md`.
- [x] Read `docs/aria-core-handoff.md`.
- [x] Read `docs/architecture.md`.
- [x] Read `docs/safety.md`.
- [x] Read `docs/anchor-integration.md`.
- [x] Read `docs/android-boundary.md`.
- [x] Read `docs/ui-shell-boundary.md`.
- [x] Read `docs/handoff.md`.
- [x] Read `docs/workflow-vnext.md`.
- [x] Read `aria/specs/_template/**`.
- [x] Read `aria/review/validation-checklist.md`.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`:

| Area | Risk | This spec task | Future implementation |
|------|------|----------------|----------------------|
| Safety summary verification | High | Documented in requirements | Must confirm all safety boundaries hold; negative checks for unsafe output |
| Release checklist validation | Medium | Defined in design | Deterministic pass/fail per item; runnable CLI commands |
| Version consistency | Medium | Defined in requirements | Automated grep/diff between `__init__.py` and `pyproject.toml` |
| Repository hygiene | Medium | Defined in requirements | Canonical contamination command; check for forbidden files |
| Public API surface summary | Medium | Referenced from requirements | Inventory from existing hardening audit; document stable exports |
| Test/validation matrix | Medium | Documented in requirements | Reference current test count; confirm tests pass; CLI smoke |
| Package metadata review | Low | Documented in requirements | Manual review with checklist |
| README review | Low | Documented in requirements | Manual review with checklist |
| Documentation consistency review | Low | Documented in requirements | Manual review; flag future/backlog status |
| Changelog/release notes | Low | Documented in requirements | Documentation artifact; draft structure from spec |
| Handoff/backlog summary | Low | Documented in requirements | Documentation artifact; update existing handoff |

## Behavior Budget check

This spec task:

- New behaviors: documentation/spec only. [x]
- Public API changes: proposed only, no source code in this task. [x]
- Files allowed: `aria/specs/features/aria-release-preparation/**`, plus `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if needed. [x]
- Tests required: none in this task, validation only. [x]
- Dependencies: none. [x]
- Stop if: release implementation, tagging, publishing, source changes, test changes, version changes, or product behavior implementation becomes necessary. Not triggered. [x]

## Implementation tasks

This task creates the Bloco 7 release preparation spec only.

### Task 1: Create spec directory

- [ ] Create `aria/specs/features/aria-release-preparation/`.

### Task 2: Write `requirements.md`

- [ ] Define problem and goal for Aria Core release preparation.
- [ ] Define non-goals: no tag, no publish, no source changes, no product behavior.
- [ ] Define actors: maintainer, implementation agent, reviewer, downstream consumers.
- [ ] Define functional requirements FR-10 through FR-140 covering:
  - release readiness checklist;
  - version consistency;
  - package metadata review;
  - README review;
  - documentation consistency review;
  - public API surface summary;
  - safety summary;
  - test/validation matrix;
  - repository hygiene check;
  - changelog/release notes draft;
  - handoff document for next phase;
  - post-core backlog summary;
  - tag/release steps for later implementation;
  - final stop conditions.
- [ ] Define non-functional requirements.
- [ ] Include Canonical Examples using Given / When / Then (CE-01 through CE-08).
- [ ] Include edge cases (EC-01 through EC-10).
- [ ] Include acceptance criteria.
- [ ] Include open questions.

### Task 3: Write `design.md`

- [ ] Document summary and context package used: Standard.
- [ ] Document context files read.
- [ ] Document files to create, files to modify, and files that must not be touched.
- [ ] Define release readiness flow with decision gates.
- [ ] Define versioning approach and resolution order.
- [ ] Define documentation update approach.
- [ ] Define safety considerations for release preparation.
- [ ] Define repository hygiene considerations and canonical contamination command.
- [ ] Define dependencies (none added).
- [ ] Include Behavior Budget.
- [ ] Include risks and risk classification.
- [ ] Include Test Risk Matrix reference.
- [ ] Include rollback strategy.
- [ ] Include validation plan for this spec task.

### Task 4: Write `tasks.md`

- [ ] Document preparation checklist.
- [ ] Document Test Risk Matrix.
- [ ] Document Behavior Budget check.
- [ ] Document implementation tasks for spec creation (Tasks 1-5).
- [ ] Document future implementation tasks for the release preparation block.
- [ ] Document validation checklist.
- [ ] Document review checklist.
- [ ] Document delta update checklist.

### Task 5: Write `review.md`

- [ ] Initialize as a review stub for later implementation.
- [ ] Document expected requirements coverage (placeholder).
- [ ] Document context package used (placeholder for implementation phase).
- [ ] Document files created/modified (placeholder for implementation phase).
- [ ] Document validation performed (placeholder for implementation phase).
- [ ] Document non-goals check (placeholder for implementation phase).
- [ ] Document Behavior Budget result (placeholder for implementation phase).
- [ ] Document risk/test coverage result (placeholder for implementation phase).
- [ ] Document open questions and follow-up tasks.

## Future implementation tasks

For the Bloco 7 release preparation implementation (do not execute now):

### Future Task A: Create release readiness checklist

- [ ] Create `docs/release-checklist.md`.
- [ ] Define checklist items covering: version consistency, package metadata, README, docs, API surface, safety, tests, hygiene, changelog, handoff, backlog, stop conditions.
- [ ] Include canonical CLI invocation commands for automated checks.
- [ ] Define clear pass/fail criteria for each item.
- [ ] Define the final gate: all items must pass before tag/publish.

### Future Task B: Verify version consistency

- [ ] Compare `__version__` in `src/noqlen_aria/__init__.py` with `version` in `pyproject.toml`.
- [ ] Decide version bump if applicable (document decision).
- [ ] If bump, update both locations.
- [ ] Search for hardcoded version strings elsewhere.

### Future Task C: Review package metadata

- [ ] Review `pyproject.toml` fields for correctness.
- [ ] Confirm no references to unimplemented features.
- [ ] Confirm build system and packaging configuration is valid.

### Future Task D: Review README

- [ ] Review `README.md` for accuracy against MVP behavior.
- [ ] Flag or fix any references to future/backlog features as implemented.
- [ ] Confirm install/usage instructions are correct.

### Future Task E: Review documentation consistency

- [ ] Review all public docs for MVP/future scope consistency.
- [ ] Ensure future UI/player/provider/cache features marked as future/backlog.
- [ ] Ensure Anchor is described as one `ControlClient` adapter.
- [ ] Make tiny clarifying fixes only; flag larger issues for follow-up specs.

### Future Task F: Produce public API surface summary

- [ ] Reference the existing Bloco 6 hardening export audit.
- [ ] Document the stable public API surface.
- [ ] Document any internal names present in public modules.

### Future Task G: Produce safety summary

- [ ] Confirm real music-library access is absent.
- [ ] Confirm direct Navidrome calls are absent.
- [ ] Confirm Anchor provider internals are absent.
- [ ] Confirm Android/UI/playback/queue/cache implementation is absent.
- [ ] Confirm provider hard coupling is absent.
- [ ] Confirm secrets/credentials are absent from release artifacts.
- [ ] Confirm optional Anchor dependency is safe.
- [ ] Confirm lifecycle apply is blocked/unavailable.
- [ ] Confirm serialized output is sanitized.

### Future Task H: Produce test/validation matrix

- [ ] Run `python3 -m pytest` and record pass count.
- [ ] Run CLI smoke commands (`--help`, `doctor`) and record results.
- [ ] Run `python3 -m py_compile src/noqlen_aria/*.py` and confirm success.
- [ ] Run repository contamination check and confirm clean.

### Future Task I: Run repository hygiene check

- [ ] Run canonical contamination command.
- [ ] Confirm no forbidden files are tracked.
- [ ] Confirm `git add .` was not used.

### Future Task J: Draft changelog/release notes

- [ ] Create `CHANGELOG.md` or release notes section.
- [ ] Summarize completed Blocos 0-6 scope.
- [ ] Separate implemented features from future/backlog.
- [ ] Include safety boundaries and known limitations.
- [ ] Include version information.

### Future Task K: Update handoff document

- [ ] Update `docs/handoff.md` with post-release status.
- [ ] Reference the post-core backlog summary.
- [ ] Reference next steps (Bloco 7+ library/search, or next approved block).

### Future Task L: Produce post-core backlog summary

- [ ] Create `docs/post-core-backlog.md` or backlog summary section.
- [ ] List planned future blocks from the roadmap (Blocos 7-21).
- [ ] Distinguish spec'd blocks from unspec'd features.
- [ ] Note that future features require dedicated specs.

### Future Task M: Define tag/release steps

- [ ] Document git tag format and version convention.
- [ ] Document release creation steps.
- [ ] Document package build and publish steps for reference.
- [ ] Document final stop conditions before execution.

### Future Task N: Final validation and commit

- [ ] Re-run full release readiness checklist.
- [ ] Confirm all items pass.
- [ ] Commit release preparation artifacts with explicit allowlisted paths.
- [ ] Update `aria/context/current.md` and `aria/context/delta.md`.

## Validation checklist

- [ ] `pwd`
- [ ] `git status --short --branch`
- [ ] `find aria/specs/features/aria-release-preparation aria/context -maxdepth 5 -type f | sort`
- [ ] `git diff --check`
- [ ] `python3 -m py_compile src/noqlen_aria/*.py`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [ ] `python3 -m pytest`
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`

## Review checklist

- [ ] Confirm this is spec-only.
- [ ] Confirm no source code changed.
- [ ] Confirm no tests changed.
- [ ] Confirm no version was changed.
- [ ] Confirm no release/tag was created.
- [ ] Confirm no package publish was attempted.
- [ ] Confirm no Android/UI/playback/queue/cache/provider code was added.
- [ ] Confirm Behavior Budget is present in the spec.
- [ ] Confirm Test Risk Matrix is present in the spec.
- [ ] Confirm Canonical Examples are present in the spec.
- [ ] Confirm context package used is documented as Standard.
- [ ] Confirm `current.md` and `delta.md` stayed concise.
- [ ] Confirm no private/local/tooling files are tracked.
- [ ] Confirm validation passed or failures are recorded.

## Delta update

- [ ] Update `aria/context/current.md` to mark Bloco 7 spec complete.
- [ ] Update `aria/context/delta.md` to record Bloco 7 spec creation and validation evidence.
- [ ] Keep both files concise.
- [ ] Update `docs/handoff.md` with Bloco 7 spec status note only if needed.
