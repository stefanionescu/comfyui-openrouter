"""Check the functions of the runtime and build scripts: private first, never exported, and private when local."""

from __future__ import annotations

import re
import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import NamedDiagnostic
    from quality.repository.functions.policy import PythonFunctionPolicy

# One leading underscore marks a private name; a dunder is neither private nor public.
PRIVATE = re.compile(r"^_(?!_)")


def _list_order_violations(source: PythonSource, body: Sequence[ast.stmt], owner: str) -> list[NamedDiagnostic]:
    """Report each private function that follows a public one in the same module or class body."""
    violations: list[NamedDiagnostic] = []
    first_public: str | None = None
    for node in body:
        if isinstance(node, ast.ClassDef):
            violations += _list_order_violations(source, node.body, f"{owner}{node.name}.")
            continue
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("__"):
            continue
        if not PRIVATE.match(node.name):
            first_public = first_public or node.name
        elif first_public is not None:
            violations.append(
                {
                    "path": source.relative_path,
                    "line": node.lineno,
                    "code": "python.private-order",
                    "name": f"{owner}{node.name}",
                    "message": f"private function follows public {first_public}; put private functions first",
                },
            )
    return violations


def _list_export_violations(source: PythonSource, tree: ast.Module) -> list[NamedDiagnostic]:
    """Report each private name listed in __all__."""
    violations: list[NamedDiagnostic] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        names = [item.value for item in ast.walk(node.value) if isinstance(item, ast.Constant)] if node.value else []
        violations.extend(
            {
                "path": source.relative_path,
                "line": node.lineno,
                "code": "python.private-export",
                "name": name,
                "message": "__all__ lists a private name",
            }
            for name in names
            if isinstance(name, str) and PRIVATE.match(name)
        )
    return violations


def _list_local_violations(
    source: PythonSource,
    tree: ast.Module,
    other_texts: Sequence[str],
    exempt: set[str],
) -> list[NamedDiagnostic]:
    """Report each public module-level function no other module names; it belongs to its module alone."""
    violations: list[NamedDiagnostic] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
            continue
        if node.name == "main" or node.name in exempt:
            continue
        pattern = re.compile(rf"\b{re.escape(node.name)}\b")
        if not any(pattern.search(text) for text in other_texts):
            violations.append(
                {
                    "path": source.relative_path,
                    "line": node.lineno,
                    "code": "python.module-only-public",
                    "name": node.name,
                    "message": "only this module uses this function; make it private",
                },
            )
    return violations


def list_name_violations(
    sources: Sequence[PythonSource],
    policy: PythonFunctionPolicy,
    selected_paths: set[str],
) -> list[NamedDiagnostic]:
    """Check the order, exports, and privacy of functions in every governed module."""
    violations: list[NamedDiagnostic] = []
    for source in sources:
        tree = source.tree
        path = source.relative_path
        is_governed = any(path == prefix or path.startswith(prefix) for prefix in policy["named_paths"])
        if tree is None or path not in selected_paths or not is_governed:
            continue
        other_texts = [other.text for other in sources if other.relative_path != source.relative_path]
        exempt = {
            name for rule in policy["allowlist"] if rule["path"] == source.relative_path for name in rule["names"]
        }
        violations += _list_order_violations(source, tree.body, "")
        violations += _list_export_violations(source, tree)
        violations += _list_local_violations(source, tree, other_texts, exempt)
    return violations


__all__ = ["list_name_violations"]
