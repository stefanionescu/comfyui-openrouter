"""Read and parse Python sources once per quality process."""

from __future__ import annotations

import io
import ast
import tokenize
from functools import cache
from typing import TYPE_CHECKING
from dataclasses import dataclass
from quality.lib.files import read_utf8

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class PythonSource:
    """Source text, syntax tree, and line metadata for one Python file.

    Attributes:
        path: Resolved source file.
        relative_path: Repository-relative diagnostic path.
        text: Original decoded source.
        lines: Source lines in order.
        tree: Borrowed syntax tree, treated as read-only by every checker.
        syntax_error: Captured parse failure, if any.
        comment_lines: Lines containing comments.
        docstring_lines: Lines belonging to docstrings.
        constant_string_lines: Lines belonging to declared constant strings.

    """

    path: Path
    relative_path: str
    text: str
    lines: tuple[str, ...]
    tree: ast.Module | None
    syntax_error: SyntaxError | None
    comment_lines: frozenset[int]
    docstring_lines: frozenset[int]
    constant_string_lines: frozenset[int]


@cache
def read_python_source(root: Path, path: Path) -> PythonSource:
    """Read one UTF-8 module and cache its syntax and line classifications."""
    text = read_utf8(path)
    try:
        tree = ast.parse(text, filename=str(path))
        syntax_error = None
    except SyntaxError as error:
        tree = None
        syntax_error = error
    return PythonSource(
        path=path,
        relative_path=path.relative_to(root).as_posix(),
        text=text,
        lines=tuple(text.splitlines()),
        tree=tree,
        syntax_error=syntax_error,
        comment_lines=frozenset(comment_lines(text)),
        docstring_lines=frozenset(docstring_lines(tree)),
        constant_string_lines=frozenset(constant_string_lines(tree)),
    )


def comment_lines(text: str) -> set[int]:
    """Return line numbers containing Python comments."""
    comments: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT and not token.line[: token.start[1]].strip():
                comments.add(token.start[0])
    except tokenize.TokenError:
        return comments
    return comments


def docstring_lines(tree: ast.Module | None) -> set[int]:
    """Return every line occupied by a module, class, or function docstring."""
    lines: set[int] = set()
    if tree is None:
        return lines
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) or not node.body:
            continue
        first = node.body[0]
        if not isinstance(first, ast.Expr) or not isinstance(first.value, ast.Constant):
            continue
        if not isinstance(first.value.value, str):
            continue
        lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return lines


def constant_string_lines(tree: ast.Module | None) -> set[int]:
    """Return lines occupied by top-level uppercase string constants."""
    lines: set[int] = set()
    if tree is None:
        return lines
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not targets or any(not target.isupper() for target in targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            lines.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return lines


def dotted_name(node: ast.AST | None) -> str:
    """Return a dotted callable or expression name."""
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""
