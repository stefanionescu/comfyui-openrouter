"""Decision answer types and the answer threshold."""

# The threshold at which a probability or confidence counts as yes.
THRESHOLD = {
    "DEFAULT": 0.5,
    "STEP": 0.01,
}

# The answer type dropdown's input name and its choices.
ANSWER_TYPES = {
    "INPUT": "answer_type",
    "YES_NO": "yes or no",
    "CHOICE": "one choice",
    "SCORE": "score",
}

__all__ = [
    "ANSWER_TYPES",
    "THRESHOLD",
]
