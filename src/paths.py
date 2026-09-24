"""Locate files that ship inside the installed extension."""

from pathlib import Path


EXTENSION_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = EXTENSION_ROOT / "resources" / "models" / "snapshot.json"

__all__ = ["EXTENSION_ROOT", "SNAPSHOT_PATH"]
