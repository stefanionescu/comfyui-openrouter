"""Build the browser bundle, or check the shipped one."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
import argparse

from scripts.paths import WEB_DIR, REPO_ROOT, FRONTEND_CHECK_DIR
from scripts.problems import report_problems

if TYPE_CHECKING:
    from pathlib import Path

BUNDLE = 'extension.js'
STYLES = 'extension.css'


async def _build_bundle(destination: Path) -> None:
    """Run the build script of package.json, with its output in the given folder."""
    process = await asyncio.create_subprocess_exec(
        'bun', 'run', '--no-install', 'build', f'--outfile={destination / BUNDLE}', cwd=REPO_ROOT
    )
    if await process.wait() != 0:
        message = 'esbuild failed.'
        raise RuntimeError(message)


def main() -> int:
    """Build the bundle into web/, or report when the shipped bundle differs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    if not arguments.check:
        asyncio.run(_build_bundle(WEB_DIR))
        return 0
    scratch = FRONTEND_CHECK_DIR
    scratch.mkdir(parents=True, exist_ok=True)
    asyncio.run(_build_bundle(scratch))
    problems = [
        f'Rebuild {name} with mise run comfy:frontend:build.'
        for name in (BUNDLE, STYLES)
        if not (built := WEB_DIR / name).is_file() or built.read_bytes() != (scratch / name).read_bytes()
    ]
    return report_problems(problems)


if __name__ == '__main__':
    raise SystemExit(main())
