"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = "OpenRouter"

# The menu headings the nodes are grouped under.
MENUS = {
    "SHARED": "OpenRouter",
    "CHAT": "OpenRouter/Chat",
    "IMAGE": "OpenRouter/Image",
    "VIDEO": "OpenRouter/Video",
    "AUDIO": "OpenRouter/Audio",
    "SEARCH": "OpenRouter/Search",
    "DECISION": "OpenRouter/Decision",
}

# The socket types more than one node shares.
SOCKET_TYPES = {
    "OPTIONS": "REQUEST_OPTIONS",
    "DOCUMENTS": "CHAT_DOCUMENTS",
    "CONVERSATION": "CHAT_CONVERSATION",
    "QUESTIONS": "DECISION_QUESTIONS",
    "ANSWERS": "DECISION_ANSWERS",
}

__all__ = [
    "MENUS",
    "NODE_PREFIX",
    "SOCKET_TYPES",
]
