# Troubleshooting

## CUDA is unavailable

Formulens requires NVIDIA CUDA and never falls back to CPU. Check `nvidia-smi`
and confirm that the active Python environment has CUDA-enabled PyTorch.
For a source checkout:

```bash
uv run --package formulens --extra ocr python -c \
  'import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())'
```

A `None` CUDA version indicates a PyTorch build without CUDA support. A CUDA
version with `False` availability usually requires checking the GPU driver or
environment access. Follow the [installation guide](installation.md).

## A daemon is already running

```bash
formulens daemon off
formulens daemon
```

Only one daemon runs per user runtime directory. `off` may wait while an active
recognition finishes. To update an older daemon that predates the shutdown
command, stop it with Ctrl+C in its terminal first.

## The shortcut does nothing

Confirm that the daemon reports **Ready**, the shortcut uses the absolute CLI
path, and `cosmic-screenshot` is installed. Run `formulens capture` in a terminal
to see any capture or clipboard error.

## LaTeX is copied, but no notification appears

```bash
formulens config show
notify-send Formulens 'Notification test'
```

Both `copy_to_clipboard` and `notifications` must be enabled for completion
notifications. If the notification test does not appear, check your desktop's
notification settings and session. Notification failures produce a warning in
the capture command. On COSMIC Wayland, install `wl-clipboard` for copying.

## Slow or inaccurate recognition

The daemon retains the model, avoiding reloads between captures. Paddle uses
optimized attention and token caching. On an RTX 3050 Laptop GPU, a synthetic
benchmark improved from about 20 seconds to 1.4 seconds with identical output.
The first optimized request took about 3 seconds; subsequent requests took
1.2–1.4 seconds. Actual book captures have taken around 2–3 seconds in testing.
These timings depend on image size, output length, GPU load, and hardware.

Crop closely around the equation, keep symbols legible, and review the output.
A blank result, chemistry markup, or output reaching the token limit is rejected.
Change `max_tokens` if a long equation reaches the limit.

## Compatibility notices in the log

The pinned Paddle checkpoint uses an upstream processor declaration deprecated
by newer Transformers versions. Its `mrope_section` field is used by Paddle's
rotary-position implementation, although a generic validator reports it as
unrecognized. Formulens keeps these known notices in the log file, leaving
unexpected warnings and errors visible.

The backend explicitly preserves the checkpoint's untied embedding weights,
preventing the misleading tied-weights warning. Checkpoint files are not modified.
