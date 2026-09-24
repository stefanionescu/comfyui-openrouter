"""Check connector types against the selected ComfyUI installation."""

from __future__ import annotations

import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from quality.lib.output import write_error
from quality.lib.comfy import host_installation
from quality.lib.json_config import require_string_list
from quality.lib.process import ProcessContext, run_command


def host_paths() -> list[str]:
    """Read dependency paths from the actual host interpreter without importing ComfyUI."""
    host, interpreter = host_installation()
    result = run_command(
        [
            str(interpreter),
            "-I",
            "-c",
            "import json, sysconfig; print(json.dumps([sysconfig.get_path('purelib'), sysconfig.get_path('platlib')]))",
        ],
        is_failure_raised=True,
        is_output_captured=True,
        context=ProcessContext(timeout_seconds=10),
    )
    packages = require_string_list(json.loads(result.stdout), "ComfyUI package directories", is_nonempty=True)
    if not all(Path(item).is_dir() for item in packages):
        msg = "ComfyUI's Python did not report valid package directories."
        raise ValueError(msg)
    return list(dict.fromkeys([str(host), *packages]))


def main() -> int:
    """Run the strict project with actual host dependencies and remove its temporary configuration."""
    root = Path.cwd()
    try:
        search_paths = [str(root), *host_paths()]
        with TemporaryDirectory(prefix="comfyui-openrouter-types-") as temporary:
            configuration = Path(temporary) / "pyrightconfig.json"
            configuration.write_text(
                json.dumps(
                    {
                        "extends": str(root / "pyrightconfig.json"),
                        "extraPaths": search_paths,
                        "executionEnvironments": [
                            {"root": str(root / "quality"), "extraPaths": [str(root)]},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            return run_command(
                ["basedpyright", "--project", str(configuration), *sys.argv[1:]],
                context=ProcessContext(working_directory=root),
            ).return_code
    except (OSError, ValueError, RuntimeError) as error:
        write_error(f"Python type check could not start: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
