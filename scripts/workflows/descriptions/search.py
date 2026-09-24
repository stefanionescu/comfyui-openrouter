"""The search workflows: answer from ranked help articles, and choose a hero image, each checked by Jev."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
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
ARTICLE_TEXTS = WORKFLOW_TEXTS["search-01-answer-from-help-articles"]
HERO_TEXTS = WORKFLOW_TEXTS["search-02-choose-a-hero-image"]

ANSWER = Subgraph(
    name=SHARED_TEXTS["answer"],
    nodes=(
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "Answer the customer in three sentences or fewer, using only these help articles.\n\n"
                    "Articles:\n{a}\n\nCustomer: {b}"
                )
            },
        ),
        Node("answer", ASK, {"model": READER}, is_paid=True),
    ),
    links=(("request.STRING", "answer.prompt"),),
    columns=(("request",), ("answer",)),
    inputs=(("articles", "request.values.a"), ("question", "request.values.b")),
    outputs=(("answer", "answer.text"),),
    description=ARTICLE_TEXTS["answer_description"],
)

CHECK_ANSWER = Subgraph(
    name=SHARED_TEXTS["check"],
    nodes=(
        Node("situation", FORMAT, {"f_string": "Articles:\n{a}\n\nCustomer: {b}\n\nAnswer: {c}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("read", READ, {"question": "supported"}),
        Node("escalation", FORMAT, {"f_string": "Pass this customer to a person. They asked: {a}"}),
        Node("pick", SWITCH),
    ),
    links=(
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "read.answers"),
        ("read.is_yes", "pick.switch"),
        ("escalation.STRING", "pick.on_false"),
    ),
    columns=(("situation", "decide"), ("read", "escalation"), ("pick",)),
    inputs=(
        ("articles", "situation.values.a"),
        ("question", "situation.values.b"),
        ("question", "escalation.values.a"),
        ("answer", "situation.values.c"),
        ("answer", "pick.on_true"),
        ("questions", "decide.questions"),
    ),
    outputs=(("reply", "pick.output"), ("summary", "decide.summary")),
    description=ARTICLE_TEXTS["check_description"],
)

ANSWER_FROM_ARTICLES = Workflow(
    slug="search-01-answer-from-help-articles",
    nodes=(
        Node(
            "question",
            TEXT,
            {"value": "My kettle stopped heating after 18 months. Can I get it fixed for free?"},
            title=SHARED_TEXTS["question"],
        ),
        Node("articles", TEXT_BLOCK, {"value": ARTICLES}, title=SHARED_TEXTS["articles"]),
        Node("rank", RANK, {"model": "cohere/rerank-4-pro", "top_n": 3}, is_paid=True),
        Node("answer", ANSWER.name),
        Node(
            "supported",
            QUESTION,
            {"name": "supported", "instructions": "Does every sentence of the answer come from the articles?"},
        ),
        Node("check", CHECK_ANSWER.name),
        Node("reply", PREVIEW, title=SHARED_TEXTS["reply"]),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("question.STRING", "rank.query"),
        ("articles.STRING", "rank.documents"),
        ("rank.texts", "answer.articles"),
        ("question.STRING", "answer.question"),
        ("rank.texts", "check.articles"),
        ("question.STRING", "check.question"),
        ("answer.answer", "check.answer"),
        ("supported.questions", "check.questions"),
        ("check.reply", "reply.source"),
        ("check.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("question", "articles"),), note=ARTICLE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["search"], (("rank",),), STAGE_COLOUR, ARTICLE_TEXTS["search"]),),
        (Group(SHARED_TEXTS["answer"], (("answer",),), STAGE_COLOUR, ARTICLE_TEXTS["answer"]),),
        (
            Group(
                SHARED_TEXTS["check"],
                (("supported", "check"), ("reply", "summary")),
                STAGE_COLOUR,
                ARTICLE_TEXTS["check"],
            ),
        ),
    ),
    subgraphs=(ANSWER, CHECK_ANSWER),
)

RANK_IMAGES = Subgraph(
    name=SHARED_TEXTS["rank"],
    nodes=(
        Node(
            "candidates",
            f"{NODE_PREFIX}ImageGenerate",
            {"model": "recraft/recraft-v4.1-flash", "model.aspect_ratio": "16:9", "model.count": 4},
            is_paid=True,
        ),
        Node("rank", RANK, {"model": "nvidia/llama-nemotron-rerank-vl-1b-v2:free", "top_n": 1}, is_paid=True),
    ),
    links=(("candidates.images", "rank.model.images.image_1"),),
    columns=(("candidates",), ("rank",)),
    inputs=(("brief", "candidates.prompt"), ("brief", "rank.query")),
    outputs=(("image", "rank.images"), ("scores", "rank.scores")),
    description=HERO_TEXTS["rank_description"],
)

CHECK_HERO = Subgraph(
    name=SHARED_TEXTS["check"],
    nodes=(
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
            is_paid=True,
        ),
        Node("situation", FORMAT, {"f_string": "Brief:\n{a}\n\nWinning image:\n{b}\n\nRank scores: {c}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("read", READ, {"question": "ready"}),
        Node("approved", TEXT, {"value": "hero/approved"}, title=SHARED_TEXTS["approved"]),
        Node("review", TEXT, {"value": "hero/review"}, title=SHARED_TEXTS["review"]),
        Node("folder", SWITCH),
        Node("save", SAVE_IMAGE),
    ),
    links=(
        ("describe.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "read.answers"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
    ),
    columns=(("describe",), ("situation", "decide", "read"), ("approved", "review", "folder"), ("save",)),
    inputs=(
        ("brief", "situation.values.a"),
        ("image", "describe.model.images.image_1"),
        ("image", "save.images"),
        ("scores", "situation.values.c"),
        ("questions", "decide.questions"),
        ("approved", "approved.value"),
        ("review", "review.value"),
    ),
    outputs=(("summary", "decide.summary"),),
    description=HERO_TEXTS["check_description"],
    previews=(("save", IMAGE_PREVIEW),),
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
            title=SHARED_TEXTS["brief"],
        ),
        Node("rank", RANK_IMAGES.name),
        Node(
            "ready",
            QUESTION,
            {
                "name": "ready",
                "instructions": (
                    "Does the image work as a homepage hero: a clear subject, open space for a headline, and no "
                    "visible defects?"
                ),
            },
        ),
        Node("check", CHECK_HERO.name),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("brief.STRING", "rank.brief"),
        ("brief.STRING", "check.brief"),
        ("rank.image", "check.image"),
        ("rank.scores", "check.scores"),
        ("ready.questions", "check.questions"),
        ("check.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",),), note=HERO_TEXTS["input"]),),
        (Group(SHARED_TEXTS["rank"], (("rank",),), STAGE_COLOUR, HERO_TEXTS["rank"]),),
        (Group(SHARED_TEXTS["check"], (("ready",), ("check", "summary")), STAGE_COLOUR, HERO_TEXTS["check"]),),
    ),
    subgraphs=(RANK_IMAGES, CHECK_HERO),
)

SEARCH_WORKFLOWS = (ANSWER_FROM_ARTICLES, CHOOSE_HERO_IMAGE)

__all__ = ["SEARCH_WORKFLOWS"]
