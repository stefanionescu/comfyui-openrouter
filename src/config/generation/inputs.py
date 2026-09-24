"""Names of the inputs every paid node shares, and of the choice that sends nothing."""

MODEL_INPUT = "model"
MODEL_TOOLTIP = "Any OpenRouter model ID. Copy one from openrouter.ai/models."
# Every dropdown's choice that sends nothing and leaves the value to the model.
MODEL_DEFAULT = "model default"
SEED_INPUT = "seed"
# Changing the run number sends the same request again.
RUN_NUMBER_INPUT = "run_number"
OPTIONS_INPUT = "options"
DEFAULT_SEED = 42
MAX_SEED = 2**32 - 1
DEFAULT_RUN_NUMBER = 0
MIN_RUN_NUMBER = 0
MAX_RUN_NUMBER = 2**31 - 1

__all__ = [
    "DEFAULT_RUN_NUMBER",
    "DEFAULT_SEED",
    "MAX_RUN_NUMBER",
    "MAX_SEED",
    "MIN_RUN_NUMBER",
    "MODEL_DEFAULT",
    "MODEL_INPUT",
    "MODEL_TOOLTIP",
    "OPTIONS_INPUT",
    "RUN_NUMBER_INPUT",
    "SEED_INPUT",
]
