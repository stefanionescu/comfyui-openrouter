"""Messages for the model check that runs before a request is sent."""

MODEL_EMPTY = "Type a model ID from openrouter.ai/models."
MODEL_KIND = "{model} does not take {kind} requests. Find one that does at openrouter.ai/models."
MODEL_UNKNOWN = "OpenRouter has no model named {model}. Copy the ID from openrouter.ai/models."

__all__ = ["MODEL_EMPTY", "MODEL_KIND", "MODEL_UNKNOWN"]
