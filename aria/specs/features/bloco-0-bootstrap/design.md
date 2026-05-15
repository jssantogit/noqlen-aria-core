# Design

## Summary

Bootstrap a Python 3.11+ package with a thin local CLI, public docs, Aria context, templates, and review checklists.

## Context files read

- Bootstrap handoff content provided as `handoff_noqlen_aria_core_complete_v2.md` in the task message.
- Anchor reference repository page at `https://github.com/jssantogit/noqlen-anchor-core`.

## Existing project context

The local directory existed, was empty, and was not a git repository.

## Files to create

The Bloco 0 file set listed in the bootstrap handoff, plus this active bootstrap spec.

## Files to modify

`.git/info/exclude` for local-only exclusions. This file must not be committed.

## Files that must not be touched

- Local workflow/tool artifacts.
- Secrets and credentials.
- Real music libraries.
- Anchor internals.
- Android project files.

## Data flow

The CLI only prints local package and runtime status. It does not call network services or inspect media libraries.

## Error handling

Use standard argparse help behavior and deterministic doctor output.

## Security considerations

Do not read secrets, credentials, private logs, real libraries, Anchor, or Navidrome.

## Dependencies

No runtime dependencies.

## Risks

- The named handoff file is not present on disk; the provided task content is used as source-of-truth content.

## Rollback strategy

Before commit, remove bootstrap files if the repository is deemed unsafe. After commit, revert with a normal non-destructive commit if required.

## Validation plan

Run the Bloco 0 validation commands from `aria/review/validation-checklist.md` and the handoff.
