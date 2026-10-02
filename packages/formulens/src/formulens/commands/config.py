"""Commands for managing Formulens configuration."""

from typing import Annotated

import typer

from formulens.commands.errors import run_config_action
from formulens.configuration.storage import (
    get_settings_path,
    initialize_settings,
    load_configuration,
    set_setting,
)

app = typer.Typer(help="Manage configuration in ~/.config/formulens.", no_args_is_help=True)


@app.command("init")
def config_init() -> None:
    """Create default configuration, preserving any existing settings."""
    typer.echo(run_config_action(initialize_settings))


@app.command("path")
def config_path() -> None:
    """Print the configuration path without creating a file."""
    typer.echo(get_settings_path())


@app.command("show")
def config_show() -> None:
    """Print effective settings as JSON, including environment overrides."""
    settings = run_config_action(load_configuration)
    typer.echo(settings.model_dump_json(indent=2))


@app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Setting name, such as notifications.")],
    value: Annotated[str, typer.Argument(help="New value: true or false.")],
) -> None:
    """Validate and save a setting in the global TOML file."""
    typer.echo(run_config_action(lambda: set_setting(key, value)))
