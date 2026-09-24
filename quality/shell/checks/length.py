"""Validate shell length limits."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.shell.parsers import check_function_length_limit, check_module_length_limit

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_length_limits(
    sources: dict[str, str],
    max_file_lines: int,
    max_function_lines: int,
) -> list[Diagnostic]:
    """Return shell file and function length diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        errors.extend(check_module_length_limit(path, source, max_file_lines))
        errors.extend(check_function_length_limit(path, source, max_function_lines))
    return errors
