"""Shell name extraction."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.shell.parsers import collect_shell_functions

if TYPE_CHECKING:
    from quality.repository.naming.types import NameCandidate

ASSIGNMENT_RE = re.compile(r"^(?:local|readonly|export)?\s*([A-Za-z_][A-Za-z0-9_]*)=")
DECLARATION_RE = re.compile(r"^(?:local|readonly|export)\s+([A-Za-z_][A-Za-z0-9_]*)")


def extract_shell_names(relative_path: str, source_text: str) -> list[NameCandidate]:
    """Return shell naming candidates."""
    names: list[NameCandidate] = [
        {
            "path": relative_path,
            "line": function["start"],
            "language": "shell",
            "category": "functions",
            "name": function["name"],
        }
        for function in collect_shell_functions(source_text)
    ]
    for line_number, line in enumerate(source_text.splitlines(), start=1):
        stripped = line.strip()
        match = ASSIGNMENT_RE.match(stripped) or DECLARATION_RE.match(stripped)
        if match:
            names.append(
                {
                    "path": relative_path,
                    "line": line_number,
                    "language": "shell",
                    "category": "variables",
                    "name": match.group(1),
                },
            )
    return names
