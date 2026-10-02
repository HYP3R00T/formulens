"""Configuration CLI integration tests with an isolated home directory."""

import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from formulens.cli import app
from typer.testing import CliRunner


class ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.path = self.home / ".config" / "formulens" / "formulens.toml"
        self.enterContext(patch("pathlib.Path.home", return_value=self.home))
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.runner = CliRunner()

    def test_path_and_show_do_not_create_files(self) -> None:
        result = self.runner.invoke(app, ["config", "path"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output.strip(), str(self.path))
        result = self.runner.invoke(app, ["config", "show"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(json.loads(result.output), {"copy_to_clipboard": True, "notifications": True})
        self.assertFalse(self.path.exists())

    def test_init_preserves_edits_and_set_roundtrips(self) -> None:
        for arguments in (["init"], ["set", "notifications", "false"], ["init"]):
            result = self.runner.invoke(app, ["config", *arguments])
            self.assertEqual(result.exit_code, 0, result.output)
        values = tomllib.loads(self.path.read_text())
        self.assertFalse(values["notifications"])
        self.assertTrue(values["copy_to_clipboard"])

    def test_environment_override_is_not_saved_by_set(self) -> None:
        os.environ["FORMULENS_NOTIFICATIONS"] = "false"
        result = self.runner.invoke(app, ["config", "show"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertFalse(json.loads(result.output)["notifications"])
        result = self.runner.invoke(app, ["config", "set", "copy_to_clipboard", "false"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(tomllib.loads(self.path.read_text())["notifications"])

    def test_invalid_edits_do_not_change_file(self) -> None:
        self.runner.invoke(app, ["config", "init"])
        original = self.path.read_bytes()
        for key, value in (("missing", "true"), ("notifications", "invalid")):
            result = self.runner.invoke(app, ["config", "set", key, value])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Configuration error:", result.output)
            self.assertEqual(self.path.read_bytes(), original)

    def test_malformed_file_is_reported_and_preserved(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("notifications = [")
        for command in ("show", "init"):
            result = self.runner.invoke(app, ["config", command])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Configuration error:", result.output)
        self.assertEqual(self.path.read_text(), "notifications = [")

    def test_current_directory_config_is_not_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch("pathlib.Path.cwd", return_value=Path(directory)):
            working_directory = Path(directory)
            (working_directory / "formulens.toml").write_text("notifications = false\n")
            (working_directory / ".env").write_text("NOTIFICATIONS=false\n")
            result = self.runner.invoke(app, ["config", "show"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(json.loads(result.output)["notifications"])
