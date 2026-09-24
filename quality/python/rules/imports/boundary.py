"""Validate Python import boundaries."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.source import dotted_name
from quality.lib.diagnostics import diagnostic
from quality.config.repository.paths import PYTHON_RUNTIME_DIRS
from quality.config.python.rules import FORBIDDEN_RUNTIME_IMPORT_ROOTS

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic
    from quality.python.policy import ImportPolicy, PackagePolicy


def collect_import_boundary_violations(
    source: PythonSource,
    config: ImportPolicy,
    package_policy: PackagePolicy,
) -> list[Diagnostic]:
    """Return absolute-import, package-owner, dynamic-import, and path-mutation violations."""
    tree = source.tree
    if tree is None:
        return []
    relative_path = source.relative_path
    bindings = import_bindings(tree)
    violations: list[Diagnostic] = []

    for node in ast.walk(tree):
        violations.extend(violations_for_node(relative_path, node, config, package_policy, bindings))

    if any(
        relative_path == runtime_dir or relative_path.startswith(f"{runtime_dir.rstrip('/')}/")
        for runtime_dir in PYTHON_RUNTIME_DIRS
    ):
        for line, module_name in runtime_imported_module_names(tree):
            root_name = module_name.split(".", 1)[0]
            if root_name not in FORBIDDEN_RUNTIME_IMPORT_ROOTS:
                continue
            violations.append(
                diagnostic(relative_path, line, "import.runtime-boundary", f"runtime imports {root_name}"),
            )

    return violations


def violations_for_node(
    relative_path: str,
    node: ast.AST,
    config: ImportPolicy,
    package_policy: PackagePolicy,
    bindings: dict[str, str],
) -> list[Diagnostic]:
    """Return import-boundary diagnostics for one AST node."""
    violations: list[Diagnostic] = []
    if isinstance(node, ast.ImportFrom):
        violations = import_from_violations(relative_path, node, config, package_policy)
    elif isinstance(node, ast.Call):
        violations = call_violations(relative_path, node, config, bindings)
    elif isinstance(node, ast.Assign | ast.AnnAssign | ast.AugAssign | ast.Delete):
        violations = mutation_violations(relative_path, node, bindings)
    return violations


def import_from_violations(
    relative_path: str,
    node: ast.ImportFrom,
    config: ImportPolicy,
    package_policy: PackagePolicy,
) -> list[Diagnostic]:
    """Return import-boundary diagnostics for one from-import."""
    violations: list[Diagnostic] = []
    if node.level and not config["are_relative_imports_allowed"]:
        violations.append(diagnostic(relative_path, node.lineno, "import.relative", "use absolute first-party imports"))
    module_name = node.module or ""
    root_name = module_name.split(".", 1)[0]
    package_roots = tuple(config["package_roots"])
    if module_name == "__future__" or not module_name or root_name not in package_roots:
        return violations
    allowed_pairs = {(pair[0], pair[1]) for pair in package_policy["allow_package_api_imports"]}
    violations.extend(
        diagnostic(relative_path, node.lineno, "import.package-barrel", f"import concrete owner for {alias.name}")
        for alias in node.names
        if "." not in module_name and alias.name != "*" and (module_name, alias.name) not in allowed_pairs
    )
    return violations


def call_violations(
    relative_path: str,
    node: ast.Call,
    config: ImportPolicy,
    bindings: dict[str, str],
) -> list[Diagnostic]:
    """Return import-boundary diagnostics for one call."""
    violations: list[Diagnostic] = []
    call_name = resolved_name(node.func, bindings)
    if call_name in {"importlib.import_module", "builtins.__import__"} and config["are_dynamic_imports_banned"]:
        violations.append(diagnostic(relative_path, node.lineno, "import.dynamic", "dynamic imports are banned"))
    if isinstance(node.func, ast.Attribute) and resolved_name(node.func.value, bindings) == "sys.path":
        violations.append(diagnostic(relative_path, node.lineno, "import.sys-path", "sys.path mutation is banned"))
    return violations


def mutation_violations(
    relative_path: str,
    node: ast.Assign | ast.AnnAssign | ast.AugAssign | ast.Delete,
    bindings: dict[str, str],
) -> list[Diagnostic]:
    """Return sys.path diagnostics for one mutation statement."""
    targets = node.targets if isinstance(node, ast.Assign | ast.Delete) else [node.target]
    if any(is_sys_path_target(target, bindings) for target in targets):
        return [diagnostic(relative_path, node.lineno, "import.sys-path", "sys.path mutation is banned")]
    return []


def is_sys_path_target(node: ast.expr, bindings: dict[str, str]) -> bool:
    """Return whether an assignment or deletion target mutates sys.path."""
    if resolved_name(node, bindings) == "sys.path" or (
        isinstance(node, ast.Subscript) and resolved_name(node.value, bindings) == "sys.path"
    ):
        return True
    if isinstance(node, ast.Starred):
        return is_sys_path_target(node.value, bindings)
    if isinstance(node, ast.List | ast.Tuple):
        return any(is_sys_path_target(element, bindings) for element in node.elts)
    return False


def import_bindings(tree: ast.Module) -> dict[str, str]:
    """Return local import names mapped to their absolute imported identities."""
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".", 1)[0]
                bindings[local_name] = alias.name if alias.asname else alias.name.split(".", 1)[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    continue
                bindings[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return bindings


def resolved_name(node: ast.AST | None, bindings: dict[str, str]) -> str:
    """Return a dotted expression name after applying import aliases."""
    name = dotted_name(node)
    if not name:
        return ""
    root, separator, tail = name.partition(".")
    if root == "__import__":
        return "builtins.__import__"
    bound_root = bindings.get(root, root)
    return f"{bound_root}.{tail}" if separator else bound_root


def runtime_imported_module_names(tree: ast.Module) -> list[tuple[int, str]]:
    """Return imported module names outside static type-checking blocks."""
    names: list[tuple[int, str]] = []

    def visit(node: ast.AST) -> None:
        """Collect runtime imports under one AST node."""
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            return
        if isinstance(node, ast.Import):
            names.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append((node.lineno, node.module or ""))
        for child in ast.iter_child_nodes(node):
            visit(child)

    for statement in tree.body:
        visit(statement)
    return names


def collect_import_boundary_diagnostics(
    sources: Sequence[PythonSource],
    config: ImportPolicy,
    package_config: PackagePolicy,
) -> list[Diagnostic]:
    """Return import and package boundary diagnostics."""
    errors: list[Diagnostic] = []
    for source in sources:
        errors.extend(collect_import_boundary_violations(source, config, package_config))
    return errors
