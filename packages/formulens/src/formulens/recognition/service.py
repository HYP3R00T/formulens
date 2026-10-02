"""A local Unix socket service keeps the OCR model loaded between captures."""

import contextlib
import json
import os
import socket
import socketserver
import sys
import tempfile
from pathlib import Path

from formulens.configuration.schema import Settings
from formulens.recognition.engine import EquationRecognizer


def get_socket_path() -> Path:
    """Use a per-user runtime directory, independent of persistent model storage."""
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    root = Path(runtime) if runtime else Path(tempfile.gettempdir()) / f"formulens-{os.getuid()}"
    return root / "formulens" / "ocr.sock"


def request_recognition(path: Path) -> str:
    """Submit a file to the running daemon and wait for its response."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(600)
        try:
            connection.connect(str(get_socket_path()))
        except (FileNotFoundError, ConnectionRefusedError) as error:
            raise RuntimeError("Start the model service first: formulens daemon") from error
        connection.sendall(json.dumps({"path": str(path.resolve())}).encode() + b"\n")
        with connection.makefile("rb") as stream:
            response = json.loads(stream.readline(1024 * 1024))
    if "error" in response:
        raise RuntimeError(response["error"])
    return response["latex"]


def serve(settings: Settings) -> None:
    """Serve one request at a time, reusing a single model instance."""
    import fcntl

    socket_path = get_socket_path()
    socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(socket_path.parent, 0o700)
    with (socket_path.parent / "daemon.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("A Formulens daemon is already running.") from error
        _serve_locked(settings, socket_path)


def _serve_locked(settings: Settings, socket_path: Path) -> None:
    """Keep the instance lock held during model loading and request processing."""
    engine = EquationRecognizer(settings)
    engine.load()
    socket_path.unlink(missing_ok=True)

    class RequestHandler(socketserver.StreamRequestHandler):
        def handle(self) -> None:
            self.connection.settimeout(10)
            try:
                raw = self.rfile.readline(65536)
            except TimeoutError:
                return
            if not raw:
                return
            try:
                request = json.loads(raw)
                response = {"latex": engine.recognize(Path(request["path"]))}
            except Exception as error:
                response = {"error": str(error)}
            with contextlib.suppress(BrokenPipeError, ConnectionResetError):
                self.wfile.write(json.dumps(response).encode() + b"\n")

    try:
        with socketserver.UnixStreamServer(str(socket_path), RequestHandler) as server:
            os.chmod(socket_path, 0o600)
            print(
                f"Formulens daemon ready: {socket_path} (model stays loaded on {engine.device})",
                file=sys.stderr,
                flush=True,
            )
            server.serve_forever()
    finally:
        socket_path.unlink(missing_ok=True)
