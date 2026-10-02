"""Assemble the Formulens CLI from its command groups."""

import typer

from formulens.commands.capture import capture
from formulens.commands.config import app as config_app
from formulens.commands.daemon import daemon
from formulens.commands.model import model_download
from formulens.commands.recognize import recognize

app = typer.Typer(help="Local equation-to-LaTeX tools.", no_args_is_help=True)
app.add_typer(config_app, name="config")
app.command("recognize")(recognize)
app.command("capture")(capture)
app.command("daemon")(daemon)
app.command("model-download")(model_download)
