"""Repository path policy for quality tooling."""

LICENSE_POLICY_FILE = "quality/config/repository/licenses/policy.json"

PYTHON_SOURCE_DIRS = ("__init__.py", "src", "scripts", "quality")
PYTHON_RUNTIME_DIRS = ("__init__.py", "src")
SHELL_SOURCE_DIRS = (".githooks", ".mise/tasks", "quality")
CONFIG_SOURCE_DIRS = ("src/config", "quality/config")

SHELL_TASK_PREFIXES = (
    ".mise/tasks/",
    ".githooks/",
)

SHELL_SCOPE_PREFIXES = {
    "all": ("",),
    "shell": ("quality/",),
    "hooks": (".githooks/",),
    "mise": (".mise/tasks/",),
    "quality": ("quality/",),
}

QUALITY_EXCLUDED_DIRS = {
    ".artifacts",
    ".cache",
    ".git",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}

FUNCTION_POLICY_EXCLUDED_DIRS = {
    ".artifacts",
    ".git",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}
