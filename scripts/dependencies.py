"""Export the runtime dependencies used by ComfyUI installers."""

import sys
import tomllib
import argparse
from typing import cast
from pathlib import Path


def build_requirements(root: Path) -> str:
    """Validate runtime dependency strings and render the ComfyUI installation requirements."""
    document = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    raw_dependencies: object = document["project"]["dependencies"]
    if not isinstance(raw_dependencies, list):
        message = "List runtime dependencies in pyproject.toml."
        raise TypeError(message)
    dependencies: list[str] = []
    for dependency in cast("list[object]", raw_dependencies):
        if (
            not isinstance(dependency, str)
            or not dependency.strip()
            or any(character in dependency for character in "\r\n\0")
        ):
            message = "List each runtime dependency as one nonempty string."
            raise ValueError(message)
        dependencies.append(dependency)
    return "# Generated from pyproject.toml by mise run repo:deps:export.\n" + "".join(
        f"{dependency}\n" for dependency in dependencies
    )


def main() -> int:
    """Export runtime requirements or report whether the generated file is current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / "requirements.txt"
    requirements_text = build_requirements(root)
    if arguments.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != requirements_text:
            sys.stdout.write("Update requirements.txt with mise run repo:deps:export." + "\n")
            return 1
    else:
        destination.write_text(requirements_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
