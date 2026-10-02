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

1. [Install Formulens](user-guide/installation.md) with Python 3.14 and CUDA support.
2. [Start the daemon and configure a capture shortcut](user-guide/usage.md).
3. [Choose a model and configure preferences](user-guide/configuration.md).

PaddleOCR-VL is the default model; GOT-OCR is also available. Native capture and
daemon support currently target Linux. Clipboard integration uses Pyperclip.
Recognition requires NVIDIA CUDA; there is no CPU fallback.

## More information

- [Usage](user-guide/usage.md): captures, existing images, daemon shutdown, and logs.
- [Troubleshooting](user-guide/troubleshooting.md): GPU setup, notifications, and recognition.
- [Development](contributors/development.md): workspace layout, checks, and local docs.
- [Publishing](contributors/publishing.md): the manual release process for maintainers.
