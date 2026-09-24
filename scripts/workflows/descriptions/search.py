"""The search workflows: answer from ranked help articles, and choose a hero image, each checked by Jev."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import TEXT, FORMAT, SWITCH, PREVIEW, SAVE_IMAGE, TEXT_BLOCK

ASK = f"{NODE_PREFIX}ChatAsk"
RANK = f"{NODE_PREFIX}SearchRank"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
READER = "openai/gpt-6-luna"
ARTICLES = (
    "Returns: unused items can be returned within 30 days for a full refund; opened items within 14 days.\n"
    "Shipping: standard delivery takes 3 to 5 working days; express orders placed before 2 pm arrive next day.\n"
    "Warranty: every kettle and toaster has a two-year warranty covering faults, not accidental damage.\n"
    "Descaling: descale kettles every four weeks in hard-water areas using the descaling tablets we sell.\n"
    "Payment: we accept cards, PayPal, and gift cards; we do not accept bank transfers.\n"
    "Order changes: you can change the address or cancel an order until it is packed, usually within 2 hours.\n"
    "Gift wrap: gift wrap costs 4 euros per item and includes a handwritten card.\n"
    "Repairs: send faulty items under warranty to our repair centre; we cover the postage both ways."
)

ANSWER_FROM_ARTICLES = Workflow(
    slug="search-01-answer-from-help-articles",
    nodes=(
        Node(
            "question",
            TEXT,
            {"value": "My kettle stopped heating after 18 months. Can I get it fixed for free?"},
            title="Customer Question",
        ),
        Node("articles", TEXT_BLOCK, {"value": ARTICLES}, title="Help Articles"),
        Node(
            "supported",
            QUESTION,
            {"name": "supported", "instructions": "Does every sentence of the answer come from the articles?"},
            title="Supported",
        ),
        Node(
            "person",
            QUESTION,
            {
                "name": "needs_person",
                "instructions": "Should a person handle this customer instead of an automatic reply?",
            },
            title="Needs a Person",
        ),
        Node(
            "find",
            RANK,
            {"model": "cohere/rerank-4-pro", "top_n": 3},
            title="Find Relevant Articles",
            is_paid=True,
        ),
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "Answer the customer in three sentences or fewer, using only these help articles.\n\n"
                    "Articles:\n{a}\n\nCustomer: {b}"
                )
            },
            title="Answer Request",
        ),
        Node("draft", ASK, {"model": READER}, title="Draft the Answer", is_paid=True),
        Node(
            "situation",
            FORMAT,
            {"f_string": "Articles:\n{a}\n\nCustomer: {b}\n\nDraft answer: {c}"},
            title="Articles and Draft",
        ),
        Node("decide", DECIDE, title="Check the Draft", is_paid=True),
        Node("read", READ, {"question": "supported"}, title="Read Supported"),
        Node(
            "escalation",
            FORMAT,
            {"f_string": "Escalate to a person. The customer asked: {a}"},
            title="Escalation Note",
        ),
        Node("pick", SWITCH, title="Answer or Escalate"),
        Node("reply", PREVIEW, title="Reply"),
        Node("summary", PREVIEW, title="Check Summary"),
    ),
    links=(
        ("question.STRING", "find.query"),
        ("articles.STRING", "find.documents"),
        ("find.texts", "request.values.a"),
        ("question.STRING", "request.values.b"),
        ("request.STRING", "draft.prompt"),
        ("find.texts", "situation.values.a"),
        ("question.STRING", "situation.values.b"),
        ("draft.text", "situation.values.c"),
        ("situation.STRING", "decide.situation"),
        ("supported.questions", "person.questions"),
        ("person.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("decide.summary", "summary.source"),
        ("question.STRING", "escalation.values.a"),
        ("read.is_yes", "pick.switch"),
        ("draft.text", "pick.on_true"),
        ("escalation.STRING", "pick.on_false"),
        ("pick.output", "reply.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("question", "articles"), ("supported", "person"))),),
        (Group(SHARED_TEXTS["search"], (("find", "request"), ("draft", "situation")), STAGE_COLOUR),),
        (
            Group(
                SHARED_TEXTS["answer"], (("decide", "read"), ("escalation", "pick"), ("reply", "summary")), STAGE_COLOUR
            ),
        ),
    ),
)

CHOOSE_HERO_IMAGE = Workflow(
    slug="search-02-choose-a-hero-image",
    nodes=(
        Node(
            "brief",
            TEXT_BLOCK,
            {
                "value": (
                    "Homepage hero for an outdoor gear shop's spring sale: a hiker on a ridge at sunrise, wide "
                    "landscape, calm sky on the left for the headline"
                )
            },
            title="Hero Brief",
        ),
        Node(
            "ready",
            QUESTION,
            {
                "name": "hero_ready",
                "instructions": (
                    "Does the image work as a homepage hero: a clear subject, open space for a headline, and no "
                    "visible defects?"
                ),
            },
            title="Hero Ready",
        ),
        Node(
            "candidates",
            f"{NODE_PREFIX}ImageGenerate",
            {"model": "recraft/recraft-v4.1-flash", "model.aspect_ratio": "16:9", "model.count": 4},
            title="Four Candidates",
            is_paid=True,
        ),
        Node(
            "rank",
            RANK,
            {"model": "nvidia/llama-nemotron-rerank-vl-1b-v2:free", "top_n": 1},
            title="Rank the Images",
            is_paid=True,
        ),
        Node(
            "describe",
            ASK,
            {
                "model": READER,
                "prompt": (
                    "Describe this image in three sentences: the subject, where the empty space is, and any visible "
                    "defect."
                ),
            },
            title="Describe the Winner",
            is_paid=True,
        ),
        Node(
            "situation",
            FORMAT,
            {"f_string": "Brief:\n{a}\n\nWinning image:\n{b}\n\nRank scores: {c}"},
            title="Brief and Winner",
        ),
        Node("decide", DECIDE, title="Check the Winner", is_paid=True),
        Node("read", READ, {"question": "hero_ready"}, title="Read Hero Ready"),
        Node("approved", TEXT, {"value": "hero/approved"}, title="Approved Folder"),
        Node("review", TEXT, {"value": "hero/review"}, title="Review Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_IMAGE, title="Save the Hero"),
        Node("summary", PREVIEW, title="Check Summary"),
    ),
    links=(
        ("brief.STRING", "candidates.prompt"),
        ("brief.STRING", "rank.query"),
        ("brief.STRING", "situation.values.a"),
        ("candidates.images", "rank.model.images.image_1"),
        ("rank.images", "describe.model.images.image_1"),
        ("describe.text", "situation.values.b"),
        ("rank.scores", "situation.values.c"),
        ("situation.STRING", "decide.situation"),
        ("ready.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("decide.summary", "summary.source"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("rank.images", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief", "ready"),)),),
        (Group(SHARED_TEXTS["search"], (("candidates", "rank"), ("describe", "situation")), STAGE_COLOUR),),
        (
            Group(
                SHARED_TEXTS["check"],
                (("decide", "read"), ("approved", "review", "folder"), ("save", "summary")),
                STAGE_COLOUR,
            ),
        ),
    ),
)

SEARCH_WORKFLOWS = (ANSWER_FROM_ARTICLES, CHOOSE_HERO_IMAGE)

__all__ = ["SEARCH_WORKFLOWS"]
