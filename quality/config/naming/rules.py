"""Naming rule runner policy."""

from quality.config.repository.paths import PYTHON_SOURCE_DIRS

SINGLE_FILE_SOURCE_ROOTS = {
    "src",
    "scripts",
    "quality",
}

SCOPE_SOURCE_DIRS = {
    "all": PYTHON_SOURCE_DIRS,
    "python": PYTHON_SOURCE_DIRS,
    "quality": ("quality",),
    "src": ("src",),
    "scripts": ("scripts",),
}

PYTHON_SCOPES = {
    "all",
    "python",
    "quality",
    "src",
    "scripts",
    "staged",
}

SHELL_SCOPES = {
    "all",
    "shell",
    "hooks",
    "mise",
    "quality",
    "scripts",
    "staged",
}

DIGIT_CHECK_CATEGORIES = {
    "directories",
    "files",
}

VAGUE_SCRIPT_NAMES = {
    "common",
    "helper",
    "helpers",
    "utils",
    "util",
}
