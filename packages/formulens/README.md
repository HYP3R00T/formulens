# Formulens

Formulens is a Linux-first CLI for a local equation-to-LaTeX workflow.

Version **0.0.1** provides configuration management through Typer and UtilityHub
Config. Equation recognition, screen capture, daemon mode, and clipboard
integration are not implemented in this release.

## Installation

Requires Python **3.14 or newer**. After this release is published, install it with
[uv](https://docs.astral.sh/uv/):

```bash
uv tool install formulens
```

## Configuration

```bash
formulens --help
formulens config init
formulens config path
formulens config show
formulens config set notifications false
```

Settings are stored at `~/.config/formulens/formulens.toml`:

```toml
copy_to_clipboard = true
notifications = true
```

`init` preserves existing configuration. `path` prints its location. `show`
displays effective settings as JSON without creating files. `set` validates and
saves an edit. These preferences are stored for future desktop integration;
they do not yet trigger clipboard output or notifications.

Environment variables such as `FORMULENS_NOTIFICATIONS=false` override saved
values. Formulens loads global TOML/YAML configuration and any `.env` inside its
configuration directory, without searching the current working directory.
`set` updates only the TOML file and does not save environment overrides.

## Development

From a checkout of the repository:

```bash
uv sync --all-packages
uv run formulens --help
uv run python -m unittest discover -s tests
```

See the [project repository](https://github.com/HYP3R00T/formulens) for development
setup and documentation.

## License

MIT. Copyright 2026 Rajesh Das. The license is included in the distribution.
