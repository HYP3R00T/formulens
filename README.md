# Formulens

Local equation-to-LaTeX recognition with a Linux-first CLI.

Formulens is being built for taking equations from PDFs, websites, and existing
images into mathematical notes. Version **0.0.1** currently provides configuration
management. Capture, OCR, daemon mode, and clipboard integration are not
implemented yet.

## Development

Requires Python 3.14 and [mise](https://mise.jdx.dev/).

```bash
git clone https://github.com/HYP3R00T/formulens.git
cd formulens
mise trust
mise install
uv sync --all-packages
uv run formulens --help
```

Configuration is stored at `~/.config/formulens/formulens.toml` using
[UtilityHub Config](https://utilityhub.hyperoot.dev/packages/utilityhub_config/).

```bash
uv run formulens config init
uv run formulens config path
uv run formulens config show
uv run formulens config set notifications false
```

`init` preserves existing settings. `show` displays effective settings without
creating files. `set` validates edits before saving. The initial preferences are
`copy_to_clipboard` and `notifications`, both enabled by default; they will be
consumed when recognition and desktop integration are implemented.

UtilityHub loads global TOML/YAML files and environment overrides such as
`FORMULENS_NOTIFICATIONS=false`. Formulens confines discovery to its config
directory, including any `.env` there; it does not load configuration from the
current working directory. `set` edits only the TOML file and does not persist
environment overrides.

For container development, open the repository in VS Code and select
**Dev Containers: Reopen in Container**, then run `uv sync --all-packages`.

## Workspace

- `pyproject.toml`: the non-publishable `formulens-workspace` root.
- `packages/formulens/`: the Python package and `formulens` CLI entry point.
- `packages/formulens/src/formulens/commands/`: command groups, with related commands together in one module.
- `packages/formulens/src/formulens/configuration/`: settings schema and persistence.
- `uv.lock`: shared dependency lockfile.
- `mise.toml`: development tools and tasks.
- `docs/`: setup and contribution documentation.

## Checks

```bash
uv run python -m unittest discover -s tests
prek run --all-files
```

## License

[MIT](LICENSE).
