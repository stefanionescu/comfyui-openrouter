"""Messages for the saved model list, its refresh, rollback, and automatic check."""

AUTOMATIC_CHECK_FAILED = "The automatic model check could not reach OpenRouter. Refresh Models to try now."
MODEL_LIST_CHANGED = "The model list changed in another window. Reopen OpenRouter models and try again."
MODEL_LIST_FORMAT = "OpenRouter's model list had an unexpected format, so the saved list was kept."
MODEL_LIST_GROWTH = (
    "OpenRouter's model list grew more than expected in one refresh, so the saved list was kept. Try again later."
)
MODEL_LIST_INCOMPLETE = (
    "OpenRouter's model list was much shorter than the saved one, so the saved list was kept. Try again later."
)
MODEL_REFRESH_RUNNING = "A model refresh is already running. Wait for it to finish."
MODEL_REFRESH_WAIT = "Wait for the model refresh to finish before restoring the previous list."
MODEL_REVISION_REQUIRED = "Send the model list revision you read."
MODEL_ROLLBACK_EMPTY = "There is no previous model list to restore."
MODEL_UNKNOWN = "Choose a model ID from the list or type one in the form author/model."
MODELS_HTTP = "OpenRouter's model list returned HTTP {status}. Try again later."
MODELS_UNREADABLE = "OpenRouter's model list could not be read. Check the connection and try again."
REFRESH_BODY = "Send no content when refreshing the model list."

__all__ = [
    "AUTOMATIC_CHECK_FAILED",
    "MODELS_HTTP",
    "MODELS_UNREADABLE",
    "MODEL_LIST_CHANGED",
    "MODEL_LIST_FORMAT",
    "MODEL_LIST_GROWTH",
    "MODEL_LIST_INCOMPLETE",
    "MODEL_REFRESH_RUNNING",
    "MODEL_REFRESH_WAIT",
    "MODEL_REVISION_REQUIRED",
    "MODEL_ROLLBACK_EMPTY",
    "MODEL_UNKNOWN",
    "REFRESH_BODY",
]
