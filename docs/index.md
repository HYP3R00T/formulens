---
icon: lucide/scan
---

# Formulens

Local equation-to-LaTeX recognition with a Linux-first CLI.

The repository currently contains a Python 3.14 workspace with a single
`formulens` package. Its Typer CLI provides `config init`, `config path`,
`config show`, and `config set` using UtilityHub Config. Settings are stored in
`~/.config/formulens/formulens.toml`. Equation recognition, capture, daemon mode,
and clipboard integration are not implemented yet.
