"""Exercise detached daemon startup and shutdown without loading GPU weights."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from formulens.cli import app
from formulens.recognition.service import get_socket_path, request_recognition
from typer.testing import CliRunner

FAKE_MODEL = """
from contextlib import nullcontext
from formulens.configuration.schema import Settings
from formulens.recognition import background, service
class Model:
    device = 'cuda'
    def __init__(self, settings):
        pass
    def load(self):
        pass
    def recognize(self, path):
        return 'x+y=z'
service.EquationRecognizer = Model
service.model_loading_output = lambda logger: nullcontext()
background.load_configuration = lambda: Settings()
"""


class BackgroundTests(unittest.TestCase):
    def run_worker(self, *, fail_loading: bool = False) -> None:
        real_popen = subprocess.Popen
        workers = []
        prefix = FAKE_MODEL
        if fail_loading:
            prefix += "def fail(self): raise RuntimeError('CUDA startup failed')\nModel.load = fail\n"

        def spawn(command, **kwargs):
            worker = real_popen([*command[:-1], prefix + command[-1]], **kwargs)
            workers.append(worker)
            return worker

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory, "XDG_STATE_HOME": directory}),
                patch("formulens.recognition.background.subprocess.Popen", side_effect=spawn),
            ):
                try:
                    result = CliRunner().invoke(app, ["daemon", "on"])
                    if fail_loading:
                        self.assertEqual(result.exit_code, 1, result.output)
                        self.assertIn("failed to start", result.output)
                        self.assertIsNotNone(workers[0].poll())
                        self.assertIn("CUDA startup failed", (root / "formulens/daemon.log").read_text())
                        return
                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertIn("Background daemon ready", result.output)
                    self.assertEqual(os.getsid(workers[0].pid), workers[0].pid)
                    self.assertEqual(request_recognition(root / "equation.png"), "x+y=z")
                    duplicate = CliRunner().invoke(app, ["daemon", "on"])
                    self.assertEqual(duplicate.exit_code, 1, duplicate.output)
                    self.assertIn("already running", duplicate.output)
                    self.assertEqual(len(workers), 1)
                    foreground = CliRunner().invoke(app, ["daemon"])
                    self.assertEqual(foreground.exit_code, 1, foreground.output)
                    self.assertIn("already running", foreground.output)
                    stopped = CliRunner().invoke(app, ["daemon", "off"])
                    self.assertEqual(stopped.exit_code, 0, stopped.output)
                    self.assertEqual(workers[0].wait(timeout=5), 0)
                    self.assertFalse(get_socket_path().exists())
                    logs = (root / "formulens/daemon.log").read_text()
                    self.assertIn("LaTeX: x+y=z", logs)
                    self.assertIn("Daemon stopped", logs)
                finally:
                    for worker in workers:
                        if worker.poll() is None:
                            worker.terminate()
                        worker.wait(timeout=5)

    def test_background_survives_launch_and_off_stops_it(self) -> None:
        self.run_worker()

    def test_loading_failure_is_reported_and_logged(self) -> None:
        self.run_worker(fail_loading=True)
