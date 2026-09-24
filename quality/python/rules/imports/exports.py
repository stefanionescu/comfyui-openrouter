"""Validate package export policy."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic
    from quality.python.policy import PackagePolicy


def collect_package_export_violations(
    source: PythonSource,
    config: PackagePolicy,
) -> list[Diagnostic]:
    """Return package export, duplicate __all__, alias constant, and export-only module violations."""
    tree = source.tree
    if tree is None:
        return []
    relative_path = source.relative_path

    violations: list[Diagnostic] = []
    names = all_exported_names(tree)
    name_values = [name for _, name in names]
    duplicate_names = sorted({name for name in name_values if name_values.count(name) > 1})
    violations.extend(
        diagnostic(relative_path, 1, "exports.duplicate", f"duplicate export {duplicate_name}")
        for duplicate_name in duplicate_names
    )

    max_exports = config["max_package_exports"]
    if relative_path.endswith("__init__.py") and len(name_values) > max_exports:
        violations.append(diagnostic(relative_path, 1, "exports.package-size", f"package exports exceed {max_exports}"))

    if is_export_only_module(relative_path, tree, config):
        violations.append(diagnostic(relative_path, 1, "exports.only", "module only re-exports imported names"))

    if config["are_constant_aliases_banned"]:
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
                is_name_alias = isinstance(node.value, ast.Name)
                is_attribute_alias = isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name)
                if target_name.isupper() and (is_name_alias or is_attribute_alias):
                    violations.append(
                        diagnostic(
                            relative_path,
                            node.lineno,
                            "exports.alias-constant",
                            f"{target_name} aliases another name",
                        ),
                    )
    return violations


def collect_package_export_diagnostics(
    sources: Sequence[PythonSource],
    config: PackagePolicy,
) -> list[Diagnostic]:
    """Return package export diagnostics for cached modules."""
    errors: list[Diagnostic] = []
    for source in sources:
        errors.extend(collect_package_export_violations(source, config))
    return errors


def all_exported_names(tree: ast.Module) -> list[tuple[int, str]]:
    """Return names declared in __all__."""
    names: list[tuple[int, str]] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            names.extend((node.lineno, value) for value in literal_string_sequence(node.value))
    return names


def is_export_only_module(relative_path: str, tree: ast.Module, config: PackagePolicy) -> bool:
    """Return true when a module only re-exports imported names."""
    allow = set(config["allow_export_only_files"])
    if Path(relative_path).name in allow:
        return False
    real_statements = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        )
    ]
    if not real_statements:
        return False
    return all(isinstance(node, ast.Import | ast.ImportFrom) or is_all_assignment(node) for node in real_statements)


def is_all_assignment(node: ast.stmt) -> bool:
    """Return whether a statement assigns the package export list."""
    if isinstance(node, ast.Assign):
        return any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    return isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__"


def literal_string_sequence(node: ast.AST) -> list[str]:
    """Return literal strings from a list or tuple node."""
    if not isinstance(node, ast.List | ast.Tuple):
        return []
    return [
        element.value for element in node.elts if isinstance(element, ast.Constant) and isinstance(element.value, str)
    ]
