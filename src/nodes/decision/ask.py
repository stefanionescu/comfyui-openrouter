"""Answer typed questions about a situation with an OpenRouter decision model."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from ...serialization import parse_json
from typing import ClassVar, TYPE_CHECKING
from ...state.capabilities import TextChoice
from ...errors import ErrorCode, ConnectorError
from ...execution.decisions import DecisionOperation
from ...comfy.execution import run_request, wait_for_execution
from ...config.generation.models import DEFAULT_DECISION_MODEL
from ...config.messages.inputs import SITUATION_EMPTY, SITUATION_LENGTH
from ..inputs import read_model, define_model_input, define_request_inputs
from ...state.decisions import AnswerSet, YesNoAnswer, ChoiceAnswer, DecisionRequest
from ...config.generation.decisions import DEFAULT_THRESHOLD, MAX_SITUATION_CHARACTERS
from ...config.namespace import NODE_PREFIX, ANSWERS_TYPE, DECISION_MENU, QUESTIONS_TYPE

if TYPE_CHECKING:
    from ...state import Json
    from ...state.decisions import QuestionSet
    from ...state.options import RequestOptions


def _read_state(situation: str) -> Json:
    """Send a JSON object or array as JSON, and anything else as text, so a person can paste either."""
    if not situation.strip():
        raise ConnectorError(ErrorCode.INVALID_INPUT, SITUATION_EMPTY)
    if len(situation) > MAX_SITUATION_CHARACTERS:
        raise ConnectorError(ErrorCode.INVALID_INPUT, SITUATION_LENGTH.format(maximum=MAX_SITUATION_CHARACTERS))
    try:
        state = parse_json(situation)
    except ConnectorError:
        return situation
    return state if isinstance(state, (dict, list)) else situation


def summarize(answers: AnswerSet) -> str:
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

    contract: ClassVar[str] = "decision-ask-v1"

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Build the model dropdown of decision models, which take no per-model settings."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Decision: Ask",
            category=DECISION_MENU,
            description=(
                "Answer typed questions about a situation with an OpenRouter decision model, "
                "with probabilities instead of text."
            ),
            inputs=[
                io.String.Input(
                    "situation",
                    multiline=True,
                    default="",
                    tooltip="What to decide on, as text or as a JSON object or array.",
                ),
                io.Custom(QUESTIONS_TYPE).Input("questions", tooltip="Connect Decision: Add Question."),
                define_model_input("decisions", DEFAULT_DECISION_MODEL, lambda _choice: [], []),
                *define_request_inputs(has_seed=False),
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
        model: dict[str, object],
        options: RequestOptions | None = None,
    ) -> io.NodeOutput:
        """Check the situation, then send it with the questions."""
        selection = read_model("decisions", model, TextChoice)
        request = DecisionRequest(
            model_id=selection.model_id,
            choice=selection.choice,
            state=_read_state(situation),
            questions=questions,
            options=options,
        )
        task = asyncio.create_task(
            run_request(DecisionOperation(request), lambda answers: io.NodeOutput(answers, summarize(answers)))
        )
        return await wait_for_execution(task)


__all__ = ["DecisionAsk", "summarize"]
