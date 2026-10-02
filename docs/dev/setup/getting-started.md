# Getting Started

Set up the Formulens development workspace. Python 3.14 is required.

## Clone the Repository

```bash
git clone https://github.com/HYP3R00T/formulens.git
cd formulens
```

## Local Setup

Install [mise](https://mise.jdx.dev/), then run:

```bash
mise trust
mise install
uv sync --all-packages
uv run formulens
```

The CLI currently prints `Hello from formulens!`.

## Dev Container Setup

Requires Docker, VS Code, and its Dev Containers extension.

1. Open the repository in VS Code.
2. Run **Dev Containers: Reopen in Container** from the command palette.
3. Wait for `scripts/setup.sh` to install the mise tools.
4. Run `uv sync --all-packages` in the container terminal.

The container provides a development environment. Desktop capture has not been
implemented or verified inside it.

## Install Git Hooks

The mise enter hook installs Git hooks when prek is available. To install them
manually:

```bash
prek install --hook-type pre-commit --overwrite
prek install --hook-type commit-msg --overwrite
prek run --all-files
```

## Next Steps

- [Developer Setup](index.md): daily development commands.
- [Resources](../resources.md): tooling references.
