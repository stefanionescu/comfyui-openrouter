"""The decision workflow: answer with a quick model, and let Jev send doubtful answers to a stronger one."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import TEXT, FORMAT, SWITCH, PREVIEW, TEXT_BLOCK

ASK = f"{NODE_PREFIX}ChatAsk"
NOTES = (
    "The store opens at 9:00 and closes at 18:00 on weekdays. On Saturdays it closes at 14:00, and on the first "
    "Saturday of each month at 16:00. It is closed on Sundays and public holidays. Returns are accepted at the "
    "service desk until 30 minutes before closing."
)

VERIFY_ESCALATE = Workflow(
    slug="decision-01-verify-then-escalate",
    nodes=(
        Node("notes", TEXT_BLOCK, {"value": NOTES}, title="Notes"),
        Node(
            "question",
            TEXT,
            {"value": "Until what time can I return an item on the first Saturday of the month?"},
            title="Question",
        ),
        Node(
            "supported",
            f"{NODE_PREFIX}DecisionAddQuestion",
            {
                "name": "supported",
                "instructions": "Is every fact in the answer stated in the notes, and does it answer the question?",
            },
            title="Supported",
        ),
        Node(
            "request",
            FORMAT,
            {"f_string": "Answer the question using only these notes.\n\nNotes:\n{a}\n\nQuestion: {b}"},
            title="Answer Request",
        ),
        Node("quick", ASK, {"model": "openai/gpt-6-luna"}, title="Quick Answer", is_paid=True),
        Node(
            "situation",
            FORMAT,
            {"f_string": "Notes:\n{a}\n\nQuestion: {b}\n\nAnswer: {c}"},
            title="Notes and Answer",
        ),
        Node("decide", f"{NODE_PREFIX}DecisionAsk", title="Check the Answer", is_paid=True),
        Node(
            "read",
            f"{NODE_PREFIX}DecisionReadAnswer",
            {"question": "supported", "threshold": 0.8},
            title="Read Supported",
        ),
        Node(
            "careful",
            ASK,
            {"model": "anthropic/claude-opus-5.5", "model.reasoning": "medium"},
            title="Careful Answer",
            is_paid=True,
        ),
        Node("pick", SWITCH, title="Keep or Escalate"),
        Node("answer", PREVIEW, title="Answer"),
        Node("summary", PREVIEW, title="Check Summary"),
    ),
    links=(
        ("notes.STRING", "request.values.a"),
        ("question.STRING", "request.values.b"),
        ("request.STRING", "quick.prompt"),
        ("request.STRING", "careful.prompt"),
        ("notes.STRING", "situation.values.a"),
        ("question.STRING", "situation.values.b"),
        ("quick.text", "situation.values.c"),
        ("situation.STRING", "decide.situation"),
        ("supported.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("decide.summary", "summary.source"),
        ("read.is_yes", "pick.switch"),
        ("quick.text", "pick.on_true"),
        ("careful.text", "pick.on_false"),
        ("pick.output", "answer.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("notes", "question"), ("supported", "request"))),),
        (Group(SHARED_TEXTS["check"], (("quick", "situation"), ("decide", "read")), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["escalate"], (("careful",), ("pick", "answer", "summary")), STAGE_COLOUR),),
    ),
)

DECISION_WORKFLOWS = (VERIFY_ESCALATE,)

__all__ = ["DECISION_WORKFLOWS"]
