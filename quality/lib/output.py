"""Console output for quality commands."""

from __future__ import annotations

import sys


def write_line(message: str) -> None:
    """Write a line to stdout."""
    stream = sys.stdout
    stream.write(f"{message}\n")
    stream.flush()


def write_error(message: str) -> None:
    """Write a line to stderr."""
    stream = sys.stderr
    stream.write(f"{message}\n")
    stream.flush()
