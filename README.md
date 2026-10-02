# Formulens

Local equation-to-LaTeX recognition with a Linux-first CLI.

The development checkout now includes PaddleOCR-VL and GOT-OCR backends, image
recognition, a model daemon, and a COSMIC capture adapter. The published `0.0.1`
release provides configuration management only. Native desktop capture still
needs an interactive check on your COSMIC session.

## Development Setup

Requires Python 3.14, [mise](https://mise.jdx.dev/), and
[uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/HYP3R00T/formulens.git
cd formulens
mise trust
mise install
uv sync --package formulens --extra ocr
mise run install-cli
```

OCR requires an NVIDIA GPU and a working NVIDIA driver. The workspace installs
CUDA-enabled PyTorch from the official CUDA 13.0 wheel index. Recognition has
no CPU fallback. The daemon keeps model weights in GPU memory until it stops.

## Recognize an Existing Image

```bash
formulens model-download
formulens recognize /path/to/equation.png
formulens recognize /path/to/equation.png --no-copy
```

The first run downloads the selected model. Subsequent runs reuse the download.
The command prints LaTeX and copies it unless `--no-copy` is supplied or
`copy_to_clipboard` is disabled. Your source image is never deleted.

## Capture an Equation on COSMIC

Start the model service in a terminal:

```bash
formulens daemon
```

Wait for **Formulens daemon ready**, then run:

```bash
formulens capture
```

Select the equation in COSMIC's normal screenshot overlay. The capture command
uses the image returned by that particular request, moves it into temporary
storage, and deletes it after recognition, including on failure. Capturing to
COSMIC's clipboard is supported too. Ordinary screenshots are not watched or
processed. This does not change your normal screenshot shortcut.

Bind an additional COSMIC custom shortcut to the absolute path printed by
`command -v formulens`, followed by `capture`. Keep the daemon running while
using that shortcut. Stop it with Ctrl+C or from another terminal:

```bash
formulens daemon off
```

Shutdown waits for any active recognition to finish. The daemon prints timestamps,
processing status, elapsed time, recognized LaTeX, and errors to its terminal.
The same logs are stored at `~/.local/state/formulens/daemon.log` (or beneath
`XDG_STATE_HOME`), with rotation at 2 MiB and three backups. Logs retain recognized
equations, but screenshots are still deleted after processing.

```bash
tail -f ~/.local/state/formulens/daemon.log
```

A daemon loads settings once; restart it after changing the model or device.

Existing images can also use the loaded service:

```bash
formulens recognize /path/to/equation.png --daemon
```

Clipboard integration uses Pyperclip to select the operating system backend.
On Wayland it requires `wl-clipboard`; X11 requires `xclip` or `xsel`.
Pyperclip also supports macOS and Windows. Notifications
use `notify-send` when available. Native capture currently requires
`cosmic-screenshot`; other desktop capture adapters can be added separately.

## Configuration and Storage

```bash
formulens config init
formulens config path
formulens config show
formulens config set model got
formulens config set device cuda
formulens config set model_directory '~/.cache/formulens/models'
```

Settings live at `~/.config/formulens/formulens.toml` through
[UtilityHub Config](https://utilityhub.hyperoot.dev/packages/utilityhub_config/):

```toml
copy_to_clipboard = true
notifications = true
model = "paddle"
model_directory = "~/.config/formulens/models"
device = "cuda"
max_tokens = 1024
```

`model` accepts `paddle` or `got`. Models are stored in Hugging Face's cache layout
under `model_directory`, separately from configuration files. Temporary captures
use the system temporary directory; the daemon socket uses the user runtime
directory. Model revisions are fixed in the backend for repeatable downloads.

`init` preserves existing files. Settings require `device = "cuda"`; remove
`cpu_threads` from configs created before GPU-only support. `set` validates edits
before saving. Environment
variables such as `FORMULENS_DEVICE=cuda` override saved values; `set` does not
persist environment overrides. Formulens confines config discovery to its own
configuration directory, including any `.env` there.

Paddle uses optimized SDPA attention and token caching during generation. On an
RTX 3050 Laptop GPU, a synthetic benchmark improved from about 20 seconds to
1.4 seconds with identical output. A fresh optimized model took about 3 seconds
for the first request and 1.2–1.4 seconds afterward. Timing and accuracy depend
on the equation and hardware. Image resolution is unchanged.
Paddle remains the default model; GOT misread a synthetic test crop.

## Code Structure

- `commands/`: CLI commands and error presentation.
- `configuration/`: validated settings and persistence.
- `recognition/`: model inference and the local service.
- `desktop/`: capture, clipboard, and notification adapters.
- `cli.py`: command registration.

These directories live in `packages/formulens/src/formulens/`. The workspace
shares `uv.lock` and uses `mise.toml` for development tooling.

## Checks

```bash
uv run --package formulens --extra ocr python -m unittest discover -s tests
prek run --all-files
```

[Documentation](https://formulens.hyperoot.dev/) ·
[Repository](https://github.com/HYP3R00T/formulens) · MIT license.
