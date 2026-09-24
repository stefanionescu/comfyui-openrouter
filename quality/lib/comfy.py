"""Locate the ComfyUI Python installation used for static development checks."""

import os
from pathlib import Path


def host_installation() -> tuple[Path, Path]:
    """Require explicit host selection and return its code directory and Python executable."""
    selected = os.environ.get("COMFYUI_PATH", "")
    if not selected:
        msg = "Set COMFYUI_PATH to the ComfyUI directory containing main.py and comfy_api."
        raise ValueError(msg)
    host = Path(selected).expanduser().resolve(strict=True)
    if not (host / "main.py").is_file() or not (host / "comfy_api/latest/__init__.py").is_file():
        msg = "COMFYUI_PATH must contain ComfyUI's main.py and comfy_api directory."
        raise ValueError(msg)
    default_python = host / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    interpreter = Path(os.environ.get("COMFYUI_PYTHON", str(default_python))).expanduser().absolute()
    if not interpreter.is_file():
        msg = "Set COMFYUI_PYTHON to the Python executable used by this ComfyUI installation."
        raise ValueError(msg)
    return host, interpreter
