"""Enforce that project code adds no logging.

rules/GENERAL.md forbids logging at every severity: no loggers, no logging wrappers,
no logging configuration. Results are returned and failures are raised through an
operation's own contract instead.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def _imports_logging(node: ast.stmt) -> bool:
    """Return whether one statement imports the logging module."""
    if isinstance(node, ast.Import):
        return any(alias.name == "logging" or alias.name.startswith("logging.") for alias in node.names)
    return isinstance(node, ast.ImportFrom) and not node.level and (node.module or "").split(".")[0] == "logging"


def collect_logging_source_violations(source: PythonSource) -> list[Diagnostic]:
    """Return every logging import or call in one file."""
    tree = source.tree
    if tree is None:
        return []
    violations: list[Diagnostic] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom) and _imports_logging(node):
            violations.append(
                diagnostic(source.relative_path, node.lineno, "python.logging", "project code adds no logging"),
            )
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "logging":
            violations.append(
                diagnostic(
                    source.relative_path,
                    node.lineno,
                    "python.logging",
                    f"project code adds no logging: logging.{node.attr}",
                ),
            )
    return violations


def collect_logging_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return logging use across cached modules."""
    violations: list[Diagnostic] = []
    for source in sources:
        violations.extend(collect_logging_source_violations(source))
    return violations
