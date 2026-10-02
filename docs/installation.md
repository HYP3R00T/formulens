# Installation

Version 0.1.0 is being prepared for release. Until it is published, install from
source using the steps below. PyPI version 0.0.1 provides configuration commands
only, without image recognition or capture.

## Requirements

- Linux with an NVIDIA GPU and a working NVIDIA driver.
- Python 3.14 or later and [uv](https://docs.astral.sh/uv/).
- [mise](https://mise.jdx.dev/) for the repository's development tools.
- COSMIC's `cosmic-screenshot` for interactive capture.
- `wl-clipboard` on Wayland, or `xclip`/`xsel` on X11, for clipboard output.
- `notify-send`, usually supplied by `libnotify`, for desktop notifications.

Verify that `nvidia-smi` reports your GPU before starting the model service.
GPU memory requirements depend on the selected model and image size.

## Install from source

```bash
git clone https://github.com/HYP3R00T/formulens.git
cd formulens
mise trust
mise install
uv sync --package formulens --extra ocr
mise run install-cli
```

The workspace selects CUDA-enabled PyTorch from the official CUDA 13.0 wheel
index. The `ocr` extra installs model dependencies. The CLI is installed in
editable mode, so source changes are available to new CLI processes.

If the CLI is not found, run `uv tool update-shell` and open a new terminal.

## Prepare the model

```bash
formulens config init
formulens model-download
```

`model-download` downloads and loads the selected model to verify that it works.
It requires an operational CUDA GPU and exits after verification. You can skip
this step: the daemon also downloads missing model files during its first start.

By default, weights are cached in `~/.config/formulens/models`. Subsequent starts
reuse those files. See [configuration](configuration.md) to change the location
or model, then follow the [usage guide](usage.md).
