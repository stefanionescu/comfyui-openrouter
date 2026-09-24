"""Load the repository function policy."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TypedDict
from quality.lib.files import read_utf8
from quality.config.repository.functions import FUNCTION_POLICY_PATH, FUNCTION_POLICY_VERSION
from quality.lib.json_config import (
    require_int,
    require_keys,
    JsonConfigError,
    require_mapping,
    require_sequence,
    read_json_mapping,
    require_string_list,
)


class NamedFunctionRule(TypedDict):
    """Exact path-scoped function exemption."""

    path: str
    names: list[str]
    reason: str


class PythonFunctionPolicy(TypedDict):
    """Python function policy."""

    max_trivial_statements: int
    allowlist: list[NamedFunctionRule]


class ShellFunctionPolicy(TypedDict):
    """Shell function policy."""

    max_trivial_statements: int


class FunctionPolicy(TypedDict):
    """Validated function policy document."""

    version: int
    python: PythonFunctionPolicy
    shell: ShellFunctionPolicy


def read_function_policy(root: Path) -> FunctionPolicy:
    """Read the validated Python and shell function policy."""
    payload = read_json_mapping(root / FUNCTION_POLICY_PATH)
    require_keys(payload, required={"version", "python", "shell"}, context=FUNCTION_POLICY_PATH)
    require_function_version(payload["version"])
    python = require_mapping(payload["python"], f"{FUNCTION_POLICY_PATH}.python")
    require_keys(
        python,
        required={"max_trivial_statements", "allowlist"},
        context=f"{FUNCTION_POLICY_PATH}.python",
    )
    max_python_statements = require_int(
        python["max_trivial_statements"],
        f"{FUNCTION_POLICY_PATH}.python.max_trivial_statements",
    )
    allowlist = validate_named_rules(root, python["allowlist"])

    shell = require_mapping(payload["shell"], f"{FUNCTION_POLICY_PATH}.shell")
    require_keys(shell, required={"max_trivial_statements"}, context=f"{FUNCTION_POLICY_PATH}.shell")
    max_shell_statements = require_int(
        shell["max_trivial_statements"],
        f"{FUNCTION_POLICY_PATH}.shell.max_trivial_statements",
    )
    return {
        "version": FUNCTION_POLICY_VERSION,
        "python": {
            "max_trivial_statements": max_python_statements,
            "allowlist": allowlist,
        },
        "shell": {
            "max_trivial_statements": max_shell_statements,
        },
    }


def validate_named_rules(root: Path, value: object) -> list[NamedFunctionRule]:
    """Validate path-scoped function exemptions."""
    context = f"{FUNCTION_POLICY_PATH}.python.allowlist"
    rules = [
        require_mapping(item, f"{context}[{index}]") for index, item in enumerate(require_sequence(value, context))
    ]
    validated: list[NamedFunctionRule] = []
    seen: set[tuple[str, str]] = set()
    for index, rule in enumerate(rules):
        item_context = f"{context}[{index}]"
        validated.append(validate_named_rule(root, rule, item_context, seen))
    return validated


def validate_named_rule(
    root: Path,
    rule: dict[str, object],
    context: str,
    seen: set[tuple[str, str]],
) -> NamedFunctionRule:
    """Validate one exact function exemption record."""
    require_keys(rule, required={"path", "names", "reason"}, context=context)
    path_value = require_nonempty_text(rule["path"], f"{context}.path")
    reason = require_nonempty_text(rule["reason"], f"{context}.reason")
    relative_path = Path(path_value)
    if (
        relative_path.is_absolute()
        or ".." in relative_path.parts
        or any(character in path_value for character in "*?[")
    ):
        message = f"{context}.path must be an exact repository-relative path"
        raise JsonConfigError(message)
    source_path = root / relative_path
    if not source_path.is_file():
        message = f"{context}.path does not name a file: {path_value}"
        raise JsonConfigError(message)
    names = require_string_list(rule["names"], f"{context}.names", is_nonempty=True)
    if len(names) != len(set(names)):
        message = f"{context}.names contains duplicates"
        raise JsonConfigError(message)
    validate_function_names(path_value, names, function_names(source_path), context, seen)
    return {"path": path_value, "names": names, "reason": reason}


def require_nonempty_text(value: object, context: str) -> str:
    """Return one non-empty policy string."""
    if not isinstance(value, str) or not value:
        message = f"{context} must be a non-empty string"
        raise JsonConfigError(message)
    return value


def validate_function_names(
    path: str,
    names: list[str],
    available: set[str],
    context: str,
    seen: set[tuple[str, str]],
) -> None:
    """Validate function names and cross-record duplicates."""
    for name in names:
        key = (path, name)
        if key in seen:
            message = f"{context} duplicates exemption {path}:{name}"
            raise JsonConfigError(message)
        if name not in available:
            message = f"{context}.names references missing function {path}:{name}"
            raise JsonConfigError(message)
        seen.add(key)


def function_names(path: Path) -> set[str]:
    """Return qualified function names declared in one Python module."""
    try:
        tree = ast.parse(read_utf8(path), filename=path.as_posix())
    except SyntaxError as error:
        message = f"{path.as_posix()} cannot validate function exemptions: {error}"
        raise JsonConfigError(message) from error
    names: set[str] = set()
    scope: list[str] = []

    class Collector(ast.NodeVisitor):
        """Collect functions with their enclosing class and function names."""

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Visit one class scope."""
            scope.append(node.name)
            self.generic_visit(node)
            scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Collect one synchronous function."""
            collect(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Collect one asynchronous function."""
            collect(node)

    def collect(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Collect a function and visit its nested definitions."""
        names.add(".".join((*scope, node.name)))
        scope.append(node.name)
        Collector().generic_visit(node)
        scope.pop()

    Collector().visit(tree)
    return names


def require_function_version(value: object) -> None:
    """Require the supported function policy version."""
    context = f"{FUNCTION_POLICY_PATH}.version"
    if require_int(value, context, minimum=1) != FUNCTION_POLICY_VERSION:
        message = f"{context} must be {FUNCTION_POLICY_VERSION}"
        raise JsonConfigError(message)
