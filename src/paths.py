"""Locate files that ship inside the installed extension."""

from pathlib import Path


EXTENSION_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = EXTENSION_ROOT / "resources" / "models" / "snapshot.json"
PROJECT_FILE = EXTENSION_ROOT / "pyproject.toml"

__all__ = ["EXTENSION_ROOT", "PROJECT_FILE", "SNAPSHOT_PATH"]
