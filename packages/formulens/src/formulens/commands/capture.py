"""Capture an equation and send it to the loaded model."""

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.desktop.capture import CaptureCancelledError, capture_equation
from formulens.desktop.output import copy_latex, notify_ready
from formulens.recognition.service import get_socket_path, request_recognition


def capture() -> None:
    """Select an equation with COSMIC, recognize it, and clean up the capture."""
    settings = run_action(load_configuration)
    if not get_socket_path().exists():
        typer.echo("Start the model service first: formulens daemon", err=True)
        raise typer.Exit(1)

    def process_capture() -> str:
        with capture_equation() as image:
            return request_recognition(image)

    try:
        text = run_action(process_capture)
    except CaptureCancelledError:
        return
    typer.echo(text)
    if settings.copy_to_clipboard:
        run_action(lambda: copy_latex(text))
        if settings.notifications:
            notify_ready()
