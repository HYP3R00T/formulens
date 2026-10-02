<div align="center">

<h1>Formulens</h1>
<p>For the equations you'd rather understand than type.</p>

<p>
  <a href="https://pypi.org/project/formulens/"><img src="https://img.shields.io/pypi/v/formulens?style=flat-square" alt="PyPI version"></a>
  <a href="https://formulens.hyperoot.dev/user-guide/installation/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white" alt="Python 3.14+"></a>
  <a href="https://formulens.hyperoot.dev/user-guide/installation/"><img src="https://img.shields.io/badge/NVIDIA-CUDA-76B900?style=flat-square&amp;logo=nvidia&amp;logoColor=white" alt="NVIDIA CUDA"></a>
  <a href="https://github.com/HYP3R00T/formulens/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT license"></a>
</p>

<p>
  <a href="https://formulens.hyperoot.dev/">Documentation</a> ·
  <a href="https://formulens.hyperoot.dev/user-guide/installation/">Installation</a> ·
  <a href="https://github.com/HYP3R00T/formulens/issues">Issues</a>
</p>

</div>

Select an equation, get its LaTeX, and get back to your notes. Formulens runs
PaddleOCR-VL or GOT-OCR locally on your NVIDIA GPU and copies the result, ready
to paste. Its daemon keeps the model loaded between captures.

On COSMIC, bind a keyboard shortcut to open the screenshot selector. Temporary
captures are deleted after processing; existing images are preserved.

Requires **Python 3.14+** and **NVIDIA CUDA**. Native capture and daemon support
currently target Linux.

## Quick Start

Follow the [installation guide](https://formulens.hyperoot.dev/user-guide/installation/),
then keep the daemon running:

```bash
formulens daemon
```

From another terminal or your capture shortcut:

```bash
formulens capture
formulens recognize /path/to/equation.png --daemon
formulens daemon off
```

See the [docs](https://formulens.hyperoot.dev/) for shortcuts, configuration,
models, logs, and troubleshooting.

<p align="center">Built with ❤️ by <a href="https://github.com/HYP3R00T">@HYP3R00T</a></p>
