"""The private state folder, its files and their size limits, and the environment variables that move them."""

# An absolute folder that replaces the platform's own state folder.
STATE_DIRECTORY_VARIABLE = "OPENROUTER_COMFY_STATE_DIRECTORY"
# The key in the server's environment, which takes precedence over the saved key.
KEY_VARIABLE = "OPENROUTER_API_KEY"
# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAME = "OpenRouterComfyUI"
XDG_STATE_FOLDER_NAME = "openrouter-comfy"
PRIVATE_FOLDER_MODE = 0o700
TEMPORARY_PREFIX = ".openrouter-"
SETTINGS_FILE_NAME = "settings.json"
CREDENTIAL_FILE_NAME = "credential"
MAX_SETTINGS_FILE_BYTES = 65_536
JOB_FOLDER_NAME = "jobs"
JOB_FILE_SUFFIX = ".json"
# An uncertain submission is recorded under this prefix and its request hash, since it has no job ID.
UNCERTAIN_PREFIX = "uncertain-"
MAX_LISTED_JOBS = 100
MAX_JOB_FILE_BYTES = 16_384

__all__ = [
    "CREDENTIAL_FILE_NAME",
    "JOB_FILE_SUFFIX",
    "JOB_FOLDER_NAME",
    "KEY_VARIABLE",
    "MAX_JOB_FILE_BYTES",
    "MAX_LISTED_JOBS",
    "MAX_SETTINGS_FILE_BYTES",
    "PRIVATE_FOLDER_MODE",
    "SETTINGS_FILE_NAME",
    "STATE_DIRECTORY_VARIABLE",
    "STATE_FOLDER_NAME",
    "TEMPORARY_PREFIX",
    "UNCERTAIN_PREFIX",
    "XDG_STATE_FOLDER_NAME",
]
