"""Exercise capture cleanup, clipboard selection, and recognition routing."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from formulens.cli import app
from formulens.configuration.schema import Settings
from formulens.desktop.capture import CaptureCancelledError, capture_equation
from formulens.desktop.output import copy_latex, notify_ready
from formulens.recognition.engine import clean_latex
from typer.testing import CliRunner


class WorkflowTests(unittest.TestCase):
    def test_display_wrappers_are_removed(self) -> None:
        for text in ("$$x+y$$", "\\[x+y\\]", "```latex\nx+y\n```", "x+y"):
            self.assertEqual(clean_latex(text), "x+y")

    def test_chemistry_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "chemistry markup"):
            clean_latex("<smiles>[X+3]</smiles>")

    def test_capture_moves_only_returned_image_and_cleans_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "equation.png"
            normal = Path(directory) / "normal.png"
            source.write_bytes(b"equation")
            normal.write_bytes(b"normal")
            result = subprocess.CompletedProcess([], 0, stdout=str(source) + "\n", stderr="")
            with (
                patch("formulens.desktop.capture.shutil.which", return_value="cosmic-screenshot"),
                patch("formulens.desktop.capture.subprocess.run", return_value=result),
                self.assertRaisesRegex(RuntimeError, "inference failed"),
                capture_equation() as captured,
            ):
                self.assertEqual(captured.read_bytes(), b"equation")
                self.assertFalse(source.exists())
                raise RuntimeError("inference failed")
            self.assertFalse(captured.exists())
            self.assertEqual(normal.read_bytes(), b"normal")

    def test_capture_cancel_does_not_read_clipboard(self) -> None:
        result = subprocess.CompletedProcess([], 0, stdout="Screenshot cancelled by user\n", stderr="")
        with (
            patch("formulens.desktop.capture.shutil.which", return_value="cosmic-screenshot"),
            patch("formulens.desktop.capture.subprocess.run", return_value=result) as run,
        ):
            with self.assertRaises(CaptureCancelledError), capture_equation():
                self.fail("Cancelled capture should not yield a file")
            self.assertEqual(run.call_count, 1)

    def test_clipboard_capture_is_temporary(self) -> None:
        results = [
            subprocess.CompletedProcess([], 0, stdout="", stderr=""),
            subprocess.CompletedProcess([], 0, stdout=b"image bytes", stderr=b""),
        ]
        with (
            patch("formulens.desktop.capture.shutil.which", return_value="cosmic-screenshot"),
            patch("formulens.desktop.capture.subprocess.run", side_effect=results),
        ):
            with capture_equation() as captured:
                self.assertEqual(captured.read_bytes(), b"image bytes")
            self.assertFalse(captured.exists())

    def test_clipboard_delegates_to_pyperclip(self) -> None:
        with patch("formulens.desktop.output.pyperclip.copy") as copy:
            copy_latex("\\frac{a}{b}")
            copy.assert_called_once_with("\\frac{a}{b}")

    def test_existing_image_is_preserved_and_no_copy_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "image.png"
            image.write_bytes(b"example")
            with (
                patch("formulens.commands.recognize.load_configuration", return_value=Settings()),
                patch("formulens.commands.recognize.EquationRecognizer") as engine,
            ):
                engine.return_value.recognize.return_value = "x+y"
                with patch("formulens.commands.recognize.copy_latex") as copy:
                    result = CliRunner().invoke(app, ["recognize", str(image), "--no-copy"])
                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertEqual(result.output.strip(), "x+y")
                    copy.assert_not_called()
            self.assertEqual(image.read_bytes(), b"example")

    def test_clipboard_backend_failure_is_reported(self) -> None:
        with (
            patch("formulens.desktop.output.pyperclip.copy", side_effect=OSError("backend unavailable")),
            self.assertRaisesRegex(RuntimeError, "Clipboard copy failed: backend unavailable"),
        ):
            copy_latex("x+y")

    def test_loaded_model_is_reused_without_importing_or_moving_again(self) -> None:
        from formulens.recognition.engine import EquationRecognizer

        engine = EquationRecognizer(Settings(device="cuda"))
        resident_model = object()
        engine.model = resident_model
        engine.device = "cuda"
        with patch.dict(sys.modules, {"torch": None, "transformers": None}):
            engine.load()
            engine.load()
        self.assertIs(engine.model, resident_model)
        self.assertEqual(engine.device, "cuda")

    def test_cpu_and_auto_device_settings_are_rejected(self) -> None:
        for device in ("cpu", "auto"):
            with self.assertRaises(ValueError):
                Settings.model_validate({"device": device})

    def test_cuda_is_required_before_model_download(self) -> None:
        from formulens.recognition.engine import EquationRecognizer

        for version, available, message in (
            (None, False, "CUDA-enabled PyTorch"),
            ("13.0", False, "NVIDIA CUDA is unavailable"),
        ):
            torch = SimpleNamespace(
                version=SimpleNamespace(cuda=version, hip=None),
                cuda=SimpleNamespace(is_available=MagicMock(return_value=available)),
            )
            transformers = MagicMock()
            with (
                patch.dict(sys.modules, {"torch": torch, "transformers": transformers}),
                self.assertRaisesRegex(RuntimeError, message),
            ):
                EquationRecognizer(Settings()).load()
            transformers.AutoProcessor.from_pretrained.assert_not_called()
            transformers.AutoModelForImageTextToText.from_pretrained.assert_not_called()

    def test_notification_failure_is_reported(self) -> None:
        with (
            patch("formulens.desktop.output.shutil.which", return_value="notify-send"),
            patch(
                "formulens.desktop.output.subprocess.run",
                return_value=subprocess.CompletedProcess([], 1, stdout="", stderr="D-Bus unavailable"),
            ),
            self.assertWarnsRegex(RuntimeWarning, "D-Bus unavailable"),
        ):
            notify_ready()

    def test_daemon_client_does_not_load_another_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "image.png"
            image.write_bytes(b"example")
            with (
                patch("formulens.commands.recognize.load_configuration", return_value=Settings()),
                patch("formulens.commands.recognize.request_recognition", return_value="x+y") as request,
                patch("formulens.commands.recognize.EquationRecognizer") as engine,
            ):
                result = CliRunner().invoke(app, ["recognize", str(image), "--daemon", "--no-copy"])
                self.assertEqual(result.exit_code, 0, result.output)
                request.assert_called_once_with(image)
                engine.assert_not_called()

    def test_invalid_model_setting_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Settings.model_validate({"model": "unknown"})
        with self.assertRaises(ValueError):
            Settings(max_tokens=0)
