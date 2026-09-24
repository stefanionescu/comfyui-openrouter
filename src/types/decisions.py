"""Decision questions, answers, and requests; each question and answer kind is its own record."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from . import Json
    from .options import Options
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class ChoiceQuestion:
    """A question whose answer is one of several named options.

    Attributes:
        name: The question's name, which its answer carries.
        instructions: What the question asks.
        options: (key, description) pairs; an empty description sends none.

    """

    name: str
    instructions: str
    options: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class YesNoQuestion:
    """A question answered with the probability of yes.

    Attributes:
        name: The question's name, which its answer carries.
        instructions: What the question asks.
        yes_means: When the answer is yes, or empty.
        no_means: When the answer is no, or empty.

    """

    name: str
    instructions: str
    yes_means: str
    no_means: str


@dataclass(frozen=True, slots=True)
class ScoreQuestion:
    """A question answered with a position on ordered levels.

    Attributes:
        name: The question's name, which its answer carries.
        instructions: What the question asks.
        levels: The levels, lowest first.

    """

    name: str
    instructions: str
    levels: tuple[str, ...]


type Question = ChoiceQuestion | YesNoQuestion | ScoreQuestion


@dataclass(frozen=True, slots=True)
class QuestionSet:
    """The questions of one decision, in the order they were added.

    Attributes:
        questions: The questions.

    """

    questions: tuple[Question, ...]


@dataclass(frozen=True, slots=True)
class ChoiceAnswer:
    """The answer to a choice question.

    Attributes:
        name: The question's name.
        choice: The chosen key.
        confidence: How sure the model is.
        probabilities: The probability of every key.

    """

    name: str
    choice: str
    confidence: float
    probabilities: Mapping[str, float]


@dataclass(frozen=True, slots=True)
class YesNoAnswer:
    """The answer to a yes-or-no question.

    Attributes:
        name: The question's name.
        probability: The probability of yes.

    """

    name: str
    probability: float


@dataclass(frozen=True, slots=True)
class ScoreAnswer:
    """The answer to a score question.

    Attributes:
        name: The question's name.
        score: The probability-weighted level position, from 0 to the number of levels minus 1.
        confidence: How sure the model is.
        probabilities: The probability of every level, keyed by position.
        legend: Each level's text, keyed by position.

    """

    name: str
    score: float
    confidence: float
    probabilities: Mapping[str, float]
    legend: Mapping[str, str]


type Answer = ChoiceAnswer | YesNoAnswer | ScoreAnswer


@dataclass(frozen=True, slots=True)
class AnswerSet:
    """The answers of one decision, in question order.

    Attributes:
        answers: The answers.

    """

    answers: tuple[Answer, ...]


@dataclass(frozen=True, slots=True)
class DecisionRequest:
    """One decision request.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        state: The situation, as text or JSON.
        questions: The questions to answer.
        options: Provider routing and extra fields.

    """

    model_id: str
    state: Json
    questions: QuestionSet
    options: Options | None


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = [
    "AnswerSet",
    "ChoiceAnswer",
    "ChoiceQuestion",
    "DecisionRequest",
    "QuestionSet",
    "ScoreAnswer",
    "ScoreQuestion",
    "YesNoAnswer",
    "YesNoQuestion",
]
