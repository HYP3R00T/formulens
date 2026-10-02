# Configuration and models

Settings are managed through [UtilityHub Config](https://utilityhub.hyperoot.dev/packages/utilityhub_config/).
They normally live in `~/.config/formulens/formulens.toml`. Use `config path` to
check the location on your system.

## Commands

```bash
formulens config init
formulens config path
formulens config show
formulens config set model paddle
formulens config set notifications true
```

`init` preserves an existing valid file. `show` prints effective settings,
including environment overrides. `set` validates values before saving them.

## Defaults

```toml
copy_to_clipboard = true
notifications = true
model = "paddle"
model_directory = "~/.config/formulens/models"
device = "cuda"
max_tokens = 1024
```

| Setting | Meaning |
| --- | --- |
| `copy_to_clipboard` | Copy recognized LaTeX by default. |
| `notifications` | Notify when copied LaTeX is ready. |
| `model` | `paddle` or `got`; Paddle is the default. |
| `model_directory` | Location of downloaded model files. |
| `device` | Must be `cuda`; NVIDIA GPU recognition only. |
| `max_tokens` | Maximum output tokens, from 16 to 4096. |

An output that reaches `max_tokens` is rejected as potentially incomplete.
Raising this limit allows longer output; it does not force generation to use all
those tokens.

Environment variables such as `FORMULENS_MODEL=got` override saved settings.
Config discovery stays within Formulens' configuration directory, including any
`.env` there. `config set` does not persist environment overrides.

Older development configurations must use `device = "cuda"` and remove the
obsolete `cpu_threads` field. Restart the daemon after changing inference settings.

## Model selection

- **PaddleOCR-VL:** the default backend, with optimized SDPA attention and token
  caching during generation.
- **GOT-OCR:** an alternative backend. It misread a synthetic test crop as
  chemistry markup; such output is rejected rather than copied.

```bash
formulens config set model got
formulens model-download
```

Both models use fixed Hugging Face revisions for repeatable downloads. Accuracy
varies with the equation and crop; review recognized LaTeX before using it.

## Storage locations

| Content | Default location |
| --- | --- |
| Configuration | `~/.config/formulens/formulens.toml` |
| Downloaded models | `~/.config/formulens/models` |
| Daemon logs | `~/.local/state/formulens/daemon.log` |
| Temporary captures | System temporary directory; deleted after processing |
| Daemon socket and lock | `$XDG_RUNTIME_DIR/formulens/` |

Model files use Hugging Face's cache layout. To put them in the conventional
cache directory instead:

```bash
formulens config set model_directory '~/.cache/formulens/models'
```

Changing the directory does not move existing downloads. The daemon downloads
missing files into the selected location on its next start.
