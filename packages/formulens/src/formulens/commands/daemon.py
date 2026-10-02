"""Keep a recognition model ready for desktop requests."""

from contextlib import suppress

import typer

from formulens.commands.errors import run_action
from formulens.configuration.storage import load_configuration
from formulens.recognition.service import serve, stop_daemon

app = typer.Typer(help="Run or stop the resident model service.", invoke_without_command=True)


@app.callback()
def daemon(context: typer.Context) -> None:
    """Load the configured model and serve requests until Ctrl+C."""
    if context.invoked_subcommand is not None:
        return
    settings = run_action(load_configuration)
    with suppress(KeyboardInterrupt):
        run_action(lambda: serve(settings))


@app.command("off")
def off() -> None:
    """Stop the daemon, waiting for any active recognition to finish."""
    run_action(stop_daemon)
    typer.echo("Daemon shutdown requested.")
