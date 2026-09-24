"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name; the menu groups them under these headings.
NODE_PREFIX = "OpenRouter"
SHARED_MENU = "OpenRouter"
CHAT_MENU = "OpenRouter/Chat"
IMAGE_MENU = "OpenRouter/Image"
VIDEO_MENU = "OpenRouter/Video"
AUDIO_MENU = "OpenRouter/Audio"
SEARCH_MENU = "OpenRouter/Search"
DECISION_MENU = "OpenRouter/Decision"

# The socket types more than one node shares.
OPTIONS_TYPE = "REQUEST_OPTIONS"
DOCUMENTS_TYPE = "CHAT_DOCUMENTS"
CONVERSATION_TYPE = "CHAT_CONVERSATION"
QUESTIONS_TYPE = "DECISION_QUESTIONS"
ANSWERS_TYPE = "DECISION_ANSWERS"

__all__ = [
    "ANSWERS_TYPE",
    "AUDIO_MENU",
    "CHAT_MENU",
    "CONVERSATION_TYPE",
    "DECISION_MENU",
    "DOCUMENTS_TYPE",
    "IMAGE_MENU",
    "NODE_PREFIX",
    "OPTIONS_TYPE",
    "QUESTIONS_TYPE",
    "SEARCH_MENU",
    "SHARED_MENU",
    "VIDEO_MENU",
]
