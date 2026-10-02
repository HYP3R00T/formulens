"""Present recognition output on the Linux desktop."""

import shutil
import subprocess
import warnings

import pyperclip


def copy_latex(text: str) -> None:
    """Let Pyperclip select the native clipboard backend for this session."""
    try:
        pyperclip.copy(text)
    except (pyperclip.PyperclipException, OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"Clipboard copy failed: {exc}") from exc


def notify_ready() -> None:
    """Show a notification when the desktop provides notify-send."""
    if not shutil.which("notify-send"):
        warnings.warn("Notifications require notify-send.", RuntimeWarning, stacklevel=2)
        return
    try:
        result = subprocess.run(
            ["notify-send", "--app-name=Formulens", "Formulens", "LaTeX ready to paste"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode:
            warnings.warn(result.stderr.strip() or "Desktop notification failed.", RuntimeWarning, stacklevel=2)
    except (OSError, subprocess.TimeoutExpired) as exc:
        warnings.warn(f"Desktop notification failed: {exc}", RuntimeWarning, stacklevel=2)
