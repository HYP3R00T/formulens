"""Translate configuration failures into CLI errors."""

from collections.abc import Callable

import typer
from pydantic import ValidationError
from utilityhub_config.errors import ConfigError


def run_config_action[T](action: Callable[[], T]) -> T:
    """Report configuration failures without a Python traceback."""
    try:
        return action()
    except (ConfigError, ValidationError, OSError, ValueError, RuntimeError) as error:
        typer.echo(f"Configuration error: {error}", err=True)
        raise typer.Exit(code=1) from error
