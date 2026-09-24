"""The chat workflows: write a product listing Jev fact-checks, and caption a training set Jev reviews."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, TEXT_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow

ASK = f"{NODE_PREFIX}ChatAsk"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
WRITER = "openai/gpt-6-sol"
READER = "openai/gpt-6-luna"
LISTING_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "bullets": {"type": "array", "items": {"type": "string"}},
            "price": {"type": "string"},
        },
        "required": ["title", "bullets", "price"],
        "additionalProperties": False,
    },
    indent=2,
)
CAPTIONS_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {"captions": {"type": "array", "items": {"type": "string"}}},
        "required": ["captions"],
        "additionalProperties": False,
    },
    indent=2,
)
LISTING_TEXTS = WORKFLOW_TEXTS["chat-01-write-a-product-listing"]
CAPTION_TEXTS = WORKFLOW_TEXTS["chat-02-caption-a-training-set"]

WRITE = Subgraph(
    name=SHARED_TEXTS["write"],
    nodes=(
        Node("photos", HostNode.CREATE_LIST),
        Node(
            "listing",
            ASK,
            {
                "model": WRITER,
                "answer_schema": LISTING_SCHEMA,
                "prompt": (
                    "Write a marketplace listing for this product from the photos and the spec sheet. Use only "
                    "facts you can see or read. Keep the title under 80 characters and write five bullet points."
                ),
            },
            title=SHARED_TEXTS["listing"],
            is_paid=True,
        ),
        Node(
            "facts",
            ASK,
            {"model": READER, "prompt": "List every fact in this spec sheet, one short line each. Add nothing else."},
            title=SHARED_TEXTS["facts"],
            is_paid=True,
        ),
    ),
    links=(("photos.list", "listing.images"),),
    columns=(("photos",), ("listing",), ("facts",)),
    inputs=(
        ("front", "photos.inputs.input0"),
        ("detail", "photos.inputs.input1"),
        ("documents", "listing.documents"),
        ("documents", "facts.documents"),
        ("options", "listing.options"),
    ),
    outputs=(("listing", "listing.text"), ("facts", "facts.text")),
    description=LISTING_TEXTS["write_description"],
)

CHECK_LISTING = Subgraph(
    name=SHARED_TEXTS["check"],
    nodes=(
        Node("situation", HostNode.FORMAT, {"f_string": "Spec facts:\n{a}\n\nListing:\n{b}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("read", READ, {"question": "supported"}),
        Node("approved", HostNode.TEXT, {"value": "listings/approved"}, title=SHARED_TEXTS["approved"]),
        Node("review", HostNode.TEXT, {"value": "listings/review"}, title=SHARED_TEXTS["review"]),
        Node("folder", HostNode.SWITCH),
        Node("save", HostNode.SAVE_TEXT, {"format": "json"}),
    ),
    links=(
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "read.answers"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
    ),
    columns=(("situation", "decide"), ("read", "approved", "review"), ("folder", "save")),
    inputs=(
        ("facts", "situation.values.a"),
        ("listing", "save.text"),
        ("listing", "situation.values.b"),
        ("questions", "decide.questions"),
        ("approved", "approved.value"),
        ("review", "review.value"),
    ),
    outputs=(("summary", "decide.summary"),),
    description=LISTING_TEXTS["check_description"],
    previews=(("save", TEXT_PREVIEW),),
)

WRITE_LISTING = Workflow(
    slug="chat-01-write-a-product-listing",
    nodes=(
        Node("front", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["front"]),
        Node("detail", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["detail"]),
        Node("spec", f"{NODE_PREFIX}ChatAttachDocument", {"file": ""}),
        Node("private", f"{NODE_PREFIX}RequestOptions", {"data_collection": "deny"}),
        Node("write", WRITE.name),
        Node(
            "supported",
            QUESTION,
            {
                "name": "supported",
                "instructions": "Is every claim in the listing backed by the spec facts or plainly visible?",
                "answer_type.yes_means": "Every claim is backed.",
                "answer_type.no_means": "At least one claim is invented or exaggerated.",
            },
        ),
        Node(
            "persuasive",
            QUESTION,
            {
                "name": "persuasive",
                "instructions": "How persuasive is the listing for a shopper comparing similar products?",
                "answer_type": "score",
                "answer_type.levels": "Flat\nClear\nCompelling",
            },
        ),
        Node("check", CHECK_LISTING.name),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("front.IMAGE", "write.front"),
        ("detail.IMAGE", "write.detail"),
        ("spec.documents", "write.documents"),
        ("private.options", "write.options"),
        ("write.facts", "check.facts"),
        ("write.listing", "check.listing"),
        ("supported.questions", "persuasive.questions"),
        ("persuasive.questions", "check.questions"),
        ("check.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("front", "detail"), ("spec", "private")), note=LISTING_TEXTS["input"]),),
        (Group(SHARED_TEXTS["write"], (("write",),), STAGE_COLOUR, LISTING_TEXTS["write"]),),
        (
            Group(
                SHARED_TEXTS["check"],
                (("supported", "persuasive"), ("check", "summary")),
                STAGE_COLOUR,
                LISTING_TEXTS["check"],
            ),
        ),
    ),
    subgraphs=(WRITE, CHECK_LISTING),
)

CAPTION = Subgraph(
    name=SHARED_TEXTS["caption"],
    nodes=(
        Node(
            "caption",
            ASK,
            {
                "model": READER,
                "answer_schema": CAPTIONS_SCHEMA,
                "prompt": (
                    "Write one training caption for each image, in the order given. Each caption is one sentence "
                    "that names only what is visible: subject, setting, lighting, and style. No opinions."
                ),
            },
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_TEXT, {"filename_prefix": "captions/captions", "format": "json"}),
    ),
    links=(("caption.text", "save.text"),),
    columns=(("caption",), ("save",)),
    inputs=(("images", "caption.images"),),
    outputs=(("captions", "caption.text"),),
    description=CAPTION_TEXTS["caption_description"],
)

CAPTION_SET = Workflow(
    slug="chat-02-caption-a-training-set",
    nodes=(
        Node("folder", HostNode.FOLDER_IMAGES, {"folder": ""}),
        Node("caption", CAPTION.name),
        Node(
            "valid",
            QUESTION,
            {
                "name": "valid",
                "instructions": (
                    "Is every caption one sentence that describes only visible content, without opinions or guesses?"
                ),
            },
        ),
        Node("decide", DECIDE, is_paid=True),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("folder.images", "caption.images"),
        ("caption.captions", "decide.situation"),
        ("valid.questions", "decide.questions"),
        ("decide.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("folder",),), note=CAPTION_TEXTS["input"]),),
        (Group(SHARED_TEXTS["caption"], (("caption",),), STAGE_COLOUR, CAPTION_TEXTS["caption"]),),
        (Group(SHARED_TEXTS["check"], (("valid",), ("decide", "summary")), STAGE_COLOUR, CAPTION_TEXTS["check"]),),
    ),
    subgraphs=(CAPTION,),
)

CHAT_WORKFLOWS = (WRITE_LISTING, CAPTION_SET)

__all__ = ["CHAT_WORKFLOWS"]
