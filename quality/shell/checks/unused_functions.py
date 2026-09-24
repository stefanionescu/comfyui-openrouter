"""Detect unused shell functions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.parsers import collect_shell_functions, shell_identifier_references

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_unused_functions(sources: dict[str, str]) -> list[Diagnostic]:
    """Return diagnostics for unused shell functions."""
    errors: list[Diagnostic] = []
    references_by_path = {path: shell_identifier_references(source) for path, source in sources.items()}
    for path, source in sources.items():
        for function in collect_shell_functions(source):
            name = str(function["name"])
            if name in {"main", "run_step"}:
                continue
            reference_count = sum(len(references.get(name, ())) for references in references_by_path.values())
            if reference_count == 0:
                errors.append(diagnostic(path, function["start"], "shell.unused-function", f"{name} is not called"))
    return errors
