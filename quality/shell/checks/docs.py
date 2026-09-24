"""Validate shell function documentation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.shell.parsers import collect_shell_functions
from quality.shell.checks.bash import is_architecture_source, is_file_executable

if TYPE_CHECKING:
    from pathlib import Path
    from quality.lib.diagnostics import Diagnostic
    from quality.shell.parsers import ShellFunction

DOC_SECTIONS = ("# Globals:", "# Arguments:", "# Outputs:", "# Returns:")
SUMMARY_RE = re.compile(r"^# (?P<name>[A-Za-z_][A-Za-z0-9_]*) - (?P<summary>.+)$")
SUMMARY_WORD_RE = re.compile(r"[A-Za-z0-9]+")
VAGUE_SUMMARY_WORDS = {
    "a",
    "an",
    "and",
    "execute",
    "executes",
    "handle",
    "handles",
    "perform",
    "performs",
    "run",
    "runs",
    "the",
}
RISKY_FUNCTION_RE = re.compile(r"\b(?:kill|mv|rm|source|sudo)\b")


def function_doc_block(lines: list[str], declaration_line: int) -> list[str]:
    """Return the contiguous comment block before one function."""
    index = declaration_line - 2
    block: list[str] = []
    while index >= 0 and lines[index].startswith("#"):
        block.append(lines[index].rstrip())
        index -= 1
    block.reverse()
    return block


def has_meaningful_summary(name: str, summary: str) -> bool:
    """Return whether a summary adds information beyond the function name."""
    name_words = set(name.removeprefix("_").split("_"))
    summary_words = {
        word.lower() for word in SUMMARY_WORD_RE.findall(summary) if word.lower() not in VAGUE_SUMMARY_WORDS
    }
    return bool(summary_words - name_words)


def requires_full_contract(path: str, name: str, body: list[str], root: Path) -> bool:
    """Return whether one function requires the full shell contract block."""
    if name == "main":
        return False
    if not is_file_executable(root / path) and not name.startswith("_"):
        return True
    function_source = "\n".join(body)
    return RISKY_FUNCTION_RE.search(function_source) is not None


def check_function_doc(
    path: str,
    function: ShellFunction,
    lines: list[str],
    root: Path,
) -> list[Diagnostic]:
    """Return documentation diagnostics for one shell function."""
    name = str(function["name"])
    start = int(function["start"])
    block = function_doc_block(lines, start)
    if not block:
        return [diagnostic(path, start, "shell.function-doc", f"{name} requires a function comment")]
    summary_match = SUMMARY_RE.fullmatch(block[0])
    if summary_match is None or summary_match.group("name") != name:
        return [
            diagnostic(
                path,
                start,
                "shell.function-doc",
                f"{name} requires an immediate '# {name} - ...' summary",
            ),
        ]
    errors: list[Diagnostic] = []
    summary = summary_match.group("summary")
    if not has_meaningful_summary(name, summary):
        errors.append(
            diagnostic(
                path,
                start,
                "shell.function-summary",
                f"{name} summary must describe concrete behavior",
            ),
        )
    body = function["body"]
    if requires_full_contract(path, name, body, root):
        positions = [block.index(section) if section in block else -1 for section in DOC_SECTIONS]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append(
                diagnostic(
                    path,
                    start,
                    "shell.function-contract",
                    f"{name} requires Globals, Arguments, Outputs, and Returns sections in order",
                ),
            )
    return errors


def check_shell_docs(sources: dict[str, str], root: Path) -> list[Diagnostic]:
    """Return diagnostics for undocumented shell functions."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if not is_architecture_source(path):
            continue
        lines = source.splitlines()
        for function in collect_shell_functions(source):
            errors.extend(check_function_doc(path, function, lines, root))
    return errors
