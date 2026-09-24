"""Python function policy checks."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from dataclasses import dataclass
from quality.config.repository.functions import HOST_NODE_HOOKS, HOST_NODE_BASES
from quality.repository.functions.references import module_name, resolved_dotted_name
from quality.config.python.rules import (
    DOCSTRING_SOURCE_PREFIXES,
    PLACEHOLDER_DOCSTRING_PREFIXES,
)
from quality.repository.functions.semantics import (
    only_call,
    DUNDER_METHODS,
    PROTOCOL_BASES,
    DATACLASS_HOOKS,
    main_guard_calls,
    EXEMPT_DECORATORS,
    is_stub_statement,
    ast_visitor_classes,
    DATACLASS_DECORATORS,
    executable_statements,
    is_direct_call_through,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import NamedDiagnostic
    from quality.repository.functions.references import ModuleNames
    from quality.repository.functions.policy import PythonFunctionPolicy


@dataclass(frozen=True, slots=True)
class ClassContext:
    """Resolved class context for function exemptions.

    Attributes:
        qualified_name: Qualified class name.
        bases: Resolved base classes.
        decorators: Resolved decorators.
        is_ast_visitor: Whether the class implements an AST visitor.

    """

    qualified_name: str
    bases: frozenset[str]
    decorators: frozenset[str]
    is_ast_visitor: bool


@dataclass(frozen=True, slots=True)
class FunctionContext:
    """Resolved function context for diagnostics and exemptions.

    Attributes:
        relative_path: Repository-relative source path.
        name: Function name.
        qualified_name: Qualified function identity.
        decorators: Resolved decorators.
        class_context: Containing class context, when present.

    """

    relative_path: str
    name: str
    qualified_name: str
    decorators: frozenset[str]
    class_context: ClassContext | None


class FunctionVisitor(ast.NodeVisitor):
    """Collect Python function policy diagnostics."""

    def __init__(
        self,
        source: PythonSource,
        policy: PythonFunctionPolicy,
        record: ModuleNames,
        visitor_classes: set[str],
    ) -> None:
        """Create a visitor for one Python module."""
        self.source = source
        self.policy = policy
        self.record = record
        self.visitor_classes = visitor_classes
        self.class_stack: list[ClassContext] = []
        self.name_stack: list[str] = []
        self.violations: list[NamedDiagnostic] = []
        tree = source.tree
        self.has_main_call = tree is not None and main_guard_calls(tree, "main")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track resolved class context while visiting methods."""
        qualified_name = ".".join((*self.name_stack, node.name))
        context = ClassContext(
            qualified_name=qualified_name,
            bases=frozenset(resolved_dotted_name(base, self.record) for base in node.bases),
            decorators=frozenset(
                resolved_dotted_name(item.func if isinstance(item, ast.Call) else item, self.record)
                for item in node.decorator_list
            ),
            is_ast_visitor=f"{self.record.name}.{qualified_name}" in self.visitor_classes,
        )
        self.class_stack.append(context)
        self.name_stack.append(node.name)
        self.generic_visit(node)
        self.name_stack.pop()
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a synchronous function definition."""
        self.visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an asynchronous function definition."""
        self.visit_function(node)

    def visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Collect diagnostics for one function definition."""
        qualified_name = ".".join((*self.name_stack, node.name))
        context = FunctionContext(
            relative_path=self.source.relative_path,
            name=node.name,
            qualified_name=qualified_name,
            decorators=frozenset(
                resolved_dotted_name(item.func if isinstance(item, ast.Call) else item, self.record)
                for item in node.decorator_list
            ),
            class_context=self.class_stack[-1] if self.class_stack else None,
        )
        self.collect_placeholder_docstring(context, node)
        if exemption_reason(context, node, self.policy, has_main_call=self.has_main_call) is None:
            self.collect_size_violations(context, node)
        self.name_stack.append(node.name)
        self.generic_visit(node)
        self.name_stack.pop()

    def collect_placeholder_docstring(
        self,
        context: FunctionContext,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        """Append a placeholder-docstring diagnostic when present."""
        docstring = ast.get_docstring(node, clean=False)
        if (
            context.relative_path.startswith(DOCSTRING_SOURCE_PREFIXES)
            and docstring is not None
            and docstring.startswith(PLACEHOLDER_DOCSTRING_PREFIXES)
        ):
            self.violations.append(
                {
                    "path": context.relative_path,
                    "line": node.lineno,
                    "code": "python.placeholder-docstring",
                    "name": context.qualified_name,
                    "message": "function docstring uses placeholder wording",
                },
            )

    def collect_size_violations(
        self,
        context: FunctionContext,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        """Append call-through or trivial-function diagnostics."""
        call = only_call(node)
        # Nested statements count too, so a short branch is as small as a short line, however often it is called.
        count = sum(
            1
            for statement in executable_statements(node)
            for child in ast.walk(statement)
            if isinstance(child, ast.stmt)
        )
        if call is not None and is_direct_call_through(node, call):
            code, message = "python.call-through", "function only forwards parameters"
        elif 0 < count <= self.policy["max_trivial_statements"]:
            code, message = "python.trivial-function", f"function has {count} statement(s); inline it"
        else:
            return
        self.violations.append(
            {
                "path": context.relative_path,
                "line": node.lineno,
                "code": code,
                "name": context.qualified_name,
                "message": message,
            },
        )


def collect_python_function_violations(
    source: PythonSource,
    policy: PythonFunctionPolicy,
    modules: Mapping[str, ModuleNames],
) -> list[NamedDiagnostic]:
    """Return Python function policy violations for one valid source."""
    tree = source.tree
    if tree is None:
        return []
    record = modules.get(module_name(source.relative_path))
    if record is None:
        return []

    violations: list[NamedDiagnostic] = []
    module_docstring = ast.get_docstring(tree, clean=False)
    if (
        source.relative_path.startswith(DOCSTRING_SOURCE_PREFIXES)
        and module_docstring is not None
        and module_docstring.startswith(PLACEHOLDER_DOCSTRING_PREFIXES)
    ):
        violations.append(
            {
                "path": source.relative_path,
                "line": 1,
                "code": "python.placeholder-docstring",
                "message": "module docstring uses placeholder wording",
            },
        )
    visitor = FunctionVisitor(source, policy, record, ast_visitor_classes(tree, record))
    visitor.visit(tree)
    violations.extend(visitor.violations)
    return violations


def exemption_reason(
    context: FunctionContext,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    policy: PythonFunctionPolicy,
    *,
    has_main_call: bool,
) -> str | None:
    """Return the fixed or repository-specific exemption reason."""
    class_context = context.class_context
    statements = executable_statements(node)
    checks = (
        ("decorator contract", bool(context.decorators.intersection(EXEMPT_DECORATORS))),
        (
            "protocol stub",
            class_context is not None
            and bool(class_context.bases.intersection(PROTOCOL_BASES))
            and bool(statements)
            and all(is_stub_statement(statement) for statement in statements),
        ),
        (
            "dataclass hook",
            class_context is not None
            and context.name in DATACLASS_HOOKS
            and bool(class_context.decorators.intersection(DATACLASS_DECORATORS)),
        ),
        ("required dunder", context.name in DUNDER_METHODS),
        (
            "host node hook",
            class_context is not None
            and bool(class_context.bases.intersection(HOST_NODE_BASES))
            and context.name in HOST_NODE_HOOKS,
        ),
        (
            "AST visitor callback",
            class_context is not None and class_context.is_ast_visitor and context.name.startswith("visit_"),
        ),
        ("module entrypoint", context.class_context is None and context.name == "main" and has_main_call),
        (
            "explicit allowlist",
            any(
                rule["path"] == context.relative_path and context.qualified_name in rule["names"]
                for rule in policy["allowlist"]
            ),
        ),
    )
    return next((reason for reason, matches in checks if matches), None)
