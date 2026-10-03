"""Console and rotating file logs for the model service."""

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from copy import copy
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from utilityhub_logging import cleanup_logging, configure_app_logging
from utilityhub_logging.cleanup import mark_handler
from utilityhub_logging.types import ManagedHandlerKind

console = Console(stderr=True)


class ConsoleLogHandler(RichHandler):
    """Keep errors concise on screen; the file handler retains full tracebacks."""

    def emit(self, record: logging.LogRecord) -> None:
        display = copy(record)
        if display.exc_info:
            display.msg = f"{record.getMessage()}: {display.exc_info[1]}"
            display.args = ()
            display.exc_info = None
            display.exc_text = None
        super().emit(display)


class CompatibilityNoticeFilter(logging.Filter):
    """Keep known upstream notices in the file without cluttering the terminal."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        processor_notice = (
            record.name.startswith("transformers")
            and "`PaddleOCRVLProcessor` defines `image_processor_class" in message
            and "deprecated" in message
        )
        rope_notice = (
            record.name.startswith("transformers")
            and message.startswith("Unrecognized keys in `rope_parameters`")
            and message.endswith("{'mrope_section'}")
        )
        return record.levelno >= logging.ERROR or not (processor_notice or rope_notice)


@contextmanager
def model_loading_output(logger: logging.Logger) -> Iterator[None]:
    """Render model loading once and route library diagnostics through our logs."""
    from transformers.utils import logging as transformer_logging

    library_logger = logging.getLogger("transformers")
    handlers = library_logger.handlers[:]
    level, propagate = library_logger.level, library_logger.propagate
    progress = transformer_logging.is_progress_bar_enabled()
    library_logger.handlers = logger.handlers[:]
    library_logger.setLevel(logging.WARNING)
    library_logger.propagate = False
    transformer_logging.disable_progress_bar()
    try:
        with console.status("Loading model into NVIDIA GPU memory…", spinner="dots"):
            yield
    finally:
        library_logger.handlers = handlers
        library_logger.setLevel(level)
        library_logger.propagate = propagate
        if progress:
            transformer_logging.enable_progress_bar()


def get_log_path() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))).expanduser()
    return root / "formulens" / "daemon.log"


def configure_logging(*, console_output: bool = True) -> logging.Logger:
    logger = logging.getLogger("formulens.daemon")
    path = get_log_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    session_path = configure_app_logging(
        app_name="formulens",
        logger=logger,
        level="DEBUG",
        logs_path=path.parent,
        console=False,
    )
    # Keep UtilityHub's formatter/context while adding stdlib size-based rotation.
    file_handler = next(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler))
    rotating = RotatingFileHandler(session_path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    rotating.setFormatter(file_handler.formatter)
    for log_filter in file_handler.filters:
        rotating.addFilter(log_filter)
    cleanup_logging(logger)
    logger.addHandler(mark_handler(rotating, kind=ManagedHandlerKind.APP, file_path=session_path))
    session_path.chmod(0o600)
    # Preserve the old fixed log on the first migration; point daemon.log at this run.
    if path.exists() and not path.is_symlink():
        path.rename(session_path.with_suffix(".previous.log"))
    link = path.with_suffix(".log.tmp")
    link.unlink(missing_ok=True)
    link.symlink_to(session_path.name)
    link.replace(path)
    if not console_output:
        return logger
    terminal = ConsoleLogHandler(console=console, show_path=False, log_time_format="%H:%M:%S")
    terminal.setLevel(logging.INFO)
    terminal.addFilter(CompatibilityNoticeFilter())
    terminal.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(mark_handler(terminal, kind=ManagedHandlerKind.APP))
    return logger
