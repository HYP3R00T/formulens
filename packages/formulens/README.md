# Formulens

Local equation-to-LaTeX recognition with a Linux-first CLI.

This package provides a Typer CLI and typed configuration through UtilityHub
Config. Capture, OCR, daemon mode, and clipboard integration are not implemented
yet.

From the repository root:

```bash
uv sync --all-packages
uv run --package formulens formulens --help
uv run --package formulens formulens config init
uv run --package formulens formulens config show
```

Configuration lives at `~/.config/formulens/formulens.toml`. Use `config path`
to print the path and `config set notifications false` to update a preference.
`config init` preserves existing files. Clipboard and notification preferences
are stored now for use by the upcoming recognition workflow.

See the [project repository](https://github.com/HYP3R00T/formulens) for development
setup and documentation.
