"""Check shell default-value policy."""

from __future__ import annotations

from typing import TYPE_CHECKING
from quality.lib.diagnostics import diagnostic
from quality.config.shell import (
    SHELL_CONFIG_PREFIXES,
    ALLOWED_DEFAULT_FRAGMENTS,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def check_config_defaults(sources: dict[str, str]) -> list[Diagnostic]:
    """Return default expansion diagnostics outside config owners."""
    errors: list[Diagnostic] = []
    for path, source in sources.items():
        if path.startswith(SHELL_CONFIG_PREFIXES):
            continue
        for line_number, line in enumerate(source.splitlines(), start=1):
            has_allowed_default = any(fragment in line for fragment in ALLOWED_DEFAULT_FRAGMENTS)
            if ":-" in line and not line.lstrip().startswith("#") and not has_allowed_default:
                errors.append(
                    diagnostic(
                        path,
                        line_number,
                        "shell.default-expansion",
                        "default expansions belong in config owners",
                    ),
                )
    return errors
