# Formulens

Local equation-to-LaTeX recognition with a Linux-first CLI.

Formulens is being built for taking equations from PDFs, websites, and existing
images into mathematical notes. The project is currently a Python workspace
scaffold: capture, OCR, daemon mode, and clipboard integration are not implemented
yet.

## Development

Requires Python 3.14 and [mise](https://mise.jdx.dev/).

```bash
git clone https://github.com/HYP3R00T/formulens.git
cd formulens
mise trust
mise install
uv sync --all-packages
uv run formulens
```

The generated CLI currently prints `Hello from formulens!`.

For container development, open the repository in VS Code and select
**Dev Containers: Reopen in Container**, then run `uv sync --all-packages`.

## Workspace

- `pyproject.toml`: the non-publishable `formulens-workspace` root.
- `packages/formulens/`: the Python package and `formulens` CLI entry point.
- `uv.lock`: shared dependency lockfile.
- `mise.toml`: development tools and tasks.
- `docs/`: setup and contribution documentation.

## Checks

```bash
prek run --all-files
```

See [Getting Started](docs/dev/setup/getting-started.md) for setup and
[Developer Setup](docs/dev/setup/index.md) for daily commands.

## License

[MIT](LICENSE).
