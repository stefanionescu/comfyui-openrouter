"""Validate shell heredoc blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_unnamed_heredocs(sources: dict[str, str]) -> list[Diagnostic]:
    """Return diagnostics for unnamed multi-line SSH heredocs."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        lines = source.splitlines()
        for index, line in enumerate(lines):
            if "ssh " in line and "<<" in line:
                previous = lines[index - 1].strip() if index > 0 else ""
                if not previous.startswith("# ") or " - " not in previous:
                    errors.append(
                        diagnostic(
                            path,
                            index + 1,
                            "shell.unnamed-ssh-block",
                            "multi-line SSH blocks must be named and documented",
                        ),
                    )
    return errors
