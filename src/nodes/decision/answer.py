"""Turn one decision answer into values that switch and math nodes can use."""

from __future__ import annotations

from comfy_api.latest import io
from typing import override, TYPE_CHECKING
from ...config.messages.inputs import QUESTION_UNKNOWN
from ...types.errors import ErrorCode, OpenRouterError
from ...types.decisions import YesNoAnswer, ChoiceAnswer
from ...config.namespace import NODE_PREFIX, ANSWERS_TYPE, DECISION_MENU
from ...config.generation.decisions import THRESHOLD_STEP, DEFAULT_THRESHOLD

if TYPE_CHECKING:
    from ...types.decisions import Answer, AnswerSet


def _build_outputs(answer: Answer, threshold: float) -> tuple[str, bool, float, float, int, float]:
    """Give every output a value for every answer kind, so any output can feed a switch node."""
    if isinstance(answer, YesNoAnswer):
        is_yes = answer.probability >= threshold
        confidence = max(answer.probability, 1 - answer.probability)
        return "yes" if is_yes else "no", is_yes, answer.probability, answer.probability, int(is_yes), confidence
    if isinstance(answer, ChoiceAnswer):
        probability = answer.probabilities.get(answer.choice, answer.confidence)
        keys = list(answer.probabilities)
        level = keys.index(answer.choice) if answer.choice in keys else 0
        is_yes = answer.confidence >= threshold
        return answer.choice, is_yes, probability, probability, level, answer.confidence
    level = max(0, round(answer.score))
    probability = answer.probabilities.get(str(level), 0.0)
    text = answer.legend.get(str(level), str(level))
    return text, answer.confidence >= threshold, probability, answer.score, level, answer.confidence


class DecisionReadAnswer(io.ComfyNode):
    """Read one answer by its question's name."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Offer the answer as text, a yes flag, numbers, and a level."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Decision: Read Answer",
            category=DECISION_MENU,
            description="Turn one decision answer into text, a yes flag, and numbers that switch nodes can use.",
            inputs=[
                io.Custom(ANSWERS_TYPE).Input("answers", tooltip="Connect Decision: Ask."),
                io.String.Input("question", default="question", tooltip="The name of the question to read."),
                io.Float.Input(
                    "threshold",
                    default=DEFAULT_THRESHOLD,
                    min=0.0,
                    max=1.0,
                    step=THRESHOLD_STEP,
                    tooltip="The probability or confidence at which is_yes becomes true.",
                ),
            ],
            outputs=[
                io.String.Output("answer", display_name="answer"),
                io.Boolean.Output("is_yes", display_name="is_yes"),
                io.Float.Output("probability", display_name="probability"),
                io.Float.Output("score", display_name="score"),
                io.Int.Output("level", display_name="level"),
                io.Float.Output("confidence", display_name="confidence"),
            ],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, answers: AnswerSet, question: str, threshold: float = DEFAULT_THRESHOLD
    ) -> io.NodeOutput:
        """Find the answer by name and read its values at the threshold."""
        name = question.strip()
        answer = next((answer for answer in answers.answers if answer.name == name), None)
        if answer is None:
            names = ", ".join(answer.name for answer in answers.answers)
            raise OpenRouterError(ErrorCode.INVALID_INPUT, QUESTION_UNKNOWN.format(name=name, names=names))
        return io.NodeOutput(*_build_outputs(answer, threshold))


__all__ = ["DecisionReadAnswer"]
