"""Answer typed questions about a situation with a decision model, such as TypeSafe's Jev, through OpenRouter."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from dataclasses import dataclass

from comfy_api.latest import io

from ..base import PaidNode, build_request_inputs
from ...state.errors import ErrorCode, OpenRouterError
from ...state.parsing import parse_json
from ...comfy.execution import send_request, wait_for_task
from ...state.decisions import AnswerSet, YesNoAnswer, ChoiceAnswer, DecisionRequest
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...openrouter.decisions import DecisionOperation
from ...config.messages.inputs import SITUATION_EMPTY
from ...config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ...config.generation.models import DEFAULT_MODELS
from ...config.generation.decisions import THRESHOLD

if TYPE_CHECKING:
    from ...state import Json
    from ...state.options import Options
    from ...state.decisions import QuestionSet


def _read_state(situation: str) -> Json:
    """Send a JSON object or array as JSON, and anything else as text, so a person can paste either.

    OpenRouter refuses a situation longer than the model reads, so the node leaves the length check to it.
    """
    if not situation.strip():
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SITUATION_EMPTY)
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
            lines.append(f'{answer.name}: {answer.choice} (confidence {answer.confidence:.2f})')
        elif isinstance(answer, YesNoAnswer):
            verdict = 'yes' if answer.probability >= THRESHOLD['DEFAULT'] else 'no'
            lines.append(f'{answer.name}: {verdict}, probability {answer.probability:.2f}')
        else:
            level = round(answer.score)
            text = answer.legend.get(str(level), str(level))
            lines.append(f'{answer.name}: {text} (score {answer.score:.2f}, confidence {answer.confidence:.2f})')
    return '\n'.join(lines)


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionAskInputs:
    """The saved inputs of Decision: Ask, by input name, except the run number."""

    situation: str
    questions: QuestionSet
    model: str
    options: Options | None = None


class DecisionAsk(PaidNode):
    """Send the situation and the questions in one request, and return the answers."""

    record = DecisionAskInputs

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the situation, the questions, and the model."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Decision: Ask',
            category=MENUS['DECISION'],
            description=(
                "Answer typed questions about a situation with a decision model on OpenRouter, such as TypeSafe's "
                'Jev. Each answer comes with its probabilities.'
            ),
            inputs=[
                io.Custom(SOCKET_TYPES['QUESTIONS']).Input('questions', tooltip='Connect Decision: Add Question.'),
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['decisions'], tooltip=MODEL_TOOLTIP),
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    'situation',
                    multiline=True,
                    default='',
                    tooltip='What to decide on, as text or as a JSON object or array.',
                ),
            ],
            outputs=[
                io.Custom(SOCKET_TYPES['ANSWERS']).Output('answers', display_name='answers'),
                io.String.Output('summary', display_name='summary'),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(cls, decision: DecisionAskInputs) -> io.NodeOutput:
        """Check the situation, then send it with the questions."""
        request = DecisionRequest(
            model_id=decision.model.strip(),
            state=_read_state(decision.situation),
            questions=decision.questions,
            options=decision.options,
        )
        return await wait_for_task(
            send_request(
                DecisionOperation(request).send,
                lambda answers: io.NodeOutput(answers, _describe_answers(answers)),
                cls.hidden.unique_id,
            )
        )


__all__ = ['DecisionAsk']
