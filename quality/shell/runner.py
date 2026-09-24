"""Run repository shell rules."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.files import read_utf8
from quality.lib.diagnostics import report_diagnostics
from quality.shell.checks.docs import check_shell_docs
from quality.shell.checks.bash import check_bash_scripts
from quality.shell.checks.safety import check_shell_safety
from quality.shell.checks.guards import check_config_guards
from quality.shell.checks.length import check_length_limits
from quality.shell.checks.embeds import check_runtime_embeds
from quality.shell.checks.config import check_config_defaults
from quality.shell.checks.heredocs import check_unnamed_heredocs
from quality.shell.scope import find_shell_files, parse_arguments
from quality.shell.checks.complexity import check_shell_complexity
from quality.shell.checks.architecture import check_shell_architecture
from quality.shell.checks.unused_functions import check_unused_functions
from quality.shell.checks.disable_justification import check_disable_justifications
from quality.shell.checks.duplicate_functions import collect_duplicate_function_bodies
from quality.config.shell import (
    RUNTIME_EMBED_FILES,
    SHELL_MAX_FILE_LINES,
    SHELL_MAX_FUNCTION_LINES,
    RUNTIME_EMBED_GLOBAL_SCOPES,
)

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic


def read_embed_sources(
    root: Path,
    scope: str,
    requested_paths: list[str],
    shell_sources: dict[str, str],
) -> dict[str, str]:
    """Return sources that participate in runtime embed checks."""
    sources = dict(shell_sources)
    candidate_paths = requested_paths or RUNTIME_EMBED_FILES
    for candidate in candidate_paths:
        path = root / candidate
        if not path.is_file() or candidate in sources:
            continue
        if scope not in RUNTIME_EMBED_GLOBAL_SCOPES and not candidate.startswith(f"{scope.rstrip('/')}/"):
            continue
        sources[candidate] = read_utf8(path)
    return sources


def run_shell_rule_set(
    *,
    scope: str,
    paths: list[str],
    root: Path,
) -> list[Diagnostic]:
    """Return diagnostics from all configured shell project rules."""
    files = find_shell_files(scope, paths, root=root, is_shebang_included=True)
    sources = {file: read_utf8(root / file) for file in files}
    embed_sources = read_embed_sources(root, scope, paths, sources)
    errors: list[Diagnostic] = []
    errors.extend(check_config_defaults(sources))
    errors.extend(check_unnamed_heredocs(sources))
    errors.extend(check_bash_scripts(sources, root))
    errors.extend(check_runtime_embeds(embed_sources))
    errors.extend(check_length_limits(sources, SHELL_MAX_FILE_LINES, SHELL_MAX_FUNCTION_LINES))
    errors.extend(check_shell_docs(sources, root))
    errors.extend(check_config_guards(sources))
    errors.extend(check_shell_architecture(sources, root))
    errors.extend(check_shell_complexity(sources))
    errors.extend(check_shell_safety(sources))
    errors.extend(check_unused_functions(sources))
    errors.extend(check_disable_justifications(sources))
    errors.extend(collect_duplicate_function_bodies(sources))
    return errors


def main() -> int:
    """Run shell project rules."""
    scope, requested_paths = parse_arguments(sys.argv[1:])
    errors = run_shell_rule_set(scope=scope, paths=requested_paths, root=Path.cwd())
    return report_diagnostics("Shell project rule violations:", errors)


if __name__ == "__main__":
    raise SystemExit(main())
