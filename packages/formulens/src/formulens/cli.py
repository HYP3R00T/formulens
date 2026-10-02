"""Assemble the Formulens CLI from its command groups."""

import typer

from formulens.commands.config import app as config_app

app = typer.Typer(help="Local equation-to-LaTeX tools.", no_args_is_help=True)
app.add_typer(config_app, name="config")
