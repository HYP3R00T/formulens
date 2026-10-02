"""Console and rotating file logs for the model service."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_path() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))).expanduser()
    return root / "formulens" / "daemon.log"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("formulens.daemon")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    path = get_log_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    file_handler = RotatingFileHandler(path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    path.chmod(0o600)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    for handler in (logging.StreamHandler(), file_handler):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
