"""Validate repository folder names."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.config.repository.paths import QUALITY_EXCLUDED_DIRS
from quality.config.shell import ALLOWED_SCRIPT_ROOT_FOLDERS, ALLOWED_SINGLE_SCRIPT_FOLDERS
from quality.config.repository.folders import (
    AMBIGUOUS_FOLDER_ALLOWLIST,
    DISALLOWED_AMBIGUOUS_FOLDER_NAMES,
    AMBIGUOUS_FOLDER_EXCLUDED_PREFIXES,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_single_script_folders(files: list[str]) -> list[Diagnostic]:
    """Return single-script folder diagnostics."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for file in files:
        grouped[Path(file).parent.as_posix()].append(Path(file).name)
    errors: list[Diagnostic] = []
    for folder, names in grouped.items():
        if folder in {*ALLOWED_SCRIPT_ROOT_FOLDERS, *ALLOWED_SINGLE_SCRIPT_FOLDERS}:
            continue
        if len(names) == 1:
            errors.append(
                diagnostic(
                    f"{folder}/{names[0]}",
                    1,
                    "shell.single-file-folder",
                    "shell folder contains only one script",
                ),
            )
    return errors


def collect_ambiguous_folder_violations(root: Path) -> list[str]:
    """Return ambiguous folder diagnostics without entering excluded trees."""
    violations: list[str] = []
    for directory, names, _filenames in root.walk(top_down=True):
        candidates: list[str] = []
        for name in names:
            path = directory / name
            relative_path = path.relative_to(root).as_posix()
            if name in QUALITY_EXCLUDED_DIRS or relative_path.startswith(tuple(AMBIGUOUS_FOLDER_EXCLUDED_PREFIXES)):
                continue
            candidates.append(name)
            if relative_path not in AMBIGUOUS_FOLDER_ALLOWLIST and name in DISALLOWED_AMBIGUOUS_FOLDER_NAMES:
                violations.append(f"{relative_path}/ uses disallowed ambiguous folder name")
        names[:] = candidates
    return violations
