"""Reject lazy singleton patterns in runtime Python modules.

Flags classes with a Singleton suffix, functions named get_instance/reset_instance,
and module-level state variables that look like singleton holders.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.python.rules import SINGLETON_CLASS_SUFFIX, SINGLETON_FUNCTION_NAMES, SINGLETON_STATE_NAMES

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def _top_level_targets(node: ast.Assign | ast.AnnAssign) -> list[str]:
    """Return top-level assignment target names."""
    if isinstance(node, ast.AnnAssign):
        return [node.target.id] if isinstance(node.target, ast.Name) else []

    return [target.id for target in node.targets if isinstance(target, ast.Name)]


def _dict_contains_instance_key(value: ast.expr) -> bool:
    """Return whether a dictionary literal contains an instance key."""
    if not isinstance(value, ast.Dict):
        return False
    return any(isinstance(key, ast.Constant) and key.value == "instance" for key in value.keys)


def _is_lazy_singleton_state(node: ast.Assign | ast.AnnAssign) -> bool:
    """Return whether an assignment looks like lazy singleton state."""
    names = _top_level_targets(node)
    value = node.value
    return (
        bool(names)
        and value is not None
        and (
            (any(name in SINGLETON_STATE_NAMES for name in names) and _dict_contains_instance_key(value))
            or (
                isinstance(value, ast.Constant)
                and value.value is None
                and any(name.lower().endswith("_instance") for name in names)
            )
        )
    )


def collect_singleton_source_violations(source: PythonSource) -> list[Diagnostic]:
    """Return singleton-pattern violations for one file."""
    tree = source.tree
    if tree is None:
        return []

    violations: list[Diagnostic] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.endswith(SINGLETON_CLASS_SUFFIX):
            violations.append(
                diagnostic(
                    source.relative_path,
                    node.lineno,
                    "python.runtime-singleton",
                    f"class {node.name} uses singleton naming",
                ),
            )
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in SINGLETON_FUNCTION_NAMES:
            violations.append(
                diagnostic(
                    source.relative_path,
                    node.lineno,
                    "python.runtime-singleton",
                    f"function {node.name} suggests singleton lifecycle",
                ),
            )
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and _is_lazy_singleton_state(node):
            names = ", ".join(_top_level_targets(node))
            violations.append(
                diagnostic(
                    source.relative_path,
                    node.lineno,
                    "python.runtime-singleton",
                    f"lazy singleton module state assignment: {names}",
                ),
            )

    return violations


def collect_singleton_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return lazy singleton state and lifecycle hooks."""
    violations: list[Diagnostic] = []
    for source in sources:
        violations.extend(collect_singleton_source_violations(source))
    return violations
