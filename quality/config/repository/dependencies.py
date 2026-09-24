"""Dependency ownership policy."""

PROJECT_METADATA_FILE = "pyproject.toml"
LOCK_FILE = "uv.lock"
PROJECT_PACKAGE_NAME = "comfyui-openrouter"
RUNTIME_EXTRAS: tuple[str, ...] = ()
DEV_DEPENDENCY_GROUP = "dev"

PROJECT_SECTION = "project"
OPTIONAL_DEPENDENCIES_SECTION = "optional-dependencies"
DEPENDENCY_GROUPS_SECTION = "dependency-groups"
LOCK_PACKAGE_SECTION = "package"
PACKAGE_NAME_FIELD = "name"

ROOT_REQUIREMENTS_GLOB = "requirements*.txt"
EXPORT_TASK = ".mise/tasks/repo/deps/export"
EXPORT_SCAN_ROOTS = (
    ".mise/tasks",
    "scripts",
)
INSTALL_COMMAND_SCAN_ROOTS = (".mise/tasks", ".githooks", "scripts", "quality/security")

REQUIREMENTS_EXPORT_COMMAND = "uv pip compile"
DIRECT_PIP_INSTALL_PATTERN = r"(^|[\s;&|({])(?:python[0-9.]*\s+-m\s+)?pip\s+install\b"
UV_PIP_INSTALL = "uv pip install"
UV_PIP_WRAPPER = "uv_run pip install"
ALLOWED_UV_PIP_PATHS: tuple[str, ...] = ()

POLICY_FILE_SUFFIXES = {".sh", ".py", ".md", ".toml"}
POLICY_FILE_NAMES: tuple[str, ...] = ()
POLICY_FILE_IGNORED_PARTS = {".git", ".venv", "node_modules", ".artifacts"}

EXPORT_MODULE = "scripts.dependencies"
