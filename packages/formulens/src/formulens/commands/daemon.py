"""Keep a recognition model ready for desktop requests."""

from contextlib import suppress

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.recognition.background import start_background
from formulens.recognition.logging import get_log_path
from formulens.recognition.service import serve, stop_daemon

app = typer.Typer(
    help="Run the model service in the foreground or background, or stop it.", invoke_without_command=True
)


@app.callback()
def daemon(context: typer.Context) -> None:
    """Load the configured model and serve requests until Ctrl+C."""
    if context.invoked_subcommand is not None:
        return
    settings = run_action(load_configuration)
    with suppress(KeyboardInterrupt):
        run_action(lambda: serve(settings))


@app.command("on")
def on() -> None:
    """Start in the background and return when the model is ready."""
    typer.echo("Starting background daemon; waiting for the model to be ready…")
    with suppress(KeyboardInterrupt):
        pid = run_action(start_background)
        typer.echo(f"Background daemon ready (PID {pid}). Logs: {get_log_path()}")
        typer.echo("Stop with: formulens daemon off")


@app.command("off")
def off() -> None:
    """Stop the daemon, waiting for any active recognition to finish."""
    run_action(stop_daemon)
    typer.echo("Daemon shutdown requested.")
