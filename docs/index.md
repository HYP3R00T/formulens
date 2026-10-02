---
icon: lucide/scan
---

# Formulens

NVIDIA GPU equation-to-LaTeX recognition with a Linux-first CLI.

The development checkout provides image recognition through PaddleOCR-VL or
GOT-OCR, a model daemon, and a COSMIC capture adapter. Native desktop capture
still needs an interactive verification on COSMIC. PyPI version `0.0.1` contains
configuration management only. Recognition requires CUDA-enabled PyTorch and a
working NVIDIA driver. The daemon keeps the model in GPU memory until it stops;
there is no CPU fallback.

## Commands

```bash
formulens config show
formulens model-download
formulens recognize /path/to/equation.png --no-copy
formulens daemon
```

Once the daemon reports ready, `formulens capture` opens COSMIC's screenshot
selector and sends the selected image to the loaded model. Temporary captures
are deleted after processing. Existing images are preserved.

Stop the service from any terminal with `formulens daemon off`. Requests,
recognized equations, timings, and errors appear in the daemon terminal and
`~/.local/state/formulens/daemon.log`; logs rotate automatically.

Settings are stored at `~/.config/formulens/formulens.toml`; downloaded models
use `~/.config/formulens/models` by default. Change this location with
`formulens config set model_directory /your/model/cache`.

See the [repository README](https://github.com/HYP3R00T/formulens#readme) for
installation, settings, desktop requirements, and development checks.
