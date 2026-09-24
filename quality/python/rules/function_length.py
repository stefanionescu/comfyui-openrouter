"""Enforce maximum function length for Python modules.

Checks functions and methods and fails when any function exceeds the limit
(default 60 code lines), excluding blank lines, comment-only lines, and docstrings.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.python.limits import MAX_FUNCTION_LINES

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


class FunctionCollector(ast.NodeVisitor):
    """Collect function definitions with qualified names."""

    def __init__(self) -> None:
        """Create an empty function collector."""
        self._scope: list[str] = []
        self.functions: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class scope while visiting nested functions."""
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Collect a synchronous function."""
        self._collect_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Collect an asynchronous function."""
        self._collect_function(node)

    def _collect_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Append one function and visit nested functions."""
        qualified = ".".join((*self._scope, node.name)) if self._scope else node.name
        self.functions.append((qualified, node))
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()


def _count_function_lines(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    raw_lines: Sequence[str],
    comments: frozenset[int],
    docstrings: frozenset[int],
) -> int:
    """Count code lines for one function node."""
    count = 0
    for line_no in range(node.lineno, (node.end_lineno or node.lineno) + 1):
        if line_no in comments or line_no in docstrings:
            continue
        line = raw_lines[line_no - 1] if line_no - 1 < len(raw_lines) else ""
        if not line.strip():
            continue
        count += 1
    return count


def collect_function_violations(source: PythonSource, limit: int) -> list[Diagnostic]:
    """Return function length violations for one file."""
    tree = source.tree
    if tree is None:
        return []

    collector = FunctionCollector()
    collector.visit(tree)

    violations: list[Diagnostic] = []
    for qualified, node in collector.functions:
        size = _count_function_lines(node, source.lines, source.comment_lines, source.docstring_lines)
        if size > limit:
            violations.append(
                diagnostic(
                    source.relative_path,
                    node.lineno,
                    "python.function-length",
                    f"{qualified} has {size} code lines, limit {limit}",
                ),
            )
    return violations


def collect_function_length_violations(
    sources: Sequence[PythonSource],
    limit: int = MAX_FUNCTION_LINES,
) -> list[Diagnostic]:
    """Return functions that exceed the code-line limit."""
    violations: list[Diagnostic] = []
    for source in sources:
        violations.extend(collect_function_violations(source, limit))
    return violations
