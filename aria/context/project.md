# Project Context

Noqlen Aria Core is the modular app/player-facing core of a music player.

Repository-local handoff: `docs/aria-core-handoff.md`.

Aria Core is the product. Aria Workflow is the development method and is not the product.

Strategic position:

`Flux -> Forge -> Anchor -> Aria`

Current architecture direction:

`Future UI/App/Player -> Aria Core -> contracts/adapters -> providers/backends`

Anchor is not the center of Aria. Anchor is one `ControlClient` adapter/control-plane backend, and Aria must depend on contracts rather than Anchor internals.

Roadmap direction: Aria Core MVP is Blocos 0-7; post-core feature expansion is Blocos 8-20. Android app/UI remains separate and consumes Aria Core.

## Non-Goals

Canonical scope boundaries live in `aria/context/scope-boundaries.md`.

## Future Product Context

Future planning context lives in `aria/context/future-product-context.md`.

## Android Music Player Reference Analysis

Android player references live in `aria/context/android-player-reference.md`.
