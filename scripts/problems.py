"""Report the problems that a check script finds."""

import sys
from collections.abc import Sequence


def report_problems(problems: Sequence[str]) -> int:
    """Write each problem on its own line to standard error, and return 1 when there is one, else 0."""
    for problem in problems:
        sys.stderr.write(problem + '\n')
    return int(bool(problems))


__all__ = ['report_problems']
