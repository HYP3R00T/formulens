"""Verify logging migration, session context, rotation, and handler cleanup."""

import os
import tempfile
import unittest
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

from formulens.recognition.logging import configure_logging, get_log_path
from utilityhub_logging import bind_context, cleanup_logging


class LoggingTests(unittest.TestCase):
    def test_sessions_preserve_old_logs_and_keep_latest_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}):
            path = get_log_path()
            path.parent.mkdir()
            path.write_text("prior daemon history\n")
            logger = configure_logging(console_output=False)
            try:
                self.assertTrue(path.is_symlink())
                previous = list(path.parent.glob("*.previous.log"))
                self.assertEqual(len(previous), 1)
                self.assertEqual(previous[0].read_text(), "prior daemon history\n")
                first_session = path.resolve()
                with bind_context(request_id=42):
                    logger.info("equation completed")
                self.assertIn("request_id=42", path.read_text())
                first_handler = logger.handlers[0]
                assert isinstance(first_handler, RotatingFileHandler)
                configure_logging(console_output=False)
                self.assertIsNone(first_handler.stream)
                self.assertNotEqual(path.resolve(), first_session)
                self.assertTrue(first_session.exists())
                logger.info("new session")
                self.assertIn("new session", path.read_text())
                self.assertNotIn("equation completed", path.read_text())
            finally:
                cleanup_logging(logger)
            self.assertEqual(logger.handlers, [])

    def test_rotation_and_rich_handler_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}):
            logger = configure_logging()
            try:
                file_handler = logger.handlers[0]
                assert isinstance(file_handler, RotatingFileHandler)
                session = Path(file_handler.baseFilename)
                self.assertEqual(file_handler.maxBytes, 2 * 1024 * 1024)
                self.assertEqual(file_handler.backupCount, 3)
                file_handler.maxBytes = 200
                for _ in range(10):
                    logger.debug("rotation payload " * 20)
                self.assertEqual(get_log_path().resolve(), session)
                for suffix in (".1", ".2", ".3"):
                    self.assertTrue(Path(str(session) + suffix).exists())
                self.assertFalse(Path(str(session) + ".4").exists())
            finally:
                cleanup_logging(logger)
            self.assertEqual(logger.handlers, [])
