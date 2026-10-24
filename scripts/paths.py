"""The repository folders and files the build scripts read and write."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = REPO_ROOT / 'web'
HELP_DIR = WEB_DIR / 'docs'
EXAMPLES_DIR = REPO_ROOT / 'example_workflows'
# ComfyUI lists each file here as a subgraph blueprint in its node library, named after the file.
SUBGRAPHS_DIR = REPO_ROOT / 'subgraphs'
README_PATH = REPO_ROOT / 'README.md'
# The script the checks run in ComfyUI's interpreter: it loads ComfyUI on the CPU, then runs the schema export.
EXPORT_SCRIPT_PATH = REPO_ROOT / 'scripts' / 'nodes' / 'export.py'
# The check builds the browser files here and compares them with the shipped ones.
FRONTEND_CHECK_DIR = REPO_ROOT / '.artifacts' / 'frontend'

__all__ = [
    'EXAMPLES_DIR',
    'EXPORT_SCRIPT_PATH',
    'FRONTEND_CHECK_DIR',
    'HELP_DIR',
    'README_PATH',
    'REPO_ROOT',
    'SUBGRAPHS_DIR',
    'WEB_DIR',
]
