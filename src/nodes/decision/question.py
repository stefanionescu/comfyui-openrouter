"""Add one question of any answer type to a decision's question list."""

from __future__ import annotations

import re
from comfy_api.latest import io
from typing import override, TYPE_CHECKING
from ...config.patterns import QUESTION_NAME_PATTERN
from ...types.errors import ErrorCode, OpenRouterError
from ...config.generation.decisions import ANSWER_TYPES
from ...config.namespace import NODE_PREFIX, MENUS, SOCKET_TYPES
from ...types.decisions import QuestionSet, ScoreQuestion, YesNoQuestion, ChoiceQuestion
from ...config.messages.inputs import (
    SCORE_LEVELS,
    QUESTION_NAME,
    CHOICE_OPTIONS,
    YES_NO_CRITERIA,
    QUESTION_REPEATED,
    QUESTION_INSTRUCTIONS,
    CHOICE_OPTION_REPEATED,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ...types.decisions import Question

QUESTION_NAME_TEXT = re.compile(QUESTION_NAME_PATTERN)


def _build_choice(name: str, instructions: str, text: str) -> ChoiceQuestion:
    """Read one key: description per line; a line without a colon is a key with no description."""
    options: list[tuple[str, str]] = []
    for line in (line.strip() for line in text.splitlines()):
        if not line:
            continue
        key, _separator, description = line.partition(":")
        if any(key.strip() == known for known, _description in options):
            raise OpenRouterError(ErrorCode.INVALID_INPUT, CHOICE_OPTION_REPEATED.format(key=key.strip()))
        options.append((key.strip(), description.strip()))
    if not options or not all(key for key, _text in options):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, CHOICE_OPTIONS)
    return ChoiceQuestion(name, instructions, tuple(options))


def _build_question(name: str, instructions: str, answer_type: Mapping[str, object]) -> Question:
    """Build the question of the chosen answer type from the fields that type shows."""
    kind = str(answer_type[ANSWER_TYPES["INPUT"]])
    if kind == ANSWER_TYPES["CHOICE"]:
        return _build_choice(name, instructions, str(answer_type.get("options", "")))
    if kind == ANSWER_TYPES["SCORE"]:
        levels = tuple(line.strip() for line in str(answer_type.get("levels", "")).splitlines() if line.strip())
        if not levels:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, SCORE_LEVELS)
        return ScoreQuestion(name, instructions, levels)
    yes_means, no_means = str(answer_type.get("yes_means", "")).strip(), str(answer_type.get("no_means", "")).strip()
    if bool(yes_means) != bool(no_means):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, YES_NO_CRITERIA)
    return YesNoQuestion(name, instructions, yes_means, no_means)


class DecisionAddQuestion(io.ComfyNode):
    """Append one question to the question list; chain several to ask more."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Show only the fields the chosen answer type needs, with yes or no first as the default."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Decision: Add Question",
            category=MENUS["DECISION"],
            description="Add one question for a decision model: yes or no, one choice, or a score.",
            inputs=[
                io.Custom(SOCKET_TYPES["QUESTIONS"]).Input(
                    "questions",
                    optional=True,
                    tooltip="Connect another Decision: Add Question to ask several questions at once.",
                ),
                io.String.Input(
                    "name",
                    default="question",
                    tooltip="Lowercase letters, digits, and underscores; Decision: Read Answer finds the answer by it.",
                ),
                io.DynamicCombo.Input(
                    ANSWER_TYPES["INPUT"],
                    display_name="answer type",
                    options=[
                        io.DynamicCombo.Option(
                            ANSWER_TYPES["YES_NO"],
                            [
                                io.String.Input("yes_means", display_name="yes means", default=""),
                                io.String.Input("no_means", display_name="no means", default=""),
                            ],
                        ),
                        io.DynamicCombo.Option(
                            ANSWER_TYPES["CHOICE"],
                            [
                                io.String.Input(
                                    "options",
                                    multiline=True,
                                    default="",
                                    tooltip="One option per line, as key: description.",
                                )
                            ],
                        ),
                        io.DynamicCombo.Option(
                            ANSWER_TYPES["SCORE"],
                            [
                                io.String.Input(
                                    "levels", multiline=True, default="", tooltip="One level per line, lowest first."
                                )
                            ],
                        ),
                    ],
                    tooltip="Yes or no gives a probability, one choice picks an option, and score places it on levels.",
                ),
                io.String.Input("instructions", multiline=True, default="", tooltip="What to decide."),
            ],
            outputs=[io.Custom(SOCKET_TYPES["QUESTIONS"]).Output("questions", display_name="questions")],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        name: str,
        instructions: str,
        answer_type: dict[str, object],
        questions: QuestionSet | None = None,
    ) -> io.NodeOutput:
        """Check the question before any request, then return the list with it appended."""
        earlier = questions.questions if questions else ()
        name = name.strip()
        if QUESTION_NAME_TEXT.match(name) is None:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUESTION_NAME)
        if any(question.name == name for question in earlier):
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUESTION_REPEATED.format(name=name))
        if not instructions.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUESTION_INSTRUCTIONS)
        question = _build_question(name, instructions.strip(), answer_type)
        return io.NodeOutput(QuestionSet((*earlier, question)))


__all__ = ["DecisionAddQuestion"]
