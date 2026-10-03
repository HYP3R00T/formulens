# Usage

## Start the daemon

```bash
formulens daemon
```

Wait for **Ready**. Keep this terminal open while using Formulens. The model stays
in GPU memory until the daemon stops; each request reuses it.

The Rich display shows loading progress, request numbers, processing time, and
recognized LaTeX. Native capture has been verified in the maintainer's COSMIC
session.

## Run in the background

```bash
formulens daemon on
```

This loads the model, waits until the service is ready, and returns your terminal
prompt. Initial downloads can make the first start slower. The daemon continues
running after you close the terminal; logs still go to
`~/.local/state/formulens/daemon.log`. A second daemon cannot start while one is
already running.

Stop it with `formulens daemon off`. Use plain `formulens daemon` when you want
live logs in the terminal. Background mode does not automatically start at login
or survive a reboot.

## Capture an equation

From another terminal:

```bash
formulens capture
```

Select the equation in COSMIC's screenshot overlay. Formulens reads the returned
image, recognizes it, and copies the LaTeX. A completion notification appears if
notifications are enabled and desktop delivery is available.

Only the screenshot returned by this capture request is processed. The image is
moved into temporary storage and deleted when processing ends, including on
failure. Capturing to COSMIC's clipboard is also supported. Your normal screenshot
shortcut remains available, and Formulens does not watch your Pictures directory.

## Add a keyboard shortcut

In COSMIC Settings, open **Input Devices → Keyboard → Keyboard Shortcuts** and
add a custom shortcut:

- **Name:** Formulens
- **Command:** the absolute path from `command -v formulens`, followed by `capture`
- **Shortcut:** your preferred unused combination, such as Ctrl + Page Down

For example, if the executable is `/home/alex/.local/bin/formulens`, use
`/home/alex/.local/bin/formulens capture`. No terminal wrapper is needed.
Keep the daemon running before using this shortcut. You can retain Ctrl + Page Up
for ordinary COSMIC screenshots.

## Recognize an existing image

```bash
formulens recognize /path/to/equation.png --daemon
```

The source image is preserved. To process a file without a running daemon:

```bash
formulens recognize /path/to/equation.png
```

That command loads a model for the request and exits afterward. To print the
result without copying it:

```bash
formulens recognize /path/to/equation.png --daemon --no-copy
```

`--copy` and `--no-copy` override the saved clipboard preference for that command.

## Stop the daemon

```bash
formulens daemon off
```

Run this from any terminal. Shutdown waits for active recognition to finish.
Ctrl+C in the daemon terminal also stops it. Stop and restart the daemon after
changing its model or inference settings.

## Read the logs

```bash
tail -F ~/.local/state/formulens/daemon.log
```

The log location follows `XDG_STATE_HOME` if set. UtilityHub Logging creates a
file per daemon session; `daemon.log` points to the latest one. Each session file
rotates at 2 MiB, with three backups. Older sessions are retained; remove them
when no longer needed. Logs contain recognized equations, timings, input paths, and full
error tracebacks; screenshot deletion does not remove equation text from logs.
Known upstream compatibility notices are recorded in the file instead of the
terminal. Unexpected warnings remain visible.
