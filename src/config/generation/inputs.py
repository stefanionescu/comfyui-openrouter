"""Names of the inputs every paid node shares, and of the choice that sends nothing."""

MODEL_INPUT = "model"
MODEL_ID_INPUT = "model_id"
# The dropdown option where any model ID can be written instead of chosen.
WRITTEN_CHOICE = "other model ID"
# Every endpoint's choice that sends nothing and leaves the value to the model.
MODEL_DEFAULT = "model default"
SEED_INPUT = "seed"
# The run number: changing it sends the same request again.
VARIATION_INPUT = "variation"
OPTIONS_INPUT = "options"
DEFAULT_SEED = 42
MAX_SEED = 2**32 - 1
DEFAULT_VARIATION = 0
MIN_VARIATION = 0
MAX_VARIATION = 2**31 - 1

__all__ = [
    "DEFAULT_SEED",
    "DEFAULT_VARIATION",
    "MAX_SEED",
    "MAX_VARIATION",
    "MIN_VARIATION",
    "MODEL_DEFAULT",
    "MODEL_ID_INPUT",
    "MODEL_INPUT",
    "OPTIONS_INPUT",
    "SEED_INPUT",
    "VARIATION_INPUT",
    "WRITTEN_CHOICE",
]
