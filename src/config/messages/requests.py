"""Messages for rejected local HTTP requests."""

CLEAR_KEY_BODY = "Send no content when clearing the saved key."
JSON_DEPTH = "The request is nested too deeply."
JSON_DUPLICATE_KEY = "The request repeats a field name."
JSON_MAPPING = "Send a JSON object."
JSON_SIZE = "The request is too large."
JSON_SYNTAX = "The request is not valid JSON."
JSON_TYPE = "Send the request as application/json."
JSON_VALUES = "The request holds values JSON cannot carry."
LOCAL_CONNECTION_REQUIRED = "OpenRouter settings require a local, same-origin ComfyUI connection."
REQUEST_TIMEOUT = "The request took too long to arrive."
SETTINGS_REVISION_REQUIRED = "Send the settings revision you read together with the changed settings."
SINGLE_KEY_REQUIRED = "Send one api_key text field."

__all__ = [
    "CLEAR_KEY_BODY",
    "JSON_DEPTH",
    "JSON_DUPLICATE_KEY",
    "JSON_MAPPING",
    "JSON_SIZE",
    "JSON_SYNTAX",
    "JSON_TYPE",
    "JSON_VALUES",
    "LOCAL_CONNECTION_REQUIRED",
    "REQUEST_TIMEOUT",
    "SETTINGS_REVISION_REQUIRED",
    "SINGLE_KEY_REQUIRED",
]
