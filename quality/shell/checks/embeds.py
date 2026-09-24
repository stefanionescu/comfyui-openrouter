"""Validate embedded runtime blocks in shell scripts."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.shell import RUNTIME_EMBED_RULES

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic

EMBED_PATTERNS = tuple((re.compile(pattern), message) for pattern, message in RUNTIME_EMBED_RULES)


def check_runtime_embeds(sources: dict[str, str]) -> list[Diagnostic]:
    """Return inline runtime heredoc diagnostics."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        for line_number, line in enumerate(source.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            for pattern, message in EMBED_PATTERNS:
                if pattern.search(line):
                    errors.append(diagnostic(path, line_number, "shell.inline-runtime", message))
                    break
    return errors
