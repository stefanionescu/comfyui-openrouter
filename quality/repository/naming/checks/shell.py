"""Validate shell script names."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.naming.rules import VAGUE_SCRIPT_NAMES
from quality.shell.checks.prefix_collisions import (
    check_bash_prefix_collisions,
    check_file_directory_collisions,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_shell_names(files: list[str]) -> list[Diagnostic]:
    """Return shell script name diagnostics."""
    errors = [
        diagnostic(file, 1, "shell.vague-name", "script uses vague owner name")
        for file in files
        if Path(file).stem in VAGUE_SCRIPT_NAMES
    ]
    errors.extend(check_bash_prefix_collisions(files))
    errors.extend(check_file_directory_collisions(files))
    return errors
