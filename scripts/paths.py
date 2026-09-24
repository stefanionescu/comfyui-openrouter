"""The repository folders and files the build scripts read and write."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = REPO_ROOT / "web"
HELP_DIR = WEB_DIR / "docs"
EXAMPLES_DIR = REPO_ROOT / "example_workflows"
README_PATH = REPO_ROOT / "README.md"
SCHEMA_SCRIPT_PATH = REPO_ROOT / "scripts" / "nodes" / "schema.py"
# The check builds the browser files here and compares them with the shipped ones.
FRONTEND_CHECK_DIR = REPO_ROOT / ".artifacts" / "frontend"

__all__ = [
    "EXAMPLES_DIR",
    "FRONTEND_CHECK_DIR",
    "HELP_DIR",
    "README_PATH",
    "REPO_ROOT",
    "SCHEMA_SCRIPT_PATH",
    "WEB_DIR",
]
