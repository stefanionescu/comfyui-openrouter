"""Reject lazy module export hooks in runtime Python modules."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.python.rules import FORBIDDEN_EXPORT_HOOKS

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def collect_deferred_violations(source: PythonSource) -> list[Diagnostic]:
    """Return deferred import violations for one file."""
    tree = source.tree
    if tree is None:
        return []

    return [
        diagnostic(
            source.relative_path,
            node.lineno,
            "import.lazy-export",
            f"module-level {node.name} hook is forbidden",
        )
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name in FORBIDDEN_EXPORT_HOOKS
    ]


def collect_deferred_import_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return forbidden lazy export hooks."""
    violations: list[Diagnostic] = []
    for source in sources:
        violations.extend(collect_deferred_violations(source))
    return violations
