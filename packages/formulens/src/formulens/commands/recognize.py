"""Recognize equations from existing images."""

from pathlib import Path
from typing import Annotated

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.desktop.output import copy_latex, notify_ready
from formulens.recognition.engine import EquationRecognizer
from formulens.recognition.service import request_recognition


def recognize(
    image: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True)],
    use_daemon: Annotated[bool, typer.Option("--daemon", help="Use the already-loaded background model.")] = False,
    copy: Annotated[bool | None, typer.Option("--copy/--no-copy", help="Override the clipboard preference.")] = None,
) -> None:
    """Print an image's LaTeX and optionally copy it. The source image is preserved."""
    settings = run_action(load_configuration)

    def action() -> str:
        return request_recognition(image) if use_daemon else EquationRecognizer(settings).recognize(image)

    text = run_action(action)
    typer.echo(text)
    should_copy = settings.copy_to_clipboard if copy is None else copy
    if should_copy:
        run_action(lambda: copy_latex(text))
        if settings.notifications:
            notify_ready()
