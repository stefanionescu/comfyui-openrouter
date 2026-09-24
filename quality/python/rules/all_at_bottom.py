"""Enforce that __all__ appears at the bottom of each module.

Flags any non-__all__ statements (function defs, class defs, imports,
assignments) that appear after the first __all__ assignment, except for
``if __name__ == "__main__":`` guards.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def _is_all_statement(node: ast.stmt) -> bool:
    """Return True if *node* is an assignment or mutation targeting ``__all__``."""
    is_all_statement = False
    if isinstance(node, ast.Assign):
        is_all_statement = any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    elif isinstance(node, ast.AugAssign | ast.AnnAssign):
        is_all_statement = isinstance(node.target, ast.Name) and node.target.id == "__all__"
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        function = node.value.func
        if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
            is_all_statement = function.value.id == "__all__"
    return is_all_statement


def _is_name_main_guard(node: ast.stmt) -> bool:
    """Return True if *node* is ``if __name__ == "__main__":``."""
    if not isinstance(node, ast.If):
        return False
    test = node.test
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
        left_operand, right_operand = test.left, test.comparators[0]
        operand_pairs = [(left_operand, right_operand), (right_operand, left_operand)]
        for name_operand, value_operand in operand_pairs:
            if (
                isinstance(name_operand, ast.Name)
                and name_operand.id == "__name__"
                and isinstance(value_operand, ast.Constant)
                and value_operand.value == "__main__"
            ):
                return True
    return False


def _named_node_label(node: ast.stmt) -> str | None:
    """Return a label for a named definition."""
    if isinstance(node, ast.FunctionDef):
        return f"function `{node.name}`"
    if isinstance(node, ast.AsyncFunctionDef):
        return f"async function `{node.name}`"
    if isinstance(node, ast.ClassDef):
        return f"class `{node.name}`"
    return None


def _describe_node(node: ast.stmt) -> str:
    """Return a human-readable label for a top-level statement."""
    named_label = _named_node_label(node)
    if named_label is not None:
        return named_label
    if isinstance(node, ast.Assign):
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        return f"assignment `{', '.join(names)}`" if names else "assignment"
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return f"assignment `{node.target.id}`"
    statement_labels: dict[type[ast.stmt], str] = {
        ast.Import: "import",
        ast.ImportFrom: "import",
        ast.If: "if statement",
        ast.For: "loop",
        ast.While: "loop",
        ast.With: "with statement",
        ast.Try: "try statement",
    }
    return statement_labels.get(type(node), type(node).__name__)


def collect_all_source_violations(source: PythonSource) -> list[Diagnostic]:
    """Return __all__ placement violations for one file."""
    tree = source.tree
    if tree is None:
        return []

    first_all_index: int | None = None
    first_all_line: int = 0
    for index, node in enumerate(tree.body):
        if _is_all_statement(node):
            first_all_index = index
            first_all_line = node.lineno
            break

    if first_all_index is None:
        return []

    violations: list[Diagnostic] = []
    for node in tree.body[first_all_index + 1 :]:
        if _is_all_statement(node):
            continue
        if _is_name_main_guard(node):
            continue
        label = _describe_node(node)
        violations.append(
            diagnostic(
                source.relative_path,
                node.lineno,
                "python.all-at-bottom",
                f"{label} is below __all__ on line {first_all_line}",
            ),
        )

    return violations


def collect_all_placement_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return statements placed below __all__ in cached modules."""
    violations: list[Diagnostic] = []
    for source in sources:
        violations.extend(collect_all_source_violations(source))
    return violations
