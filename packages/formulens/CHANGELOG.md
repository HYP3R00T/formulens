# Changelog

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
