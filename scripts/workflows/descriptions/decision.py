"""The decision workflow: answer with a quick model, and let Jev send doubtful answers to a stronger one."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow

ASK = f"{NODE_PREFIX}ChatAsk"
NOTES = (
    "The store opens at 9:00 and closes at 18:00 on weekdays. On Saturdays it closes at 14:00, and on the first "
    "Saturday of each month at 16:00. It is closed on Sundays and public holidays. Returns are accepted at the "
    "service desk until 30 minutes before closing."
)
TEXTS = WORKFLOW_TEXTS["decision-01-verify-then-escalate"]

ANSWER = Subgraph(
    name=SHARED_TEXTS["answer"],
    nodes=(
        Node(
            "request",
            HostNode.FORMAT,
            {"f_string": "Answer the question using only these notes.\n\nNotes:\n{a}\n\nQuestion: {b}"},
        ),
        Node("quick", ASK, {"model": "openai/gpt-6-luna"}, is_paid=True),
    ),
    links=(("request.STRING", "quick.prompt"),),
    columns=(("request",), ("quick",)),
    inputs=(("notes", "request.values.a"), ("question", "request.values.b")),
    outputs=(("answer", "quick.text"), ("prompt", "request.STRING")),
    description=TEXTS["answer_description"],
)

CHECK = Subgraph(
    name=SHARED_TEXTS["check"],
    nodes=(
        Node("situation", HostNode.FORMAT, {"f_string": "Notes:\n{a}\n\nQuestion: {b}\n\nAnswer: {c}"}),
        Node("decide", f"{NODE_PREFIX}DecisionAsk", is_paid=True),
        Node("read", f"{NODE_PREFIX}DecisionReadAnswer", {"question": "supported", "threshold": 0.8}),
    ),
    links=(("situation.STRING", "decide.situation"), ("decide.answers", "read.answers")),
    columns=(("situation", "decide"), ("read",)),
    inputs=(
        ("notes", "situation.values.a"),
        ("question", "situation.values.b"),
        ("answer", "situation.values.c"),
        ("questions", "decide.questions"),
    ),
    outputs=(("supported", "read.is_yes"), ("summary", "decide.summary")),
    description=TEXTS["check_description"],
)

ESCALATE = Subgraph(
    name=SHARED_TEXTS["escalate"],
    nodes=(
        Node(
            "careful",
            ASK,
            {"model": "anthropic/claude-opus-5.5", "reasoning_effort": "medium"},
            is_paid=True,
        ),
        Node("pick", HostNode.SWITCH),
    ),
    links=(("careful.text", "pick.on_false"),),
    columns=(("careful",), ("pick",)),
    inputs=(("prompt", "careful.prompt"), ("answer", "pick.on_true"), ("supported", "pick.switch")),
    outputs=(("answer", "pick.output"),),
    description=TEXTS["escalate_description"],
)

VERIFY_ESCALATE = Workflow(
    slug="decision-01-verify-then-escalate",
    nodes=(
        Node("notes", HostNode.TEXT_BLOCK, {"value": NOTES}, title=SHARED_TEXTS["notes"]),
        Node(
            "question",
            HostNode.TEXT,
            {"value": "Until what time can I return an item on the first Saturday of the month?"},
            title=SHARED_TEXTS["question"],
        ),
        Node("answer", ANSWER.name),
        Node(
            "supported",
            f"{NODE_PREFIX}DecisionAddQuestion",
            {
                "name": "supported",
                "instructions": "Is every fact in the answer stated in the notes, and does it answer the question?",
            },
        ),
        Node("check", CHECK.name),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("escalate", ESCALATE.name),
        Node("result", HostNode.PREVIEW, title=SHARED_TEXTS["answer"]),
    ),
    links=(
        ("notes.STRING", "answer.notes"),
        ("question.STRING", "answer.question"),
        ("notes.STRING", "check.notes"),
        ("question.STRING", "check.question"),
        ("answer.answer", "check.answer"),
        ("supported.questions", "check.questions"),
        ("check.summary", "summary.source"),
        ("answer.prompt", "escalate.prompt"),
        ("answer.answer", "escalate.answer"),
        ("check.supported", "escalate.supported"),
        ("escalate.answer", "result.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("notes", "question"),), note=TEXTS["input"]),),
        (Group(SHARED_TEXTS["answer"], (("answer",),), STAGE_COLOUR, TEXTS["answer"]),),
        (Group(SHARED_TEXTS["check"], (("supported",), ("check", "summary")), STAGE_COLOUR, TEXTS["check"]),),
        (Group(SHARED_TEXTS["escalate"], (("escalate",), ("result",)), STAGE_COLOUR, TEXTS["escalate"]),),
    ),
    subgraphs=(ANSWER, CHECK, ESCALATE),
)

DECISION_WORKFLOWS = (VERIFY_ESCALATE,)

__all__ = ["DECISION_WORKFLOWS"]
