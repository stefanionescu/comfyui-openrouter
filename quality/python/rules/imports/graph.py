"""Validate runtime import graph cycles."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING
from dataclasses import dataclass
from collections import defaultdict
from quality.lib.diagnostics import diagnostic
from quality.config.python.rules import RUNTIME_ROOT_PACKAGE
from quality.python.rules.imports.cycles import CycleTraversal

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


@dataclass(frozen=True, slots=True)
class ModuleRecord:
    """One internal module and its package resolution context.

    Attributes:
        name: Dotted module identity.
        source: Borrowed read-only parsed source.
        is_package_initializer: Whether this file initializes a package.

    """

    name: str
    source: PythonSource
    is_package_initializer: bool

    @property
    def package(self) -> str:
        """The package used to resolve relative imports."""
        if self.is_package_initializer:
            return self.name
        return self.name.rpartition(".")[0]


class RuntimeImportVisitor(ast.NodeVisitor):
    """Collect imports outside bare TYPE_CHECKING bodies."""

    def __init__(self) -> None:
        """Create an empty runtime import collection."""
        self.imports: list[ast.Import | ast.ImportFrom] = []

    def visit_If(self, node: ast.If) -> None:
        """Skip bare TYPE_CHECKING bodies and visit other branches."""
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            for statement in node.orelse:
                self.visit(statement)
            return
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Collect one import statement."""
        self.imports.append(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Collect one from-import statement."""
        self.imports.append(node)


def collect_import_graph_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return cycle diagnostics for the cached runtime import graph."""
    records = collect_modules(sources, RUNTIME_ROOT_PACKAGE)
    graph = parse_import_edges(records)
    diagnostics: list[Diagnostic] = []
    for component in cycle_components(graph):
        first_module = min(component)
        source = records[first_module].source
        diagnostics.append(
            diagnostic(
                source.relative_path,
                1,
                "import.cycle",
                format_cycle_component(component, graph),
            ),
        )
    for module in sorted(module for module, targets in graph.items() if module in targets):
        source = records[module].source
        diagnostics.append(
            diagnostic(
                source.relative_path,
                1,
                "import.self-cycle",
                f"{module} imports itself",
            ),
        )
    return diagnostics


def collect_modules(sources: Sequence[PythonSource], root_package: str) -> dict[str, ModuleRecord]:
    """Map runtime module names to source and package metadata."""
    records: dict[str, ModuleRecord] = {}
    prefix = f"{root_package}/"
    for source in sources:
        if source.relative_path != f"{root_package}.py" and not source.relative_path.startswith(prefix):
            continue
        relative = Path(source.relative_path)
        is_initializer = relative.name == "__init__.py"
        if source.relative_path == f"{root_package}.py":
            name = root_package
        else:
            module_path = relative.relative_to(root_package).with_suffix("")
            parts = list(module_path.parts)
            if is_initializer:
                parts.pop()
            name = root_package if not parts else f"{root_package}." + ".".join(parts)
        records[name] = ModuleRecord(name=name, source=source, is_package_initializer=is_initializer)
    return records


def parse_import_edges(records: dict[str, ModuleRecord]) -> dict[str, set[str]]:
    """Parse direct internal import edges from module ASTs."""
    edges: dict[str, set[str]] = defaultdict(set)
    known_modules = set(records)
    for module, record in records.items():
        edges.setdefault(module, set())
        tree = record.source.tree
        if tree is None:
            continue
        for node in runtime_import_nodes(tree):
            if isinstance(node, ast.Import):
                edges[module].update(import_statement_targets(node, known_modules))
            else:
                edges[module].update(import_from_targets(record, node, known_modules))
    return dict(edges)


def runtime_import_nodes(tree: ast.Module) -> list[ast.Import | ast.ImportFrom]:
    """Return import nodes outside bare TYPE_CHECKING bodies."""
    visitor = RuntimeImportVisitor()
    visitor.visit(tree)
    return visitor.imports


def import_statement_targets(node: ast.Import, known_modules: set[str]) -> set[str]:
    """Return internal targets for an import statement."""
    targets: set[str] = set()
    for alias in node.names:
        selected = nearest_known_module(alias.name, known_modules)
        if selected is not None:
            targets.add(selected)
    return targets


def import_from_targets(
    record: ModuleRecord,
    node: ast.ImportFrom,
    known_modules: set[str],
) -> set[str]:
    """Return internal base and known-submodule targets for a from-import."""
    target = absolute_import_from_target(record, node)
    targets: set[str] = set()
    selected = nearest_known_module(target, known_modules)
    if selected is not None and selected != record.name:
        targets.add(selected)
    for alias in node.names:
        if alias.name == "*":
            continue
        submodule = f"{target}.{alias.name}" if target else alias.name
        if submodule in known_modules:
            targets.add(submodule)
    return targets


def absolute_import_from_target(record: ModuleRecord, node: ast.ImportFrom) -> str:
    """Return the absolute target for one from-import."""
    if node.level == 0:
        return node.module or ""
    relative_name = f"{'.' * node.level}{node.module or ''}"
    try:
        return importlib.util.resolve_name(relative_name, record.package)
    except ImportError:
        return ""


def nearest_known_module(module_name: str, known_modules: set[str]) -> str | None:
    """Resolve a module name to the nearest internal module or package."""
    candidate = module_name
    while candidate:
        if candidate in known_modules:
            return candidate
        if "." not in candidate:
            return None
        candidate = candidate.rsplit(".", 1)[0]
    return None


def cycle_components(graph: dict[str, set[str]]) -> list[list[str]]:
    """Return multi-module strongly connected components."""
    modules = set(graph)
    adjacency = {module: {target for target in graph[module] if target in modules} for module in modules}
    components = CycleTraversal(adjacency).components_for(modules)
    return [component for component in components if len(component) > 1]


def format_cycle_component(component: list[str], edges: dict[str, set[str]]) -> str:
    """Render one cycle component."""
    ordered = sorted(component)
    relationships: list[str] = []
    for module in ordered:
        neighbors = sorted(target for target in edges.get(module, set()) if target in component)
        if neighbors:
            relationships.append(f"{module} -> {', '.join(neighbors)}")
    return f"cycle across {', '.join(ordered)}" if not relationships else "; ".join(relationships)
