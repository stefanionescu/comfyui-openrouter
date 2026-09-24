"""Validate inline suppression directives across Git-visible files."""

from __future__ import annotations

import io
import re
import argparse
import tokenize
from pathlib import Path
from dataclasses import dataclass
from quality.lib.diagnostics import Diagnostic, diagnostic, report_diagnostics
from quality.lib.files import read_utf8, git_files, VISIBLE_FILE_ARGUMENTS, STAGED_FILE_ARGUMENTS

NOSEMGREP_RE = re.compile(r"\bnosem" + r"grep\b", re.IGNORECASE)
NOSEC_RE = re.compile(r"\bnosec\b(?P<tail>.*)$", re.IGNORECASE)
NOQA_RE = re.compile(r"\bnoqa\b(?P<tail>.*)$", re.IGNORECASE)
BEARER_DISABLE_RE = re.compile(r"\bbearer:disable\b(?P<tail>.*)$", re.IGNORECASE)
TYPE_IGNORE_RE = re.compile(r"\btype:\s*ignore(?P<tail>.*)$", re.IGNORECASE)
PYRIGHT_IGNORE_RE = re.compile(r"\bpyright:\s*ignore(?P<tail>.*)$", re.IGNORECASE)
COVERAGE_RE = re.compile(r"\bpragma:\s*no\s+cover(?P<tail>.*)$", re.IGNORECASE)
REASON_SEPARATOR = " -- reason: "
BANDIT_CODES_RE = re.compile(r"^(B[0-9]{3})(?:[,\s]+B[0-9]{3})*$")
NOQA_CODES_RE = re.compile(r"^:[ \t]*[A-Z]+[0-9]+(?:[ \t]*,[ \t]*[A-Z]+[0-9]+)*$")
BRACKET_CODES_RE = re.compile(r"^\[[A-Za-z0-9_.-]+(?:\s*,\s*[A-Za-z0-9_.-]+)*\]$")
BEARER_CODES_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\s*,\s*[a-z][a-z0-9_]*)*$")


@dataclass(frozen=True, slots=True)
class DirectivePolicy:
    """One governed inline suppression directive.

    Attributes:
        pattern: Pattern identifying a suppression.
        code: Diagnostic code.
        message: Diagnostic explanation.
        prefix_pattern: Required directive prefix, when applicable.

    """

    pattern: re.Pattern[str]
    code: str
    message: str
    prefix_pattern: re.Pattern[str] | None


def collect_suppression_diagnostics(root: Path, scope: str = "all") -> list[Diagnostic]:
    """Return invalid suppression directives in Git-visible repository files."""
    diagnostics: list[Diagnostic] = []
    paths = (
        git_files(STAGED_FILE_ARGUMENTS, root=root, is_existing_required=True)
        if scope == "staged"
        else git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True)
    )
    for relative_path in paths:
        path = root / relative_path
        is_governed = path.suffix in {".py", ".sh", ".toml", ".yaml", ".yml"} or relative_path.startswith(
            (".githooks/", ".mise/tasks/"),
        )
        if not path.is_file() or not is_governed:
            continue
        source = read_utf8(path)
        source_lines = source.splitlines()
        for line_number, comment in source_comments(path, source):
            diagnostics.extend(line_diagnostics(relative_path, line_number, comment))
            diagnostics.extend(nosec_diagnostics(relative_path, line_number, comment, source_lines))
            diagnostics.extend(bearer_diagnostics(relative_path, line_number, comment, source_lines))
    return diagnostics


def source_comments(path: Path, source: str) -> list[tuple[int, str]]:
    """Return comment text with source line numbers."""
    if path.suffix == ".py":
        try:
            tokenized_comments = [
                (token.start[0], token.string)
                for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type == tokenize.COMMENT
            ]
        except tokenize.TokenError:
            tokenized_comments = None
        if tokenized_comments is not None:
            return tokenized_comments
    return [
        (line_number, line[line.index("#") :])
        for line_number, line in enumerate(source.splitlines(), start=1)
        if "#" in line
    ]


