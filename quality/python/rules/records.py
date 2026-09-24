"""Check fixed-shape dataclass storage and explicitly mutable frozen fields."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING
from quality.lib.source import dotted_name
from quality.lib.diagnostics import diagnostic
from quality.config.python.rules import MUTABLE_RECORD_TYPES

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource
    from quality.lib.diagnostics import Diagnostic


def collect_record_violations(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Require slotted dataclasses and honest mutability for owned collection fields."""
    errors: list[Diagnostic] = []
    for source in sources:
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if isinstance(node, ast.ClassDef):
                errors.extend(_record_errors(source, node))
    return errors


def _record_errors(source: PythonSource, node: ast.ClassDef) -> list[Diagnostic]:
    """Inspect dataclasses without applying their storage rules to framework models."""
    errors: list[Diagnostic] = []
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if dotted_name(target) not in {"dataclass", "dataclasses.dataclass"}:
            continue
        options = (
            {item.arg: item.value.value for item in decorator.keywords if isinstance(item.value, ast.Constant)}
            if isinstance(decorator, ast.Call)
            else {}
        )
        if options.get("slots") is not True:
            errors.append(
                diagnostic(
                    source.relative_path, node.lineno, "record.slots", "use slots=True for fixed-shape dataclasses"
                )
            )
        if options.get("frozen") is True:
            errors.extend(
                diagnostic(
                    source.relative_path,
                    field.lineno,
                    "record.mutable-field",
                    "use immutable fields or declare mutable build state without frozen=True",
                )
                for field in node.body
                if isinstance(field, ast.AnnAssign)
                and any(dotted_name(part) in MUTABLE_RECORD_TYPES for part in ast.walk(field.annotation))
            )
    return errors
