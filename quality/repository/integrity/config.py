"""Validate declarative configuration modules and their import boundary."""

from __future__ import annotations

import os
import ast
import importlib.util
from pathlib import Path
from quality.lib.files import read_utf8
from quality.lib.output import write_error
from quality.config.repository.paths import CONFIG_SOURCE_DIRS, QUALITY_EXCLUDED_DIRS
from quality.config.repository.integrity import CONFIG_IMPORT_ROOTS, DECLARATIVE_EXCLUSIONS

CONTROL_FLOW_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.Match,
)
EXECUTABLE_NODES = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.Call,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.AugAssign,
    ast.Delete,
)
SAFE_BINARY_OPERATORS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)


def collect_config_violations(root: Path) -> list[str]:
    """Return diagnostics for every declared configuration source root."""
    violations: list[str] = []
    for config_dir in CONFIG_SOURCE_DIRS:
        base = root / config_dir
        if not base.is_dir():
            violations.append(f"{config_dir} configured source root does not exist")
            continue
        for path in config_paths(base):
            relative_path = path.relative_to(root).as_posix()
            if relative_path.startswith(DECLARATIVE_EXCLUSIONS):
                continue
            violations.extend(check_config_file(root, path))
    return violations


def config_paths(base: Path) -> list[Path]:
    """Return Python configuration files without entering excluded directories."""
    paths: list[Path] = []
    for directory, names, files in os.walk(base, topdown=True):
        names[:] = sorted(name for name in names if name not in QUALITY_EXCLUDED_DIRS)
        paths.extend(Path(directory) / name for name in sorted(files) if name.endswith(".py"))
    return paths


def check_config_file(root: Path, path: Path) -> list[str]:
    """Return declarative-value and safe-import diagnostics for one module."""
    relative_path = path.relative_to(root).as_posix()
    try:
        tree = ast.parse(read_utf8(path), filename=relative_path)
    except SyntaxError as exception:
        return [f"{relative_path}:{exception.lineno or 1} invalid Python syntax"]

    violations: list[str] = []
    known_constants: set[str] = set()
    for node in tree.body:
        violations.extend(check_top_level_node(relative_path, node, known_constants))
        known_constants.update(assigned_constant_names(node))
        if isinstance(node, ast.ImportFrom):
            known_constants.update(alias.asname or alias.name for alias in node.names if alias.name.isupper())
    for node in ast.walk(tree):
        if isinstance(node, CONTROL_FLOW_NODES):
            violations.append(f"{relative_path}:{node.lineno} config contains control flow")
        elif isinstance(node, EXECUTABLE_NODES):
            violations.append(f"{relative_path}:{node.lineno} config contains executable syntax")
    return sorted(set(violations))


def check_top_level_node(relative_path: str, node: ast.stmt, known_constants: set[str]) -> list[str]:
    """Return diagnostics for one top-level configuration statement."""
    violations: list[str] = []
    if isinstance(node, ast.Import | ast.ImportFrom):
        modules = imported_modules(relative_path, node)
        violations.extend(
            f"{relative_path}:{node.lineno} config import is outside the safe boundary: {module}"
            for module in modules
            if not any(module == root or module.startswith(f"{root}.") for root in CONFIG_IMPORT_ROOTS)
        )
    elif isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return violations
        violations.append(f"{relative_path}:{node.lineno} config contains non-docstring expression")
    elif isinstance(node, ast.Assign):
        violations.extend(check_assignment(relative_path, node.lineno, node.targets, node.value, known_constants))
    elif isinstance(node, ast.AnnAssign):
        violations.extend(check_assignment(relative_path, node.lineno, [node.target], node.value, known_constants))
    else:
        violations.append(f"{relative_path}:{node.lineno} config contains non-assignment statement")
    return violations


def imported_modules(relative_path: str, node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return absolute module names imported by one statement."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level == 0:
        return [node.module or ""]
    package = ".".join(Path(relative_path).parent.parts)
    relative_name = f"{'.' * node.level}{node.module or ''}"
    try:
        return [importlib.util.resolve_name(relative_name, package)]
    except ImportError:
        return [f"<invalid relative import {relative_name}>"]


def check_assignment(
    relative_path: str,
    line: int,
    targets: list[ast.expr],
    value: ast.expr | None,
    known_constants: set[str],
) -> list[str]:
    """Require named assignments composed from immutable declarative expressions."""
    violations: list[str] = []
    if not all(isinstance(target, ast.Name) for target in targets):
        violations.append(f"{relative_path}:{line} config assignment mutates an object")
    if value is None or not is_config_value(value, known_constants):
        violations.append(f"{relative_path}:{line} config assignment must use declarative values")
    return violations


def assigned_constant_names(node: ast.stmt) -> set[str]:
    """Return uppercase names established by one assignment."""
    targets: list[ast.expr] = []
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
    return {target.id for target in targets if isinstance(target, ast.Name) and target.id.isupper()}


def is_config_value(node: ast.AST, known_constants: set[str]) -> bool:
    """Return whether an expression is deterministic declarative configuration."""
    is_valid = False
    if isinstance(node, ast.Constant):
        is_valid = True
    elif isinstance(node, ast.Name):
        is_valid = node.id in known_constants
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd | ast.USub):
        is_valid = is_config_value(node.operand, known_constants)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, SAFE_BINARY_OPERATORS):
        is_valid = is_config_value(node.left, known_constants) and is_config_value(node.right, known_constants)
    elif isinstance(node, ast.Starred):
        is_valid = is_config_value(node.value, known_constants)
    elif isinstance(node, ast.Tuple | ast.List | ast.Set):
        is_valid = all(is_config_value(element, known_constants) for element in node.elts)
    elif isinstance(node, ast.Dict):
        is_valid = all(
            (key is None or is_config_value(key, known_constants)) and is_config_value(value, known_constants)
            for key, value in zip(node.keys, node.values, strict=True)
        )
    return is_valid


def main() -> int:
    """Run declarative configuration policy."""
    violations = collect_config_violations(Path.cwd())
    if not violations:
        return 0
    write_error("Configuration integrity violations:")
    for violation in violations:
        write_error(f"- {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
