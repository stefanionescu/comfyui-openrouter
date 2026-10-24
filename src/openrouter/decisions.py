"""Send one decision request and read each answer in question order."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

from .models import validate_model
from .options import build_request_body
from .transport import send_json, read_reply
from ..state.errors import ErrorCode, OpenRouterError
from ..state.replies import DecisionReply
from ..state.decisions import (
    AnswerSet,
    ScoreAnswer,
    YesNoAnswer,
    ChoiceAnswer,
    ScoreQuestion,
    YesNoQuestion,
    ChoiceQuestion,
)
from ..config.openrouter import ENDPOINT_URLS
from ..config.messages.run import REPLY_UNREADABLE

if TYPE_CHECKING:
    from ..state import Json
    from ..state.replies import AnswerReply
    from ..state.settings import Configuration
    from ..state.decisions import Answer, Question, DecisionRequest

# The wire type of each question kind.
WIRE_TYPES = {ChoiceQuestion: 'choice', YesNoQuestion: 'noul', ScoreQuestion: 'score'}


def _describe_question(question: Question) -> dict[str, Json]:
    """Write one question as Jev reads it; a choice option without a description sends null."""
    described: dict[str, Json] = {'type': WIRE_TYPES[type(question)], 'instructions': question.instructions}
    if isinstance(question, ChoiceQuestion):
        described['criteria'] = {key: description or None for key, description in question.options}
    elif isinstance(question, ScoreQuestion):
        described['criteria'] = list(question.levels)
    elif question.yes_means or question.no_means:
        described['criteria'] = {'true': question.yes_means, 'false': question.no_means}
    return described


def _read_answer(question: Question, reply: AnswerReply | None) -> Answer:
    """Read the answer to one question, which must be of the question's own kind; a choice must be one of its keys."""
    if reply is None or reply.type != WIRE_TYPES[type(question)]:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    if isinstance(question, YesNoQuestion) and reply.noul is not None:
        return YesNoAnswer(question.name, reply.noul)
    keys = [key for key, _description in question.options] if isinstance(question, ChoiceQuestion) else []
    if reply.choice in keys:
        level = keys.index(reply.choice)
        return ChoiceAnswer(question.name, reply.choice, level, reply.confidence or 0.0, dict(reply.probabilities))
    if isinstance(question, ScoreQuestion) and reply.score is not None:
        legend = {key: value if isinstance(value, str) else str(value) for key, value in reply.legend.items()}
        return ScoreAnswer(question.name, reply.score, reply.confidence or 0.0, dict(reply.probabilities), legend)
    raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)


@dataclass(frozen=True, slots=True)
class DecisionOperation:
    """One decision request; Decision: Add Question checks each question and Decision: Ask the situation.

    Attributes:
        request: The request to send.

    """

    request: DecisionRequest

    async def send(self, configuration: Configuration) -> AnswerSet:
        """Check the model, send the situation and questions, and read the answers in question order."""
        request = self.request
        await validate_model(request.model_id, 'decisions', configuration.settings)
        questions: dict[str, Json] = {
            question.name: _describe_question(question) for question in request.questions.questions
        }
        body: dict[str, Json] = {'model': request.model_id, 'state': request.state, 'questions': questions}
        document = await send_json(
            ENDPOINT_URLS['decisions'], build_request_body(body, request.options, 'decisions'), configuration
        )
        reply = read_reply(DecisionReply, document)
        return AnswerSet(
            tuple(_read_answer(question, reply.answers.get(question.name)) for question in request.questions.questions)
        )


__all__ = ['DecisionOperation']
