"""Path name extraction."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quality.repository.naming.types import NameCandidate


def extract_path_names(relative_path: str, language: str) -> list[NameCandidate]:
    """Return file and directory naming candidates."""
    path = Path(relative_path)
    entries: list[NameCandidate] = []
    for part in path.parent.parts:
        if part in {".", ""}:
            continue
        entries.append(
            {"path": relative_path, "line": 1, "language": language, "category": "directories", "name": part},
        )
    entries.append({"path": relative_path, "line": 1, "language": language, "category": "files", "name": path.stem})
    return entries
