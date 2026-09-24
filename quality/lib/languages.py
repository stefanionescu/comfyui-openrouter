"""Source-language classification for quality tooling."""

from __future__ import annotations

from quality.config.shell import BASH_SHEBANGS
from quality.config.repository.paths import SHELL_TASK_PREFIXES


def source_language(
    relative_path: str,
    source_text: str = "",
    *,
    are_task_paths_included: bool = False,
) -> str | None:
    """Return python, shell, or None for a repository path."""
    if relative_path.endswith(".py"):
        return "python"
    first_line = source_text.splitlines()[0] if source_text.splitlines() else ""
    is_shell = (
        relative_path.endswith(".sh")
        or (are_task_paths_included and relative_path.startswith(tuple(SHELL_TASK_PREFIXES)))
        or first_line in BASH_SHEBANGS
    )
    if is_shell:
        return "shell"
    return None
