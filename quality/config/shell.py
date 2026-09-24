"""Shell quality threshold constants."""

BASH_SHEBANGS = (
    "#!/usr/bin/env bash",
    "#!/bin/bash",
)

SHELL_MAX_FILE_LINES = 140
SHELL_MAX_FUNCTION_LINES = 40
SHELL_MAX_FUNCTION_BRANCHES = 8
SHELL_MAX_FUNCTION_NESTING = 3
SHELL_MAX_MUTABLE_ASSIGNMENTS = 8
SHELL_DUPLICATE_MIN_LINES = 3
SHELL_DUPLICATE_MIN_MATCHES = 2
BASH_PREFIX_COLLISION_THRESHOLD = 2
SHELL_CONFIG_GUARD_PATTERN = r"^\[\[ -n \$\{(?P<name>_CFG_[A-Z][A-Z0-9_]*_READY):-\} \]\] && return 0$"

SHELL_ARCHITECTURE_PREFIXES = (".mise/tasks/", ".githooks/", "quality/")

SHELL_ACTION_PREFIXES = {
    "acquire",
    "apply",
    "await",
    "build",
    "check",
    "choose",
    "cleanup",
    "clear",
    "detect",
    "export",
    "finalize",
    "get",
    "guard",
    "handle",
    "init",
    "install",
    "kill",
    "launch",
    "normalize",
    "parse",
    "prepare",
    "push",
    "read",
    "reconfigure",
    "require",
    "run",
    "select",
    "set",
    "setup",
    "show",
    "start",
    "stop",
    "validate",
    "wipe",
    "write",
}

SHELL_BASH_4_PATTERNS = (
    (r"\b(?:mapfile|readarray)\b", "mapfile and readarray require Bash 4"),
    (r"\bdeclare\s+-A\b", "associative arrays require Bash 4"),
    (r"\$\{[^}\n]+(?:,,|\^\^)\}", "case-conversion expansion requires Bash 4"),
    (r"\b(?:coproc|wait\s+-n)\b", "command requires Bash 4 or newer"),
)

BASH_PREFIX_ALLOWLIST = {
    ".githooks": ("pre",),
    ".mise/tasks/repo/hook": ("pre",),
}

ALLOWED_DEFAULT_FRAGMENTS = (
    "MISE_PROJECT_ROOT:-",
    "PYTHONPATH:-",
    "SKIP_",
    "RUN_",
    "${1:-}",
    "${2:-}",
)

SHELL_CONFIG_PREFIXES = ("quality/config/",)

RUNTIME_EMBED_RULES = (
    (r"\bpython[0-9.]*\s+-c\b", "inline Python commands are not allowed"),
    (r"\bpython[0-9.]*\s+(?:-\s*)?<<", "inline Python heredocs are not allowed"),
    (
        r"(?:\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|\"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?\")\s+-\s*<<",
        "variable Python heredocs are not allowed",
    ),
    (r"\bnode\s+-e\b", "inline Node commands are not allowed"),
    (r"\bnode\s+<<", "inline Node heredocs are not allowed"),
    (r"\bcat\s+>[^<]+<<", "generated script heredocs are not allowed"),
)

RUNTIME_EMBED_FILES: tuple[str, ...] = ()

RUNTIME_EMBED_GLOBAL_SCOPES = (
    "all",
    "shell",
)

ALLOWED_SCRIPT_ROOT_FOLDERS = {
    ".",
    ".githooks",
}

ALLOWED_SINGLE_SCRIPT_FOLDERS = {
    # Repository setup/check tasks share their explicit task root.
    ".mise/tasks/repo",
    # The help pages are written by hand, so their check has no build task beside it.
    ".mise/tasks/comfy/nodes",
    # These shell entrypoints share their owner with JavaScript policy or filtering code.
    "quality/config/repository/licenses",
    "quality/repository/licenses",
    ".mise/tasks/repo/licenses",
    ".mise/tasks/repo/security",
    ".mise/tasks/repo/links",
    "quality/config/security/bearer",
    "quality/config/security/codeql/frontend",
    "quality/config/security/gitleaks",
    "quality/config/security/osv",
    "quality/config/security/semgrep",
    "quality/repository/hooks",
    "quality/security/bandit",
    "quality/security/bearer",
    "quality/security/codeql/python",
    "quality/security/codeql",
    "quality/security/gitleaks",
    "quality/security/osv",
    "quality/security/pip-audit",
    "quality/security/semgrep",
}
