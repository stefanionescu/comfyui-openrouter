"""Check the help pages and menus against the registered nodes."""

from __future__ import annotations

import os
import re
import sys
import json
import asyncio
import argparse
from typing import cast
from pathlib import Path
from src.paths import EXTENSION_ROOT
from src.config.namespace import (
    CHAT_MENU,
    AUDIO_MENU,
    IMAGE_MENU,
    VIDEO_MENU,
    SEARCH_MENU,
    SHARED_MENU,
    DECISION_MENU,
)

Schema = dict[str, object]
SOCKET_ROW = re.compile(r"^\| `([a-z_.]+)` \|")
MENUS = (SHARED_MENU, CHAT_MENU, IMAGE_MENU, VIDEO_MENU, AUDIO_MENU, SEARCH_MENU, DECISION_MENU)


def read_host_installation() -> tuple[Path, Path]:
    """Return the ComfyUI folder and its Python interpreter."""
    chosen = os.environ.get("COMFYUI_PATH", "")
    if not chosen:
        message = "Set COMFYUI_PATH to the ComfyUI folder that holds main.py."
        raise ValueError(message)
    host = Path(chosen).expanduser().resolve(strict=True)
    if not (host / "main.py").is_file():
        message = f"{host} holds no main.py; set COMFYUI_PATH to the ComfyUI folder."
        raise ValueError(message)
    interpreter = Path(os.environ.get("COMFYUI_PYTHON", "") or host / ".venv" / "bin" / "python")
    if not interpreter.is_file():
        message = "Set COMFYUI_PYTHON to the Python interpreter of the ComfyUI environment."
        raise ValueError(message)
    return host, interpreter


def read_schemas() -> dict[str, object]:
    """Describe the nodes and the host nodes the workflows place."""
    host, interpreter = read_host_installation()
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join((str(host), str(EXTENSION_ROOT))))
    return cast("dict[str, object]", json.loads(asyncio.run(_describe(interpreter, environment))))


async def _describe(interpreter: Path, environment: dict[str, str]) -> str:
    """Run the schema script in ComfyUI's interpreter."""
    process = await asyncio.create_subprocess_exec(
        str(interpreter),
        str(EXTENSION_ROOT / "scripts/nodes/schema.py"),
        cwd=EXTENSION_ROOT,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        message = f"The schema export failed:\n{stderr.decode()}"
        raise RuntimeError(message)
    return stdout.decode()


def check_help_pages(schemas: dict[str, Schema]) -> list[str]:
    """Check that every node has a help page naming real inputs."""
    problems: list[str] = []
    pages = {path.stem: path for path in (EXTENSION_ROOT / "web/docs").glob("*.md")}
    problems.extend(f"Add web/docs/{node_id}.md." for node_id in schemas if node_id not in pages)
    for stem, path in sorted(pages.items()):
        schema = schemas.get(stem)
        if schema is None:
            problems.append(f"Name {path.name} for a registered node.")
            continue
        sockets = {item["name"] for item in cast("list[dict[str, object]]", schema["inputs"])}
        sockets |= {item["name"] for item in cast("list[dict[str, object]]", schema["outputs"])}
        for line in path.read_text(encoding="utf-8").splitlines():
            row = SOCKET_ROW.match(line)
            if row and row.group(1).split(".")[0] not in sockets:
                problems.append(f"{path.name}: {stem} has no socket named {row.group(1)}.")
    return problems


def main() -> int:
    """Check the help pages and menus, or print the schemas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true", help="Print the node descriptions instead of checking.")
    arguments = parser.parse_args()
    export = read_schemas()
    if arguments.export:
        sys.stdout.write(json.dumps(export, indent=2) + "\n")
        return 0
    schemas = cast("dict[str, Schema]", export["nodes"])
    problems = check_help_pages(schemas)
    problems += [
        f"Put {node_id} in an OpenRouter menu."
        for node_id, schema in schemas.items()
        if schema["category"] not in MENUS
    ]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
