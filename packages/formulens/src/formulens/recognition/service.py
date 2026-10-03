"""A local Unix socket service keeps the OCR model loaded between captures."""

import contextlib
import json
import os
import socket
import socketserver
import tempfile
import time
from pathlib import Path

from utilityhub_logging import bind_context, cleanup_logging

from formulens.configuration.schema import Settings
from formulens.recognition.engine import EquationRecognizer
from formulens.recognition.logging import configure_logging, get_log_path, model_loading_output


def get_socket_path() -> Path:
    """Use a per-user runtime directory, independent of persistent model storage."""
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    root = Path(runtime) if runtime else Path(tempfile.gettempdir()) / f"formulens-{os.getuid()}"
    return root / "formulens" / "ocr.sock"


def request_recognition(path: Path) -> str:
    """Submit a file to the running daemon and wait for its response."""
    response = _request({"path": str(path.resolve())})
    return response["latex"]


def stop_daemon() -> None:
    """Ask the daemon to exit gracefully after any active recognition finishes."""
    _request({"action": "stop"})


def _request(request: dict[str, str]) -> dict[str, str]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(600)
        try:
            connection.connect(str(get_socket_path()))
        except (FileNotFoundError, ConnectionRefusedError) as error:
            raise RuntimeError("No Formulens daemon is running. Start it with: formulens daemon") from error
        connection.sendall(json.dumps(request).encode() + b"\n")
        with connection.makefile("rb") as stream:
            response = json.loads(stream.readline(1024 * 1024))
    if "error" in response:
        raise RuntimeError(response["error"])
    return response


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


def _serve_locked(settings: Settings, socket_path: Path, *, console_output: bool = True) -> None:
    """Keep the instance lock held during model loading and request processing."""
    logger = configure_logging(console_output=console_output)
    logger.info("Starting Formulens · %s · NVIDIA CUDA", settings.model)
    logger.info("Log file: %s", get_log_path())
    engine = EquationRecognizer(settings)
    try:
        with model_loading_output(logger):
            engine.load()
    except Exception:
        logger.exception("Model loading failed")
        cleanup_logging(logger)
        raise
    socket_path.unlink(missing_ok=True)
    stopping = False
    processed = 0

    class RequestHandler(socketserver.StreamRequestHandler):
        def handle(self) -> None:
            nonlocal stopping, processed
            self.connection.settimeout(10)
            try:
                raw = self.rfile.readline(65536)
            except TimeoutError:
                return
            if not raw:
                return
            try:
                request = json.loads(raw)
                if request.get("action") == "stop":
                    stopping = True
                    logger.info("Shutdown requested")
                    response = {"status": "stopping"}
                else:
                    processed += 1
                    started = time.monotonic()
                    with bind_context(request_id=processed):
                        logger.info("Equation #%s · Processing", processed)
                        logger.debug("Input: %s", request["path"])
                        text = engine.recognize(Path(request["path"]))
                        logger.info("Equation #%s · Ready in %.2fs", processed, time.monotonic() - started)
                        logger.info("LaTeX: %s", text)
                        response = {"latex": text}
            except Exception as error:
                logger.exception("Request failed")
                response = {"error": str(error)}
            with contextlib.suppress(BrokenPipeError, ConnectionResetError):
                self.wfile.write(json.dumps(response).encode() + b"\n")

    try:
        with socketserver.UnixStreamServer(str(socket_path), RequestHandler) as server:
            os.chmod(socket_path, 0o600)
            logger.info("Ready · Model stays loaded on %s · Waiting for equations", engine.device)
            logger.info("Stop with formulens daemon off%s", " or Ctrl+C" if console_output else "")
            logger.debug("Socket: %s", socket_path)
            while not stopping:
                server.handle_request()
    finally:
        socket_path.unlink(missing_ok=True)
        logger.info("Daemon stopped")
        cleanup_logging(logger)
