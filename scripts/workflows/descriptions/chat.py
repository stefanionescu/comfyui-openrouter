"""The chat workflows: write a product listing Jev fact-checks, and caption a training set Jev reviews."""

from __future__ import annotations

import json
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import (
    TEXT,
    IMAGE,
    FORMAT,
    SWITCH,
    PREVIEW,
    SAVE_TEXT,
    FOLDER_IMAGES,
    SAVE_CAPTIONS,
)

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

WRITE_LISTING = Workflow(
    slug="chat-01-write-a-product-listing",
    nodes=(
        Node("front", IMAGE, {"image": ""}, title="Product Photo (Front)"),
        Node("detail", IMAGE, {"image": ""}, title="Product Photo (Detail)"),
        Node("spec", f"{NODE_PREFIX}ChatAttachDocument", {"file": ""}, title="Spec Sheet"),
        Node("private", f"{NODE_PREFIX}RequestOptions", {"data_collection": "deny"}, title="Keep Data Private"),
        Node(
            "write",
            ASK,
            {
                "model": WRITER,
                "model.answer_schema": LISTING_SCHEMA,
                "prompt": (
                    "Write a marketplace listing for this product from the photos and the spec sheet. Use only "
                    "facts you can see or read. Keep the title under 80 characters and write five bullet points."
                ),
            },
            title="Write the Listing",
            is_paid=True,
        ),
        Node(
            "facts",
            ASK,
            {
                "model": READER,
                "prompt": "List every fact in this spec sheet, one short line each. Add nothing else.",
            },
            title="List the Spec Facts",
            is_paid=True,
        ),
        Node(
            "supported",
            QUESTION,
            {
                "name": "supported",
                "instructions": "Is every claim in the listing backed by the spec facts or plainly visible?",
                "answer_type.yes_means": "Every claim is backed.",
                "answer_type.no_means": "At least one claim is invented or exaggerated.",
            },
            title="Supported",
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
            title="Persuasive",
        ),
        Node("situation", FORMAT, {"f_string": "Spec facts:\n{a}\n\nListing:\n{b}"}, title="Facts and Listing"),
        Node("decide", DECIDE, title="Check the Listing", is_paid=True),
        Node("read", READ, {"question": "supported"}, title="Read Supported"),
        Node("approved", TEXT, {"value": "listings/approved"}, title="Approved Folder"),
        Node("review", TEXT, {"value": "listings/review"}, title="Review Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_TEXT, {"format": "json"}, title="Save the Listing"),
        Node("summary", PREVIEW, title="Check Summary"),
    ),
    links=(
        ("front.IMAGE", "write.model.images.image_1"),
        ("detail.IMAGE", "write.model.images.image_2"),
        ("spec.documents", "write.documents"),
        ("spec.documents", "facts.documents"),
        ("private.options", "write.options"),
        ("facts.text", "situation.values.a"),
        ("write.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("supported.questions", "persuasive.questions"),
        ("persuasive.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("decide.summary", "summary.source"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("write.text", "save.text"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("front", "detail"), ("spec", "private"))),),
        (Group(SHARED_TEXTS["write"], (("write",), ("facts",)), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["check"], (("supported", "persuasive"), ("situation", "decide", "read")), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["save"], (("approved", "review", "folder"), ("save", "summary"))),),
    ),
)

CAPTION_SET = Workflow(
    slug="chat-02-caption-a-training-set",
    nodes=(
        Node("folder", FOLDER_IMAGES, {"folder": ""}, title="Training Images"),
        Node(
            "caption",
            ASK,
            {
                "model": READER,
                "prompt": (
                    "Write a one-sentence training caption for this image. Name only what is visible: subject, "
                    "setting, lighting, and style. No opinions."
                ),
            },
            title="Caption Each Image",
            is_paid=True,
        ),
        Node(
            "rules",
            QUESTION,
            {
                "name": "follows_rules",
                "instructions": (
                    "Is the caption one sentence that describes only visible content, without opinions or guesses?"
                ),
            },
            title="Caption Rules",
        ),
        Node("decide", DECIDE, title="Check Each Caption", is_paid=True),
        Node("save", SAVE_CAPTIONS, {"folder_name": "captions"}, title="Save Captions"),
        Node("verdicts", PREVIEW, title="Caption Verdicts"),
    ),
    links=(
        ("folder.images", "caption.model.images.image_1"),
        ("folder.images", "save.images"),
        ("caption.text", "save.texts"),
        ("caption.text", "decide.situation"),
        ("rules.questions", "decide.questions"),
        ("decide.summary", "verdicts.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("folder",),)),),
        (Group(SHARED_TEXTS["write"], (("caption", "save"),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["check"], (("rules",), ("decide", "verdicts")), STAGE_COLOUR),),
    ),
)

CHAT_WORKFLOWS = (WRITE_LISTING, CAPTION_SET)

__all__ = ["CHAT_WORKFLOWS"]
