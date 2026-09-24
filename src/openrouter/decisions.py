"""Send one decision request and read each answer in question order."""

from __future__ import annotations

from .models import check_model
from .transport import post_json
from typing import TYPE_CHECKING
from .options import apply_options
from pydantic import ValidationError
from ..state.replies import DecisionReply
from ..config.openrouter import DECISIONS_URL
from ..errors import ErrorCode, ConnectorError
from ..config.messages.run import REPLY_UNREADABLE
from ..state.decisions import (
    AnswerSet,
    ScoreAnswer,
    YesNoAnswer,
    ChoiceAnswer,
    ScoreQuestion,
    YesNoQuestion,
    ChoiceQuestion,
)

if TYPE_CHECKING:
    from ..state import Json
    from ..state.replies import AnswerReply
    from ..state.settings import Settings, ExecutionConfiguration
    from ..state.decisions import Answer, Question, DecisionRequest

# The wire type of each question kind.
WIRE_TYPES = {ChoiceQuestion: "choice", YesNoQuestion: "noul", ScoreQuestion: "score"}


def _describe_question(question: Question) -> dict[str, Json]:
    """Write one question as Jev reads it; a choice option without a description sends null."""
    described: dict[str, Json] = {"type": WIRE_TYPES[type(question)], "instructions": question.instructions}
    if isinstance(question, ChoiceQuestion):
        described["criteria"] = {key: description or None for key, description in question.options}
    elif isinstance(question, ScoreQuestion):
        described["criteria"] = list(question.levels)
    elif question.yes_means or question.no_means:
        described["criteria"] = {"true": question.yes_means, "false": question.no_means}
    return described


def _read_answer(question: Question, reply: AnswerReply | None) -> Answer:
    """Read the answer to one question, which must be of the question's own kind."""
    if reply is None or reply.type != WIRE_TYPES[type(question)]:
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    if isinstance(question, YesNoQuestion) and reply.noul is not None:
        return YesNoAnswer(question.name, reply.noul)
    if isinstance(question, ChoiceQuestion) and reply.choice is not None:
        return ChoiceAnswer(question.name, reply.choice, reply.confidence or 0.0, dict(reply.probabilities))
    if isinstance(question, ScoreQuestion) and reply.score is not None:
        legend = {key: value if isinstance(value, str) else str(value) for key, value in reply.legend.items()}
        return ScoreAnswer(question.name, reply.score, reply.confidence or 0.0, dict(reply.probabilities), legend)
    raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)


class DecisionOperation:
    """One decision request; its questions and situation were checked when they were built."""

    def __init__(self, request: DecisionRequest) -> None:
        """Keep the request to send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Accept the request: Decision: Add Question checks each question and Decision: Ask the situation."""

    async def send(self, configuration: ExecutionConfiguration) -> AnswerSet:
        """Check the model, send the situation and questions, and read the answers in question order."""
        request = self.request
        await check_model(request.model_id, "decisions", configuration)
        questions: dict[str, Json] = {
            question.name: _describe_question(question) for question in request.questions.questions
        }
        body: dict[str, Json] = {"model": request.model_id, "state": request.state, "questions": questions}
        document = await post_json(DECISIONS_URL, apply_options(body, request.options, "decisions"), configuration)
        try:
            reply = DecisionReply.model_validate(document)
        except ValidationError:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        return AnswerSet(
            tuple(_read_answer(question, reply.answers.get(question.name)) for question in request.questions.questions)
        )


__all__ = ["DecisionOperation"]
