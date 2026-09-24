"""Enforce maximum code-line limits per runtime file.

Python files must not exceed a configurable limit of code lines (default 300).

Blank lines, comment-only lines, and docstring-only lines are excluded from
the count. __init__.py barrel-export files (only imports and __all__) are exempt.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.python.limits import MAX_FILE_LINES

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def _is_barrel_init(source: PythonSource) -> bool:
    """Check if __init__.py is a barrel-export file (only imports, __all__, docstrings, pass)."""
    if source.path.name != "__init__.py" or source.tree is None:
        return False
    for node in ast.iter_child_nodes(source.tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Assign):
            targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if targets == ["__all__"]:
                continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.Pass):
            continue
        return False
    return True


def _count_code_lines(source: PythonSource) -> int:
    """Count non-blank, non-comment, non-docstring lines."""
    count = 0
    for line_number, line in enumerate(source.lines, start=1):
        if not line.strip():
            continue
        if line_number in source.comment_lines:
            continue
        if line_number in source.constant_string_lines:
            continue
        if line_number in source.docstring_lines:
            continue
        count += 1
    return count


def collect_module_length_violations(
    sources: Sequence[PythonSource],
    limit: int = MAX_FILE_LINES,
) -> list[Diagnostic]:
    """Return Python modules that exceed the code-line limit."""
    violations: list[Diagnostic] = []
    for source in sources:
        if _is_barrel_init(source):
            continue
        code_lines = _count_code_lines(source)
        if code_lines > limit:
            violations.append(
                diagnostic(
                    source.relative_path,
                    1,
                    "python.module-length",
                    f"{code_lines} code lines, limit {limit}",
                ),
            )
    return violations
