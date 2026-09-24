"""Diagnostic records for quality tools."""

from __future__ import annotations

from quality.lib.output import write_error
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence


class Diagnostic(TypedDict):
    """One quality diagnostic."""

    path: str
    line: int
    code: str
    message: str


class NamedDiagnostic(Diagnostic, total=False):
    """One quality diagnostic that includes a symbol name."""

    name: str


def diagnostic(path: str, line: int, code: str, message: str) -> Diagnostic:
    """Build one quality diagnostic."""
    line = max(line, 1)
    if not path:
        path = "<unknown>"
    return {"path": path, "line": line, "code": code, "message": message}


def format_diagnostic(item: Diagnostic) -> str:
    """Return a stable diagnostic line."""
    location = f"{item['path']}:{item['line']}"
    if not item["code"]:
        return f"- {location}: {item['message']}"
    return f"- {location}: {item['code']}: {item['message']}"


def report_diagnostics(header: str, diagnostics: Sequence[Diagnostic]) -> int:
    """Print diagnostics and return a command exit code."""
    if not diagnostics:
        return 0
    write_error(header)
    for item in sorted(diagnostics, key=lambda entry: (entry["path"], entry["line"], entry["code"], entry["message"])):
        write_error(format_diagnostic(item))
    return 1


def report_violations(header: str, violations: Sequence[str]) -> int:
    """Print string violations and return a command exit code."""
    if not violations:
        return 0
    write_error(header)
    for violation in sorted(violations):
        write_error(f"- {violation}")
    return 1
