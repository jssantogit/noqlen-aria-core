# Aria Workflow Contract

This repository follows Aria Workflow. For Aria Bloco 0, the primary source of truth is `handoff_noqlen_aria_core_complete_v2.md` as provided in the bootstrap handoff.

Before non-trivial work, read the relevant files under `aria/context/` and `aria/review/`. Create and review a spec before non-trivial implementation, then implement one task at a time.

After changes, run appropriate validation and record the evidence. Keep commits small and focused.

Forbidden:
- Unrelated refactors.
- Invented business rules.
- Local workflow/tool artifacts in commits.
- `git add .`.
- Direct Navidrome calls, Anchor internals, Anchor CLI integration, Android UI/SDK, playback, cache/offline behavior in Bloco 0.
