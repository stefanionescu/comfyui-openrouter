"""Answer typed questions about a situation with a decision model, such as TypeSafe's Jev, through OpenRouter."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...types.parsing import parse_json
from ..inputs import build_request_inputs
from ...openrouter.decisions import DecisionOperation
from ...types.errors import ErrorCode, OpenRouterError
from ...comfy.execution import send_request, wait_for_task
from ...config.generation.models import DEFAULT_DECISION_MODEL
from ...config.generation.inputs import MODEL_INPUT, MODEL_TOOLTIP
from ...config.messages.inputs import SITUATION_EMPTY, SITUATION_LENGTH
from ...types.decisions import AnswerSet, YesNoAnswer, ChoiceAnswer, DecisionRequest
from ...config.generation.decisions import DEFAULT_THRESHOLD, MAX_SITUATION_CHARACTERS
from ...config.namespace import NODE_PREFIX, ANSWERS_TYPE, DECISION_MENU, QUESTIONS_TYPE

if TYPE_CHECKING:
    from ...types import Json
    from ...types.options import Options
    from ...types.decisions import QuestionSet


def _read_state(situation: str) -> Json:
    """Send a JSON object or array as JSON, and anything else as text, so a person can paste either."""
    if not situation.strip():
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SITUATION_EMPTY)
    if len(situation) > MAX_SITUATION_CHARACTERS:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SITUATION_LENGTH.format(maximum=MAX_SITUATION_CHARACTERS))
    try:
        state = parse_json(situation)
    except OpenRouterError:
        return situation
    return state if isinstance(state, (dict, list)) else situation


def _describe_answers(answers: AnswerSet) -> str:
    """Write one line per answer, with numbers to two decimals."""
    lines: list[str] = []
    for answer in answers.answers:
        if isinstance(answer, ChoiceAnswer):
            lines.append(f"{answer.name}: {answer.choice} (confidence {answer.confidence:.2f})")
        elif isinstance(answer, YesNoAnswer):
            verdict = "yes" if answer.probability >= DEFAULT_THRESHOLD else "no"
            lines.append(f"{answer.name}: {verdict}, probability {answer.probability:.2f}")
        else:
            level = round(answer.score)
            text = answer.legend.get(str(level), str(level))
            lines.append(f"{answer.name}: {text} (score {answer.score:.2f}, confidence {answer.confidence:.2f})")
    return "\n".join(lines)


class DecisionAsk(PaidNode):
    """Send the situation and the questions in one request, and return the answers."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the situation, the questions, and the model."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Decision: Ask",
            category=DECISION_MENU,
            description=(
                "Answer typed questions about a situation with a decision model on OpenRouter, such as TypeSafe's "
                "Jev. Each answer comes with its probabilities."
            ),
            inputs=[
                io.String.Input(
                    "situation",
                    multiline=True,
                    default="",
                    tooltip="What to decide on, as text or as a JSON object or array.",
                ),
                io.Custom(QUESTIONS_TYPE).Input("questions", tooltip="Connect Decision: Add Question."),
                io.String.Input(MODEL_INPUT, default=DEFAULT_DECISION_MODEL, tooltip=MODEL_TOOLTIP),
                *build_request_inputs(has_seed=False),
            ],
            outputs=[
                io.Custom(ANSWERS_TYPE).Output("answers", display_name="answers"),
                io.String.Output("summary", display_name="summary"),
            ],
        )

    @classmethod
    async def send(
        cls,
        *,
        situation: str,
        questions: QuestionSet,
        model: str,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Check the situation, then send it with the questions."""
        request = DecisionRequest(
            model_id=model.strip(),
            state=_read_state(situation),
            questions=questions,
            options=options,
        )
        task = asyncio.create_task(
            send_request(DecisionOperation(request), lambda answers: io.NodeOutput(answers, _describe_answers(answers)))
        )
        return await wait_for_task(task)


__all__ = ["DecisionAsk"]
