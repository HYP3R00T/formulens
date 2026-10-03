"""Start the model service independently of the invoking terminal."""

import fcntl
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from utilityhub_logging import cleanup_logging

from formulens.configuration.storage import load_configuration
from formulens.recognition.logging import configure_logging, get_log_path
from formulens.recognition.service import _serve_locked, get_socket_path


def start_background() -> int:
    """Detach a worker and return its PID once the model service is ready."""
    socket_path = get_socket_path()
    socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (socket_path.parent / "daemon.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("A Formulens daemon is already running.") from error

        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                f"from formulens.recognition.background import run_background; run_background({lock.fileno()})",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            pass_fds=(lock.fileno(),),
            cwd=Path.home(),
        )
    try:
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Background daemon failed to start. See logs: {get_log_path()}")
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(1)
                try:
                    connection.connect(str(socket_path))
                except FileNotFoundError, ConnectionRefusedError, TimeoutError:
                    pass
                else:
                    return process.pid
            time.sleep(0.1)
        raise RuntimeError(f"Daemon startup timed out. See logs: {get_log_path()}")
    except BaseException:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        raise


def run_background(lock_fd: int) -> None:
    """Child entry point; retain the inherited lock for the worker's lifetime."""
    with os.fdopen(lock_fd, "a"):
        try:
            _serve_locked(load_configuration(), get_socket_path(), console_output=False)
        except Exception:
            logger = configure_logging(console_output=False)
            logger.exception("Background daemon failed")
            cleanup_logging(logger)
            raise SystemExit(1) from None
