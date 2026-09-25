"""The private state folder, its files and their size limits, and the environment variables that move them."""

# The key in the server's environment, which takes precedence over the saved key, and an absolute folder that
# replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    "KEY": "OPENROUTER_API_KEY",
    "STATE_DIRECTORY": "OPENROUTER_COMFY_STATE_DIRECTORY",
}

# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAMES = {
    "DEFAULT": "OpenRouterComfyUI",
    "XDG": "openrouter-comfy",
}

# Only the folder's owner may open it.
PRIVATE_FOLDER_MODE = 0o700

# A file is written under this prefix, then moved into place.
TEMPORARY_PREFIX = ".openrouter-"

# The settings and the saved key.
FILE_NAMES = {
    "SETTINGS": "settings.json",
    "CREDENTIAL": "credential",
}

# The video job records. An uncertain submission is recorded under the uncertain prefix and its request hash,
# since it has no job ID.
JOB_FILES = {
    "FOLDER": "jobs",
    "SUFFIX": ".json",
    "UNCERTAIN_PREFIX": "uncertain-",
}

# The largest settings file and job record the extension reads.
MAX_FILE_BYTES = {
    "SETTINGS": 65_536,
    "JOB": 16_384,
}

__all__ = [
    "ENVIRONMENT_VARIABLES",
    "FILE_NAMES",
    "JOB_FILES",
    "MAX_FILE_BYTES",
    "PRIVATE_FOLDER_MODE",
    "STATE_FOLDER_NAMES",
    "TEMPORARY_PREFIX",
]
