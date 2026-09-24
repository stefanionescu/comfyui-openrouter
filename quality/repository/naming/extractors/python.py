"""Python AST name extraction."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quality.repository.naming.types import NameCandidate


class PythonNameExtractor(ast.NodeVisitor):
    """Collect Python names by category."""

    def __init__(self, relative_path: str) -> None:
        """Create a name extractor for one Python file."""
        self.relative_path = relative_path
        self.class_depth = 0
        self.names: list[NameCandidate] = []

    def generic_visit(self, node: ast.AST) -> None:
        """Collect loop, comprehension, and expression bindings before traversing children."""
        if isinstance(node, ast.For | ast.AsyncFor | ast.comprehension | ast.NamedExpr):
            self.visit_target(node.target, node.target.lineno, None)
        elif isinstance(node, ast.With | ast.AsyncWith):
            for item in node.items:
                if item.optional_vars is not None:
                    self.visit_target(item.optional_vars, item.optional_vars.lineno, None)
        super().generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Collect class or exception names."""
        category = "exceptions" if node.name.endswith("Error") else "classes"
        self.names.append(
            {
                "path": self.relative_path,
                "line": node.lineno,
                "language": "python",
                "category": category,
                "name": node.name,
            },
        )
        self.class_depth += 1
        self.generic_visit(node)
        self.class_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Collect function names from synchronous definitions."""
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Collect function names from asynchronous definitions."""
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Add function and parameter names."""
        category = "methods" if self.class_depth else "functions"
        self.names.append(
            {
                "path": self.relative_path,
                "line": node.lineno,
                "language": "python",
                "category": category,
                "name": node.name,
            },
        )
        self._visit_arguments(node.args, node.lineno)
        self.generic_visit(node)

    def _visit_arguments(self, arguments: ast.arguments, line: int) -> None:
        """Add parameter names."""
        for argument in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs):
            if argument.arg not in {"self", "cls"}:
                self.names.append(
                    {
                        "path": self.relative_path,
                        "line": line,
                        "language": "python",
                        "category": "parameters",
                        "name": argument.arg,
                    },
                )
        if arguments.vararg:
            self.names.append(
                {
                    "path": self.relative_path,
                    "line": line,
                    "language": "python",
                    "category": "parameters",
                    "name": arguments.vararg.arg,
                },
            )
        if arguments.kwarg:
            self.names.append(
                {
                    "path": self.relative_path,
                    "line": line,
                    "language": "python",
                    "category": "parameters",
                    "name": arguments.kwarg.arg,
                },
            )

    def visit_Assign(self, node: ast.Assign) -> None:
        """Collect assignment target names."""
        for target in node.targets:
            self.visit_target(target, node.lineno, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Collect annotated assignment target names."""
        self.visit_target(node.target, node.lineno, node.annotation)
        self.generic_visit(node)

    def visit_target(self, target: ast.AST, line: int, value: ast.AST | None) -> None:
        """Add assignment target names."""
        if isinstance(target, ast.Name):
            category = (
                "type_aliases"
                if is_type_alias(target.id, value)
                else ("constants" if target.id.isupper() else "variables")
            )
            self.names.append(
                {
                    "path": self.relative_path,
                    "line": line,
                    "language": "python",
                    "category": category,
                    "name": target.id,
                },
            )
        elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            self.names.append(
                {
                    "path": self.relative_path,
                    "line": line,
                    "language": "python",
                    "category": "attributes",
                    "name": target.attr,
                },
            )
        elif isinstance(target, ast.Tuple | ast.List):
            for element in target.elts:
                self.visit_target(element, line, value)


def extract_python_names(relative_path: str, source_text: str) -> list[NameCandidate]:
    """Return Python naming candidates."""
    try:
        tree = ast.parse(source_text, filename=relative_path)
    except SyntaxError:
        return []
    extractor = PythonNameExtractor(relative_path)
    extractor.visit(tree)
    return extractor.names


def is_type_alias(name: str, value: ast.AST | None) -> bool:
    """Return whether an annotation or value represents a type alias."""
    normalized_name = name.lstrip("_")
    if isinstance(value, ast.Name) and value.id in {"TypeAlias", "type"}:
        return True
    if (
        isinstance(value, ast.Subscript)
        and isinstance(value.value, ast.Name)
        and value.value.id in {"type", "TypeAlias"}
    ):
        return True
    return (
        normalized_name[:1].isupper()
        and not normalized_name.isupper()
        and isinstance(value, ast.Name | ast.BinOp | ast.Subscript | ast.Attribute)
    )
