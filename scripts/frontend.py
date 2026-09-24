"""Build the browser bundle, or check the shipped one."""

from __future__ import annotations

import sys
import asyncio
import argparse
from typing import TYPE_CHECKING
from scripts.paths import WEB_DIR, REPO_ROOT, FRONTEND_CHECK_DIR

if TYPE_CHECKING:
    from pathlib import Path

ENTRY = "web/scripts/extension.ts"
BUNDLE = "extension.js"
STYLES = "extension.css"
HOST_MODULES = ("../../scripts/app.js", "../../scripts/api.js")


async def _build_bundle(destination: Path) -> None:
    """Run esbuild into the given folder."""
    process = await asyncio.create_subprocess_exec(
        "bun",
        "x",
        "esbuild",
        ENTRY,
        f"--outfile={destination / BUNDLE}",
        "--bundle",
        "--platform=browser",
        "--format=esm",
        "--target=es2022",
        "--charset=utf8",
        "--legal-comments=inline",
        *(f"--external:{module}" for module in HOST_MODULES),
        cwd=REPO_ROOT,
    )
    if await process.wait() != 0:
        message = "esbuild failed."
        raise RuntimeError(message)


def main() -> int:
    """Build the bundle into web/, or report when the shipped bundle differs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if not arguments.check:
        asyncio.run(_build_bundle(WEB_DIR))
        return 0
    scratch = FRONTEND_CHECK_DIR
    scratch.mkdir(parents=True, exist_ok=True)
    asyncio.run(_build_bundle(scratch))
    problems = [
        f"Rebuild {name} with mise run comfy:frontend:build."
        for name in (BUNDLE, STYLES)
        if not (built := WEB_DIR / name).is_file() or built.read_bytes() != (scratch / name).read_bytes()
    ]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
