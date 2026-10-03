# Changelog

## 0.1.1 — 2026-10-03

### Added

- `formulens daemon on` starts the GPU service in the background, with file logs and shutdown through `daemon off`.

### Changed

- Use UtilityHub Logging for session files, context, and cleanup while keeping Rich output and rotating logs.

### Fixed

- Refresh the editable CLI environment during installation so new dependencies are available.

### Documentation

- Explain the XDG state directory, session logs, rotation, retention, and live log viewing.

## 0.1.0 — 2026-10-02

### Added

- Local equation-to-LaTeX recognition using PaddleOCR-VL or GOT-OCR on NVIDIA GPUs.
- COSMIC capture with clipboard output, completion notifications, and temporary image cleanup.
- A persistent GPU daemon with shutdown commands, Rich status output, and rotating logs.
- Commands for recognizing existing images and downloading models.

### Improved

- Faster Paddle inference through SDPA attention and generation caching.
- User guides for installation, capture shortcuts, configuration, and troubleshooting.

## 0.0.1

- Initial PyPI release with CLI configuration commands backed by UtilityHub Config.
