"""The decision workflows: classify, verify, route, and verify then escalate, as OpenRouter's Jev guides describe."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import (
    TEXT,
    AUDIO,
    FORMAT,
    SWITCH,
    COMPARE,
    PREVIEW,
    SAVE_IMAGE,
    TEXT_BLOCK,
)

ASK = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
CHAT = f"{NODE_PREFIX}ChatAsk"
GENERATE = f"{NODE_PREFIX}ImageGenerate"

SORT_A_TICKET = Workflow(
    slug="decision-01-sort-a-ticket",
    nodes=(
        Node(
            "team",
            QUESTION,
            {
                "name": "team",
                "instructions": "Which team should handle this ticket?",
                "answer_type": "one choice",
                "answer_type.options": (
                    "payments: Checkout, billing, and payment problems.\n"
                    "frontend: Pages that do not display or respond."
                ),
            },
        ),
        Node(
            "bug",
            QUESTION,
            {
                "name": "is_bug",
                "instructions": "Is this a defect?",
                "answer_type.yes_means": "Something that worked is broken.",
                "answer_type.no_means": "A question, a request, or expected behavior.",
            },
        ),
        Node(
            "urgency",
            QUESTION,
            {
                "name": "urgency",
                "instructions": "How urgent is this ticket?",
                "answer_type": "score",
                "answer_type.levels": "Can wait\nThis week\nBlocking revenue right now",
            },
        ),
        Node("ask", ASK, {"situation": "My checkout page shows a blank screen."}, is_paid=True),
        Node("read", READ, {"question": "team"}),
        Node("answer", PREVIEW, title=SHARED_TEXTS["answer"]),
        Node("summary", PREVIEW, title="Summary"),
    ),
    links=(
        ("team.questions", "bug.questions"),
        ("bug.questions", "urgency.questions"),
        ("urgency.questions", "ask.questions"),
        ("ask.answers", "read.answers"),
        ("read.answer", "answer.source"),
        ("ask.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("team", "bug", "urgency"),)),),
        (Group(SHARED_TEXTS["decision"], (("ask", "summary"),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["answer"], (("read", "answer"),)),),
    ),
)

SORT_A_VOICEMAIL = Workflow(
    slug="decision-02-sort-a-voicemail",
    nodes=(
        Node("recording", AUDIO, {"audio": ""}),
        Node("transcribe", f"{NODE_PREFIX}AudioTranscribe", is_paid=True),
        Node(
            "department",
            QUESTION,
            {
                "name": "department",
                "instructions": "Which department should call back?",
                "answer_type": "one choice",
                "answer_type.options": "sales\nsupport\nbilling",
            },
        ),
        Node(
            "callback",
            QUESTION,
            {"name": "callback", "instructions": "Does the caller ask to be called back?"},
        ),
        Node("ask", ASK, is_paid=True),
        Node("summary", PREVIEW, title="Summary"),
    ),
    links=(
        ("recording.AUDIO", "transcribe.audio"),
        ("transcribe.text", "ask.situation"),
        ("department.questions", "callback.questions"),
        ("callback.questions", "ask.questions"),
        ("ask.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("recording", "department", "callback"),)),),
        (Group(SHARED_TEXTS["transcript"], (("transcribe",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["decision"], (("ask", "summary"),), STAGE_COLOUR),),
    ),
)

CHECK_BEFORE_SAVING = Workflow(
    slug="decision-03-check-an-image-before-saving",
    nodes=(
        Node("brief", TEXT_BLOCK, {"value": "A red panda astronaut floating in space"}, title="Brief"),
        Node("approved", TEXT, {"value": "openrouter/approved"}, title="Approved folder"),
        Node("rejected", TEXT, {"value": "openrouter/rejected"}, title="Rejected folder"),
        Node(
            "check",
            QUESTION,
            {
                "name": "matches",
                "instructions": "Does the image, as described, show everything the brief asks for?",
            },
        ),
        Node("image", GENERATE, is_paid=True),
        Node("describe", CHAT, {"prompt": "Describe this image in one paragraph."}, is_paid=True),
        Node("situation", FORMAT, {"f_string": "Brief: {a}\n\nDescription of the image: {b}"}),
        Node("ask", ASK, is_paid=True),
        Node("read", READ, {"question": "matches"}),
        Node("folder", SWITCH),
        Node("save", SAVE_IMAGE),
    ),
    links=(
        ("brief.STRING", "image.prompt"),
        ("brief.STRING", "situation.values.a"),
        ("image.images", "describe.model.images.image_1"),
        ("image.images", "save.images"),
        ("describe.text", "situation.values.b"),
        ("situation.STRING", "ask.situation"),
        ("check.questions", "ask.questions"),
        ("ask.answers", "read.answers"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("rejected.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief", "check"), ("approved", "rejected"))),),
        (Group(SHARED_TEXTS["image"], (("image",), ("describe", "situation")), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["decision"], (("ask", "read"), ("folder", "save")), STAGE_COLOUR),),
    ),
)

ROUTE_A_REQUEST = Workflow(
    slug="decision-04-route-a-request",
    nodes=(
        Node(
            "request",
            TEXT_BLOCK,
            {"value": "A product shot of a red sneaker on a white background"},
            title="Request",
        ),
        Node(
            "style",
            QUESTION,
            {
                "name": "style",
                "instructions": "Does the request ask for a photograph or an illustration?",
                "answer_type": "one choice",
                "answer_type.options": "photo: A realistic photograph.\nillustration: A drawing or painting.",
            },
        ),
        Node("ask", ASK, is_paid=True),
        Node("read", READ, {"question": "style"}),
        Node("is_photo", COMPARE, {"string_b": "photo"}),
        Node("photo", GENERATE, {"model": "black-forest-labs/flux.2-pro"}, is_paid=True),
        Node("drawing", GENERATE, {"model": "recraft/recraft-v4.1"}, is_paid=True),
        Node("pick", SWITCH),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/decision-04-route-a-request"}),
    ),
    links=(
        ("request.STRING", "ask.situation"),
        ("request.STRING", "photo.prompt"),
        ("request.STRING", "drawing.prompt"),
        ("style.questions", "ask.questions"),
        ("ask.answers", "read.answers"),
        ("read.answer", "is_photo.string_a"),
        ("is_photo.BOOLEAN", "pick.switch"),
        ("photo.images", "pick.on_true"),
        ("drawing.images", "pick.on_false"),
        ("pick.output", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("request", "style"),)),),
        (Group(SHARED_TEXTS["decision"], (("ask", "read", "is_photo"),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["image"], (("photo", "drawing"), ("pick", "save")), STAGE_COLOUR),),
    ),
)

VERIFY_THEN_ESCALATE = Workflow(
    slug="decision-05-verify-then-escalate",
    nodes=(
        Node(
            "notes",
            TEXT_BLOCK,
            {
                "value": (
                    "The store opens at 9:00 and closes at 18:00 on weekdays. "
                    "On Saturdays it closes at 14:00. It is closed on Sundays."
                )
            },
            title="Notes",
        ),
        Node("question", TEXT, {"value": "When does the store close on Saturday?"}, title="Question"),
        Node(
            "supported",
            QUESTION,
            {
                "name": "supported",
                "instructions": (
                    "Is every fact in the answer stated in the notes, and does the answer address the question?"
                ),
            },
        ),
        Node(
            "task",
            FORMAT,
            {"f_string": "Answer the question using only these notes.\n\nNotes:\n{a}\n\nQuestion: {b}"},
        ),
        Node("draft", CHAT, is_paid=True),
        Node("situation", FORMAT, {"f_string": "Notes:\n{a}\n\nQuestion: {b}\n\nAnswer: {c}"}),
        Node("ask", ASK, is_paid=True),
        Node("read", READ, {"question": "supported", "threshold": 0.8}),
        Node("strong", CHAT, {"model": "anthropic/claude-sonnet-5"}, is_paid=True),
        Node("pick", SWITCH),
        Node("answer", PREVIEW, title=SHARED_TEXTS["answer"]),
    ),
    links=(
        ("notes.STRING", "task.values.a"),
        ("question.STRING", "task.values.b"),
        ("task.STRING", "draft.prompt"),
        ("task.STRING", "strong.prompt"),
        ("notes.STRING", "situation.values.a"),
        ("question.STRING", "situation.values.b"),
        ("draft.text", "situation.values.c"),
        ("situation.STRING", "ask.situation"),
        ("supported.questions", "ask.questions"),
        ("ask.answers", "read.answers"),
        ("read.is_yes", "pick.switch"),
        ("draft.text", "pick.on_true"),
        ("strong.text", "pick.on_false"),
        ("pick.output", "answer.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("notes", "question", "supported"),)),),
        (Group(SHARED_TEXTS["ask"], (("task", "draft"), ("situation",)), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["decision"], (("ask", "read"),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["answer"], (("strong",), ("pick", "answer")), STAGE_COLOUR),),
    ),
)

DECISION_WORKFLOWS = (
    SORT_A_TICKET,
    SORT_A_VOICEMAIL,
    CHECK_BEFORE_SAVING,
    ROUTE_A_REQUEST,
    VERIFY_THEN_ESCALATE,
)

__all__ = ["DECISION_WORKFLOWS"]
