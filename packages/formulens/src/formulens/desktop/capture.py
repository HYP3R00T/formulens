"""Capture a single image through COSMIC's interactive screenshot tool."""

import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class CaptureCancelledError(Exception):
    """The user dismissed the capture selector."""


@contextmanager
def capture_equation() -> Iterator[Path]:
    """Move only this request's screenshot to temporary storage and remove it on exit."""
    if shutil.which("cosmic-screenshot") is None:
        raise RuntimeError("COSMIC capture requires cosmic-screenshot on PATH.")
    result = subprocess.run(["cosmic-screenshot", "--notify=false"], capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "COSMIC screenshot failed.")
    output = result.stdout.strip()
    if "cancelled" in output.lower():
        raise CaptureCancelledError
    with tempfile.TemporaryDirectory(prefix="formulens-capture-") as directory:
        temporary = Path(directory) / "equation.png"
        if output:
            source = Path(output.splitlines()[-1])
            if not source.is_file():
                raise RuntimeError("COSMIC did not return a valid screenshot path.")
            shutil.move(str(source), temporary)
        else:
            # COSMIC returns an empty path when the user captures to clipboard.
            result_image = subprocess.run(
                ["wl-paste", "--no-newline", "--type", "image/png"], capture_output=True, check=False
            )
            if result_image.returncode or not result_image.stdout:
                raise RuntimeError("COSMIC clipboard capture is unavailable. Capture to Pictures instead.")
            temporary.write_bytes(result_image.stdout)
        yield temporary
