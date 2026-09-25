"""Messages for private settings, keys, and state storage."""

KEY_EMPTY = "Enter an OpenRouter API key of 1 to {maximum} characters without spaces at either end."

KEY_REQUIRED = (
    "Set your OpenRouter API key in OpenRouter settings or in the server's OPENROUTER_API_KEY before running."
)

KEY_UNREADABLE = "The saved OpenRouter key could not be read. Save the key again in OpenRouter settings."

KEY_WHITESPACE = "Remove spaces and line breaks from the OpenRouter API key."

PRIVATE_STATE_LOCATION = "Keep OpenRouter's private state outside ComfyUI, its package, and its media folders."

RUNTIME_NOT_READY = "The OpenRouter nodes are still loading. Wait for ComfyUI to finish starting, then run again."

SETTINGS_CHANGED = "The settings changed in another window. Reload the settings and try again."

SETTINGS_RANGE = "Choose each OpenRouter setting within its range."

SETTINGS_UNREADABLE = "OpenRouter's private settings could not be read. Check the state folder's permissions."

SETTINGS_WHOLE_NUMBERS = "Enter whole numbers for the OpenRouter settings."

SETTING_READ_ONLY = "That OpenRouter setting cannot be changed here."

SETTING_UNKNOWN = "OpenRouter's settings file has an unknown setting. Remove it or reset the settings."

STATE_DIRECTORY_ABSOLUTE = "Set OPENROUTER_COMFY_STATE_DIRECTORY to an absolute folder path."

STATE_FILE_SIZE = "An OpenRouter state file is larger than expected. Check the state folder."

STATE_UNREADABLE = "OpenRouter's private state could not be read or written. Check the state folder's permissions."

__all__ = [
    "KEY_EMPTY",
    "KEY_REQUIRED",
    "KEY_UNREADABLE",
    "KEY_WHITESPACE",
    "PRIVATE_STATE_LOCATION",
    "RUNTIME_NOT_READY",
    "SETTINGS_CHANGED",
    "SETTINGS_RANGE",
    "SETTINGS_UNREADABLE",
    "SETTINGS_WHOLE_NUMBERS",
    "SETTING_READ_ONLY",
    "SETTING_UNKNOWN",
    "STATE_DIRECTORY_ABSOLUTE",
    "STATE_FILE_SIZE",
    "STATE_UNREADABLE",
]
