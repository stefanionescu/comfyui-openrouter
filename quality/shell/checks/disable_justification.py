"""Validate ShellCheck disable justifications."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_disable_justifications(sources: dict[str, str]) -> list[Diagnostic]:
    """Return diagnostics for shellcheck disables without local reasons."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        lines = source.splitlines()
        for index, line in enumerate(lines):
            if "shellcheck disable=" not in line:
                continue
            window = "\n".join(lines[max(0, index - 2) : index + 2])
            if "lint:justify -- reason:" not in window:
                errors.append(
                    diagnostic(
                        path,
                        index + 1,
                        "shell.disable-justification",
                        "shellcheck disable requires lint:justify reason",
                    ),
                )
    return errors
