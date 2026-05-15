# Noqlen Aria Core

Noqlen Aria Core is the app/interface orchestration core for the Noqlen ecosystem. It is the product boundary that future user interfaces will call.

Aria Workflow is the development method used in this repository. Aria Workflow is not the product.

Aria Core is not UI and is not an Android app. Future UI must remain a thin adapter over Aria Core.

Future ecosystem flow:

`Future UI/App -> Aria Core -> Anchor Client -> Anchor Core API -> Navidrome`

Bloco 0 is bootstrap, repository context, and workflow only. Future product context is documented here and under `aria/context/`, but product features are not implemented yet.

## Development

Python 3.11+ is required.

Install locally for development:

```bash
python3 -m pip install -e .
```

CLI smoke examples:

```bash
noqlen-aria --help
noqlen-aria doctor
```

Without installation:

```bash
PYTHONPATH=src python3 -m noqlen_aria.cli --help
PYTHONPATH=src python3 -m noqlen_aria.cli doctor
```

## Bloco 0 Boundaries

Bloco 0 does not add Anchor as a dependency, does not add Android/Kotlin/Gradle dependencies, does not implement UI, and does not integrate with Navidrome or real music libraries.
