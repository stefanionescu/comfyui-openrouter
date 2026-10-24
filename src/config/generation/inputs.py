"""Names of the inputs every paid node shares, and of the choice that sends nothing."""

# The inputs every paid node shares.
INPUT_NAMES = {
    "MODEL": "model",
    "SEED": "seed",
    "RUN_NUMBER": "run_number",
    "OPTIONS": "options",
}

# The model input's tooltip.
MODEL_TOOLTIP = "Any OpenRouter model ID. Copy one from openrouter.ai/models."

# Every dropdown's choice that sends nothing and leaves the value to the model.
MODEL_DEFAULT = "default"

# A default or custom dropdown's choice that shows a value, and the name of that value.
VALUE_CHOICE = {
    "SET": "custom",
    "VALUE": "value",
}

# The seed's default, and its largest value: OpenRouter refuses a seed of 2**31 or more.
SEED = {
    "DEFAULT": 42,
    "MAX": 2**31 - 1,
}

# The run number is the extension's own cache counter.
RUN_NUMBER = {
    "DEFAULT": 0,
    "MIN": 0,
    "MAX": 2**31 - 1,
}

__all__ = [
    "INPUT_NAMES",
    "MODEL_DEFAULT",
    "MODEL_TOOLTIP",
    "RUN_NUMBER",
    "SEED",
    "VALUE_CHOICE",
]
