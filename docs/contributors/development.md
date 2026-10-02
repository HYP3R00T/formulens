# Development

## Workspace

Formulens is a uv workspace. The root project is a development workspace; the
publishable Python package is `packages/formulens`.

Within `packages/formulens/src/formulens/`:

- `commands/` contains Typer commands.
- `configuration/` validates and persists settings.
- `recognition/` implements inference, the daemon, and logging.
- `desktop/` handles capture, clipboard output, and notifications.
- `cli.py` assembles the command groups.

Development tools are managed through `mise.toml`. See
[installation](../user-guide/installation.md) for the source setup.

## Checks

```bash
uv run --package formulens --extra ocr python -m unittest discover -s tests
prek run --all-files
```

The socket integration tests require access to local Unix sockets. Most tests
use mocked models and do not download weights or run GPU inference. Verify
changes to inference separately with representative equation images on CUDA.

## Local documentation

```bash
mise run docs
```

Build the site without serving it:

```bash
uvx zensical build --clean
```

End-user documentation belongs under `docs/user-guide/`; contributor and
maintainer guides belong under `docs/contributors/`. Navigation is configured
in `zensical.toml`. Keep both READMEs short and link to these guides for details.

## Release preparation

Follow the [publishing guide](publishing.md) to update the package changelog,
verify the build, and publish manually.
