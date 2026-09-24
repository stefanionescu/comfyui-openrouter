"""Decision question limits, answer types, and the default answer threshold."""

MAX_QUESTIONS = 32
MIN_CHOICE_OPTIONS = 2
MAX_CHOICE_OPTIONS = 32
MIN_SCORE_LEVELS = 2
# TypeSafe's decisions API accepts 2 to 10 score levels.
MAX_SCORE_LEVELS = 10
# Keeps the situation well inside Jev's 32,000-token context, at about four characters per token.
MAX_SITUATION_CHARACTERS = 200_000
DEFAULT_THRESHOLD = 0.5
THRESHOLD_STEP = 0.01
ANSWER_TYPE_INPUT = "answer_type"
YES_NO_ANSWER = "yes or no"
CHOICE_ANSWER = "one choice"
SCORE_ANSWER = "score"

__all__ = [
    "ANSWER_TYPE_INPUT",
    "CHOICE_ANSWER",
    "DEFAULT_THRESHOLD",
    "MAX_CHOICE_OPTIONS",
    "MAX_QUESTIONS",
    "MAX_SCORE_LEVELS",
    "MAX_SITUATION_CHARACTERS",
    "MIN_CHOICE_OPTIONS",
    "MIN_SCORE_LEVELS",
    "SCORE_ANSWER",
    "THRESHOLD_STEP",
    "YES_NO_ANSWER",
]
