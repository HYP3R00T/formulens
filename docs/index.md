---
icon: lucide/scan
---

# Formulens

Turn equation screenshots into LaTeX without typing them out.

Formulens runs locally on an NVIDIA GPU. Start its daemon, use a keyboard
shortcut to select an equation on COSMIC, and paste the recognized LaTeX into
your notes when the completion notification appears. The daemon keeps the model
loaded between requests.

You can also recognize an existing image. Temporary screenshots are deleted
once processing ends; files supplied to `recognize` are preserved.

## Get started

1. [Install Formulens](installation.md) with Python 3.14 and CUDA support.
2. [Start the daemon and configure a capture shortcut](usage.md).
3. [Choose a model and configure preferences](configuration.md).

PaddleOCR-VL is the default model; GOT-OCR is also available. Native capture and
daemon support currently target Linux. Clipboard integration uses Pyperclip.
Recognition requires NVIDIA CUDA; there is no CPU fallback.

## More information

- [Usage](usage.md): captures, existing images, daemon shutdown, and logs.
- [Troubleshooting](troubleshooting.md): GPU setup, notifications, and recognition.
- [Development](development.md): workspace layout, checks, and local docs.
- [Release notes](releases.md): the upcoming 0.1.0 release and initial 0.0.1 release.
