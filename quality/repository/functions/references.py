"""Resolve the classes and imports each repository Python module declares."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING
from dataclasses import dataclass
from types import MappingProxyType
from quality.lib.source import dotted_name

if TYPE_CHECKING:
    from quality.lib.source import PythonSource
    from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ModuleNames:
    """Class and import identities declared by one Python module.

    Attributes:
        name: Dotted module identity.
        source: Borrowed read-only parsed source.
        classes: Read-only map of class names.
        bindings: Read-only map of resolved imports.

    """

    name: str
    source: PythonSource
    classes: Mapping[str, str]
    bindings: Mapping[str, str]


def index_modules(sources: Sequence[PythonSource]) -> dict[str, ModuleNames]:
    """Index each module's classes and resolved imports by its module name."""
    modules = {
        module_name(source.relative_path): collect_module_names(source) for source in sources if source.tree is not None
    }
    known_modules = set(modules)
    return {
        module: ModuleNames(
            name=record.name,
            source=record.source,
            classes=record.classes,
            bindings=MappingProxyType(import_bindings(record, known_modules)),
        )
        for module, record in modules.items()
    }


def module_name(relative_path: str) -> str:
    """Return the importable module name for a repository Python path."""
    path = Path(relative_path).with_suffix("")
    parts = list(path.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def collect_module_names(source: PythonSource) -> ModuleNames:
    """Collect the classes declared in one module."""
    module = module_name(source.relative_path)
    classes: dict[str, str] = {}
    scope: list[str] = []

    class DefinitionVisitor(ast.NodeVisitor):
        """Collect qualified class definitions."""

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Collect one class and visit its body."""
            qualified = ".".join((*scope, node.name))
            classes[qualified] = f"{module}:{qualified}"
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit one synchronous function scope."""
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Visit one asynchronous function scope."""
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

    tree = source.tree
    if tree is not None:
        DefinitionVisitor().visit(tree)
    return ModuleNames(name=module, source=source, classes=MappingProxyType(classes), bindings=MappingProxyType({}))


def import_bindings(record: ModuleNames, known_modules: set[str]) -> dict[str, str]:
    """Return local import names mapped to absolute identities."""
    tree = record.source.tree
    if tree is None:
        return {}
    bindings: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            bindings.update(
                {
                    alias.asname or alias.name.split(".", 1)[0]: alias.name
                    if alias.asname
                    else alias.name.split(".", 1)[0]
                    for alias in node.names
                }
            )
        elif isinstance(node, ast.ImportFrom):
            bindings.update(from_import_bindings(record, node, known_modules))
    return bindings


def from_import_bindings(
    record: ModuleNames,
    node: ast.ImportFrom,
    known_modules: set[str],
) -> dict[str, str]:
    """Return bindings declared by one from-import statement."""
    base = absolute_from_target(
        record.name,
        node,
        is_initializer=record.source.path.name == "__init__.py",
    )
    bindings: dict[str, str] = {}
    for alias in node.names:
        if alias.name == "*":
            continue
        identity = f"{base}.{alias.name}" if base else alias.name
        if alias.name in known_modules and not base:
            identity = alias.name
        bindings[alias.asname or alias.name] = identity
    return bindings


def absolute_from_target(module: str, node: ast.ImportFrom, *, is_initializer: bool) -> str:
    """Return the absolute target for one from-import."""
    if node.level == 0:
        return node.module or ""
    package = module if is_initializer else module.rpartition(".")[0]
    try:
        return importlib.util.resolve_name(f"{'.' * node.level}{node.module or ''}", package)
    except ImportError:
        return ""


def resolved_dotted_name(node: ast.AST, record: ModuleNames) -> str:
    """Return a dotted expression identity after applying import bindings."""
    name = dotted_name(node)
    if not name:
        return ""
    root, separator, tail = name.partition(".")
    bound_root = record.bindings.get(root)
    if bound_root is None and root in record.classes:
        bound_root = f"{record.name}.{root}"
    if bound_root is None:
        bound_root = root
    return f"{bound_root}.{tail}" if separator else bound_root
