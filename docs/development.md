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
[installation](installation.md) for the source setup.

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

Documentation content belongs under `docs/`; navigation is configured in
`zensical.toml`. Keep both READMEs short and link to these guides for details.

## Release preparation

The upcoming package version is 0.1.0. Update release notes, verify the built
package and CUDA installation, and complete review before publishing. See
[release notes](releases.md). Version 0.1.0 has not been published yet.
