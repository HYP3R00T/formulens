"""Keep a recognition model ready for desktop requests."""

from contextlib import suppress

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.recognition.service import serve


def daemon() -> None:
    """Load the configured model and serve requests until Ctrl+C."""
    settings = run_action(load_configuration)
    typer.echo(f"Loading {settings.model} on {settings.device}; models: {settings.get_model_directory()}", err=True)
    with suppress(KeyboardInterrupt):
        run_action(lambda: serve(settings))
