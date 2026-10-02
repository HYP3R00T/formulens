# Changelog

## 0.1.0 (unreleased)

- Recognize equation images locally with PaddleOCR-VL or GOT-OCR.
- Require NVIDIA CUDA for OCR and retain the loaded model in GPU memory while
  the daemon runs.
- Capture equations through COSMIC, copy LaTeX to the clipboard, notify when
  ready, and delete temporary screenshots after processing.
- Process existing images without deleting them.
- Stop the resident service with `formulens daemon off`.
- Show readable Rich daemon output and retain rotating logs with equations,
  timings, and error details.
- Improve Paddle generation speed with token caching and optimized attention.
- Use Pyperclip for clipboard backend selection across operating systems.
- Store downloaded models in a configurable directory, defaulting to
  `~/.config/formulens/models`.
- Correct Paddle's untied-weight configuration and retain known upstream
  compatibility notices in the log file.

### Requirements and compatibility

- Python 3.14 or later, CUDA-enabled PyTorch, and a working NVIDIA GPU driver.
- Install the `ocr` extra for recognition support.
- Native capture and daemon support currently target Linux; COSMIC capture uses
  `cosmic-screenshot`, and notifications use `notify-send`.
- Configure `device = "cuda"` and remove `cpu_threads` from older configurations.
- Recognition accuracy and latency depend on the model, crop, and hardware.

## 0.0.1

- Initial PyPI release with Typer commands and UtilityHub configuration management.
