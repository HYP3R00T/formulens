"""Verify daemon request reuse, logging, failures, and graceful shutdown."""

import logging
import os
import tempfile
import threading
import time
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

from formulens.cli import app
from formulens.configuration.schema import Settings
from formulens.recognition.logging import CompatibilityNoticeFilter
from formulens.recognition.service import _serve_locked, request_recognition, stop_daemon
from typer.testing import CliRunner


class DaemonTests(unittest.TestCase):
    def test_only_known_library_notices_are_hidden_from_terminal(self) -> None:
        notice_filter = CompatibilityNoticeFilter()
        messages = (
            "`PaddleOCRVLProcessor` defines `image_processor_class = 'AutoImageProcessor'`, which is deprecated.",
            "Unrecognized keys in `rope_parameters` for 'rope_type'='default': {'mrope_section'}",
        )
        for message in messages:
            warning = logging.LogRecord("transformers.processing_utils", logging.WARNING, "", 0, message, (), None)
            self.assertFalse(notice_filter.filter(warning))
            warning.levelno = logging.ERROR
            self.assertTrue(notice_filter.filter(warning))
        unknown = logging.LogRecord("transformers.modeling_utils", logging.WARNING, "", 0, "Unknown issue", (), None)
        self.assertTrue(notice_filter.filter(unknown))

    def test_requests_are_logged_and_stop_removes_socket(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            socket_path = root / "ocr.sock"
            with (
                patch.dict(os.environ, {"XDG_STATE_HOME": directory}),
                patch("formulens.recognition.service.get_socket_path", return_value=socket_path),
                patch("formulens.recognition.service.EquationRecognizer") as recognizer,
                patch("formulens.recognition.service.model_loading_output", return_value=nullcontext()),
            ):
                engine = recognizer.return_value
                engine.device = "cuda"
                engine.recognize.side_effect = ["x+y=z", RuntimeError("bad crop"), "a=b"]
                thread = threading.Thread(target=_serve_locked, args=(Settings(), socket_path), daemon=True)
                thread.start()
                deadline = time.monotonic() + 5
                while not socket_path.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(socket_path.exists())
                try:
                    self.assertEqual(request_recognition(root / "one.png"), "x+y=z")
                    with self.assertRaisesRegex(RuntimeError, "bad crop"):
                        request_recognition(root / "two.png")
                    self.assertEqual(request_recognition(root / "three.png"), "a=b")
                finally:
                    stop_daemon()
                    thread.join(timeout=5)
                self.assertFalse(thread.is_alive())
                self.assertFalse(socket_path.exists())
                engine.load.assert_called_once()
                recognizer.assert_called_once()
                logs = (root / "formulens/daemon.log").read_text()
                for expected in ("Processing", "Ready in", "x+y=z", "bad crop", "a=b", "Daemon stopped"):
                    self.assertIn(expected, logs)

    def test_off_does_not_load_model_or_configuration(self) -> None:
        with (
            patch("formulens.commands.daemon.stop_daemon") as stop,
            patch("formulens.commands.daemon.load_configuration") as configuration,
            patch("formulens.commands.daemon.serve") as serve,
        ):
            result = CliRunner().invoke(app, ["daemon", "off"])
            self.assertEqual(result.exit_code, 0, result.output)
            stop.assert_called_once()
            configuration.assert_not_called()
            serve.assert_not_called()
