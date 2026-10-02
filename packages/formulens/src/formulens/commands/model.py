"""Download and verify the configured recognition model."""

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.recognition.engine import EquationRecognizer


def model_download() -> None:
    """Download the configured model into model_directory and verify it loads."""
    settings = run_action(load_configuration)
    run_action(EquationRecognizer(settings).load)
    typer.echo(f"Model ready: {settings.get_model_directory()}")
