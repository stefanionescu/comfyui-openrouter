"""Messages for the model check that runs before a request is sent."""

MODEL_COUNT = "{model} takes a count of at most {maximum}. Lower count, or choose a model that makes more."

MODEL_EMPTY = "Type a model ID from openrouter.ai/models."

MODEL_FIELD = "{model} does not take {field}. Leave it unset, or choose a model that takes it."

MODEL_FRAME = "{model} does not take a {frame}. Disconnect it, or choose a model that does."

MODEL_INPUT = "{model} does not read {kind}. Disconnect it, or choose a model that does at openrouter.ai/models."

MODEL_KIND = "{model} does not take {kind} requests. Find one that does at openrouter.ai/models."

MODEL_OUTPUT = "{model} does not make {kind}. Set outputs to text, or choose a model that does."

MODEL_RANGE = "{model} takes {field} from {minimum} to {maximum}."

MODEL_SCHEMA = "{model} cannot follow an answer schema. Clear the answer schema, or choose a model that can."

MODEL_TOKENS = "{model} answers with at most {maximum} tokens. Set max tokens to {maximum} or less, or to 0."

MODEL_UNKNOWN = "OpenRouter has no model named {model}. Copy the ID from openrouter.ai/models."

MODEL_VALUE = "{model} takes {field} {values}. Choose one of them, or the model's default."

MODEL_VOICE = "{model} cannot copy a voice. Disconnect the voice sample, or choose a model that clones voices."

__all__ = [
    "MODEL_COUNT",
    "MODEL_EMPTY",
    "MODEL_FIELD",
    "MODEL_FRAME",
    "MODEL_INPUT",
    "MODEL_KIND",
    "MODEL_OUTPUT",
    "MODEL_RANGE",
    "MODEL_SCHEMA",
    "MODEL_TOKENS",
    "MODEL_UNKNOWN",
    "MODEL_VALUE",
    "MODEL_VOICE",
]
