# Requirements

## Status

Approved for Bloco 0 bootstrap.

## Problem

Noqlen Aria Core needs a safe initial repository, workflow contract, project context, and local validation surface.

## Goal

Create the repository bootstrap and Aria Workflow context without implementing product features.

## Non-goals

- No Aria Core product contracts.
- No Android UI/SDK.
- No playback, queue, now playing, cache, or offline behavior.
- No Anchor dependency or real integration.
- No direct Navidrome calls.

## Actors

- Maintainer.
- Future implementation agents.
- Future thin UI adapters.

## Functional requirements

- Provide repository metadata and package skeleton.
- Provide a safe local `doctor` CLI command.
- Provide workflow, context, spec, prompt, agent, and review files.
- Document future product context as planning only.

## Non-functional requirements

- Local-only validation.
- Minimal dependencies.
- English public docs.
- Strict repository hygiene.

## Edge cases

- Handoff file may be provided in task context rather than present on disk.
- Remote repository may already exist or GitHub CLI may be unavailable.

## Acceptance criteria

- Required files exist.
- CLI help and doctor run locally.
- Tests pass when pytest is available.
- Repository is committed on `main`.
- Push is performed only if safe.

## Open questions

- None for Bloco 0.
