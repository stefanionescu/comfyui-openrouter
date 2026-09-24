"""Fixed Python language semantics for function-policy analysis."""

from __future__ import annotations

import ast
from quality.lib.source import dotted_name
from quality.repository.functions.references import ModuleNames, resolved_dotted_name

EXEMPT_DECORATORS = {
    "abc.abstractmethod",
    "contextlib.contextmanager",
    "property",
    "pydantic.field_validator",
    "pydantic.model_validator",
    "typing.overload",
}
PROTOCOL_BASES = {"typing.Protocol"}
DATACLASS_DECORATORS = {
    "attr.s",
    "attrs.define",
    "attrs.frozen",
    "dataclasses.dataclass",
    "pydantic.dataclasses.dataclass",
}
AST_VISITOR_BASES = {"ast.NodeTransformer", "ast.NodeVisitor"}
DATACLASS_HOOKS = {"__post_init__"}
DUNDER_METHODS = {
    "__aiter__",
    "__anext__",
    "__aenter__",
    "__aexit__",
    "__bool__",
    "__bytes__",
    "__contains__",
    "__del__",
    "__enter__",
    "__eq__",
    "__exit__",
    "__format__",
    "__ge__",
    "__getitem__",
    "__gt__",
    "__hash__",
    "__init__",
    "__iter__",
    "__le__",
    "__len__",
    "__lt__",
    "__ne__",
    "__next__",
    "__repr__",
    "__setitem__",
    "__str__",
}


def ast_visitor_classes(tree: ast.Module, record: ModuleNames) -> set[str]:
    """Return classes that inherit from AST visitor bases."""
    bases_by_class: dict[str, set[str]] = {}
    scope: list[str] = []

    class Collector(ast.NodeVisitor):
        """Collect resolved class bases."""

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Track a synchronous function scope."""
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Track an asynchronous function scope."""
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Collect one class and visit nested classes."""
            qualified = ".".join((*scope, node.name))
            bases_by_class[f"{record.name}.{qualified}"] = {resolved_dotted_name(base, record) for base in node.bases}
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

    Collector().visit(tree)
    visitors = {name for name, bases in bases_by_class.items() if bases.intersection(AST_VISITOR_BASES)}
    is_changed = True
    while is_changed:
        is_changed = False
        for name, bases in bases_by_class.items():
            if name not in visitors and bases.intersection(visitors):
                visitors.add(name)
                is_changed = True
    return visitors


def main_guard_calls(tree: ast.Module, function_name: str) -> bool:
    """Return whether a real main guard calls the named function."""
    for statement in tree.body:
        if not isinstance(statement, ast.If) or not is_main_guard(statement):
            continue
        guarded_body = ast.Module(body=statement.body, type_ignores=[])
        if any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == function_name
            for node in ast.walk(guarded_body)
        ):
            return True
    return False


def is_main_guard(node: ast.stmt) -> bool:
    """Return whether a statement is an exact __name__ main guard."""
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    test = node.test
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    left = test.left
    right = test.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    ) or (
        isinstance(right, ast.Name)
        and right.id == "__name__"
        and isinstance(left, ast.Constant)
        and left.value == "__main__"
    )


def executable_statements(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
    """Return executable statements without a leading docstring."""
    statements = list(node.body)
    if (
        statements
        and isinstance(statements[0], ast.Expr)
        and isinstance(statements[0].value, ast.Constant)
        and isinstance(statements[0].value.value, str)
    ):
        statements.pop(0)
    return statements


def is_stub_statement(statement: ast.stmt) -> bool:
    """Return whether a statement is a stub marker."""
    if isinstance(statement, ast.Pass):
        return True
    if isinstance(statement, ast.Expr):
        return isinstance(statement.value, ast.Constant) and statement.value.value is Ellipsis
    return isinstance(statement, ast.Raise) and dotted_name(statement.exc) == "NotImplementedError"


def only_call(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.Call | None:
    """Return the only call expression in a pass-through function."""
    statements = executable_statements(node)
    if len(statements) != 1:
        return None
    statement = statements[0]
    expression = statement.value if isinstance(statement, ast.Return | ast.Expr) else None
    while isinstance(expression, ast.Await):
        expression = expression.value
    return expression if isinstance(expression, ast.Call) else None


def is_direct_call_through(node: ast.FunctionDef | ast.AsyncFunctionDef, call: ast.Call) -> bool:
    """Return whether a function directly forwards all positional parameters."""
    arguments = node.args
    if arguments.vararg or arguments.kwonlyargs or arguments.kwarg or call.keywords:
        return False
    parameters = tuple(argument.arg for argument in (*arguments.posonlyargs, *arguments.args))
    if len(call.args) != len(parameters):
        return False
    return all(
        isinstance(argument, ast.Name) and argument.id == parameters[index] for index, argument in enumerate(call.args)
    )


__all__ = [
    "DATACLASS_DECORATORS",
    "DATACLASS_HOOKS",
    "DUNDER_METHODS",
    "EXEMPT_DECORATORS",
    "PROTOCOL_BASES",
    "ast_visitor_classes",
    "executable_statements",
    "is_direct_call_through",
    "is_stub_statement",
    "main_guard_calls",
    "only_call",
]