def line_diagnostics(path: str, line_number: int, line: str) -> list[Diagnostic]:
    """Return suppression diagnostics for one source line."""
    diagnostics: list[Diagnostic] = []
    if NOSEMGREP_RE.search(line):
        diagnostics.append(
            diagnostic(path, line_number, "suppression.nosemgrep", "nosemgrep directives are forbidden"),
        )
    for policy in DIRECTIVE_POLICIES:
        diagnostics.extend(validate_directive(path, line_number, line, policy))
    return diagnostics


def validate_directive(
    path: str,
    line_number: int,
    line: str,
    policy: DirectivePolicy,
) -> list[Diagnostic]:
    """Validate one optional directive occurrence."""
    match = policy.pattern.search(line)
    if match is None:
        return []
    tail = match.group("tail")
    prefix, separator, reason = tail.partition(REASON_SEPARATOR)
    stripped_prefix = prefix.strip()
    is_valid_prefix = (
        not stripped_prefix
        if policy.prefix_pattern is None
        else policy.prefix_pattern.fullmatch(stripped_prefix) is not None
    )
    if separator and reason.strip() and is_valid_prefix:
        return []
    return [diagnostic(path, line_number, policy.code, policy.message)]


def preceding_reason(line_number: int, source_lines: list[str]) -> str | None:
    """Return an immediately preceding suppression reason."""
    previous_line = source_lines[line_number - 2].strip() if line_number > 1 else ""
    if not previous_line.startswith("# reason:"):
        return None
    reason = previous_line.removeprefix("# reason:").strip()
    return reason or None


def nosec_diagnostics(
    path: str,
    line_number: int,
    line: str,
    source_lines: list[str],
) -> list[Diagnostic]:
    """Validate one optional Bandit suppression."""
    match = NOSEC_RE.search(line)
    if match is None:
        return []
    rule_ids = match.group("tail").strip()
    if BANDIT_CODES_RE.fullmatch(rule_ids) is not None and preceding_reason(line_number, source_lines):
        return []
    return [
        diagnostic(
            path,
            line_number,
            "suppression.nosec",
            "nosec requires Bandit IDs and an immediately preceding reason comment",
        ),
    ]


def bearer_diagnostics(
    path: str,
    line_number: int,
    line: str,
    source_lines: list[str],
) -> list[Diagnostic]:
    """Validate one optional Bearer block suppression."""
    match = BEARER_DISABLE_RE.search(line)
    if match is None:
        return []
    rule_ids = match.group("tail").strip()
    if BEARER_CODES_RE.fullmatch(rule_ids) is not None and preceding_reason(line_number, source_lines):
        return []
    return [
        diagnostic(
            path,
            line_number,
            "suppression.bearer-disable",
            "Bearer disable requires explicit rule IDs and an immediately preceding reason comment",
        ),
    ]


DIRECTIVE_POLICIES = (
    DirectivePolicy(
        NOQA_RE,
        "suppression.noqa",
        "noqa requires explicit codes and a same-line reason",
        NOQA_CODES_RE,
    ),
    DirectivePolicy(
        TYPE_IGNORE_RE,
        "suppression.type-ignore",
        "type ignore requires bracketed diagnostics and a same-line reason",
        BRACKET_CODES_RE,
    ),
    DirectivePolicy(
        PYRIGHT_IGNORE_RE,
        "suppression.pyright-ignore",
        "pyright ignore requires bracketed diagnostics and a same-line reason",
        BRACKET_CODES_RE,
    ),
    DirectivePolicy(
        COVERAGE_RE,
        "suppression.coverage",
        "coverage pragma requires a same-line reason",
        None,
    ),
)


def main() -> int:
    """Run inline suppression policy."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("all", "staged"), default="all")
    arguments = parser.parse_args()
    diagnostics = collect_suppression_diagnostics(Path.cwd(), arguments.scope)
    return report_diagnostics("Inline suppression policy violations:", diagnostics)


if __name__ == "__main__":
    raise SystemExit(main())
