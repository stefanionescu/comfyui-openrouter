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

# The socket types more than one node shares, prefixed so they cannot match another pack's types.
SOCKET_TYPES = {
    "OPTIONS": "OPENROUTER_REQUEST_OPTIONS",
    "DOCUMENTS": "OPENROUTER_CHAT_DOCUMENTS",
    "CONVERSATION": "OPENROUTER_CHAT_CONVERSATION",
    "QUESTIONS": "OPENROUTER_DECISION_QUESTIONS",
    "ANSWERS": "OPENROUTER_DECISION_ANSWERS",
}

__all__ = [
    "MENUS",
    "NODE_PREFIX",
    "SOCKET_TYPES",
]
