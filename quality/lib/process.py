"""Subprocess boundary for repository quality tooling."""

from __future__ import annotations

import asyncio
from pathlib import Path
from shutil import which
from contextlib import suppress
from typing import TYPE_CHECKING
from dataclasses import dataclass
from types import MappingProxyType

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ProcessResult:
    """Captured result from one repository quality command.

    Attributes:
        return_code: Child exit status.
        stdout: Captured standard output.
        stderr: Captured standard error.

    """

    return_code: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True, slots=True)
class ProcessContext:
    """Execution directory, environment, and deadline for a child process.

    Attributes:
        working_directory: Child working directory.
        timeout_seconds: Maximum execution duration.
        environment: Read-only environment snapshot for the child.

    """

    working_directory: Path | None = None
    timeout_seconds: float | None = None
    environment: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        """Own a stable environment snapshot instead of retaining a caller's mutable mapping."""
        if self.environment is not None:
            object.__setattr__(self, "environment", MappingProxyType(dict(self.environment)))


def executable(name: str) -> str:
    """Return an absolute executable path from PATH."""
    found = which(name)
    if found is None:
        message = f"Executable not found on PATH: {name}"
        raise FileNotFoundError(message)
    # Preserve executable symlinks so Python can locate the selected virtual environment.
    return str(Path(found).absolute())


def run_command(
    arguments: Sequence[str],
    *,
    is_output_captured: bool = False,
    is_failure_raised: bool = False,
    context: ProcessContext | None = None,
) -> ProcessResult:
    """Run a fixed argument list without a shell."""
    if not arguments:
        message = "Command arguments must not be empty."
        raise ValueError(message)
    command = [executable(arguments[0]), *arguments[1:]]
    return asyncio.run(
        _run_subprocess(
            command,
            is_output_captured=is_output_captured,
            is_failure_raised=is_failure_raised,
            context=context or ProcessContext(),
        ),
    )


async def _run_subprocess(
    command: list[str],
    *,
    is_output_captured: bool,
    is_failure_raised: bool,
    context: ProcessContext,
) -> ProcessResult:
    """Run one resolved executable and collect its result."""
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=context.working_directory,
        env=context.environment,
        stdout=asyncio.subprocess.PIPE if is_output_captured else None,
        stderr=asyncio.subprocess.PIPE if is_output_captured else None,
    )
    try:
        async with asyncio.timeout(context.timeout_seconds):
            stdout, stderr = await process.communicate()
    finally:
        if process.returncode is None:
            with suppress(ProcessLookupError):
                process.kill()
            await process.communicate()
    return_code = process.returncode
    if return_code is None:
        message = f"Command did not report an exit status: {' '.join(command)}"
        raise RuntimeError(message)
    result = ProcessResult(
        return_code=return_code,
        stdout=stdout or b"",
        stderr=stderr or b"",
    )
    if is_failure_raised and return_code != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        message = f"Command failed with exit status {return_code}: {' '.join(command)}{suffix}"
        raise RuntimeError(message)
    return result
