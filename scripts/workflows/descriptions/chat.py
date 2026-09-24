"""The chat workflows: questions, images, documents, conversations and spoken answers."""

from __future__ import annotations

import json
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import (
    FIELD,
    IMAGE,
    PREVIEW,
    SAVE_IMAGE,
    FOLDER_IMAGES,
    PREVIEW_AUDIO,
    SAVE_CAPTIONS,
)

ASK = f"{NODE_PREFIX}ChatAsk"
ANSWER_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {"name": {"type": "string"}, "price": {"type": "string"}},
        "required": ["name", "price"],
        "additionalProperties": False,
    },
    indent=2,
)

ASK_A_QUESTION = Workflow(
    slug="chat-01-ask-a-question",
    nodes=(
        Node("ask", ASK, {"prompt": "Explain in three sentences how a rainbow forms."}, is_paid=True),
        Node("answer", PREVIEW),
    ),
    links=(("ask.text", "answer.source"),),
    stacks=((Group(SHARED_TEXTS["ask"], (("ask",), ("answer",)), STAGE_COLOUR),),),
)

DESCRIBE_AN_IMAGE = Workflow(
    slug="chat-02-describe-an-image",
    nodes=(
        Node("photo", IMAGE, {"image": ""}),
        Node("ask", ASK, {"prompt": "Describe this image in one paragraph."}, is_paid=True),
        Node("answer", PREVIEW),
    ),
    links=(("photo.IMAGE", "ask.model.images.image_1"), ("ask.text", "answer.source")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo",),)),),
        (Group(SHARED_TEXTS["ask"], (("ask",), ("answer",)), STAGE_COLOUR),),
    ),
)

CAPTION_A_FOLDER = Workflow(
    slug="chat-03-caption-a-folder",
    nodes=(
        Node("folder", FOLDER_IMAGES, {"folder": ""}),
        Node(
            "caption",
            ASK,
            {"prompt": ("Write a one-sentence training caption for this image. Describe only what is visible.")},
            is_paid=True,
        ),
        Node("save", SAVE_CAPTIONS, {"folder_name": "openrouter-captions"}),
    ),
    links=(
        ("folder.images", "caption.model.images.image_1"),
        ("folder.images", "save.images"),
        ("caption.text", "save.texts"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("folder",),)),),
        (Group(SHARED_TEXTS["ask"], (("caption",), ("save",)), STAGE_COLOUR),),
    ),
)

COMPARE_TWO_IMAGES = Workflow(
    slug="chat-04-compare-two-images",
    nodes=(
        Node("before", IMAGE, {"image": ""}, title="Before"),
        Node("after", IMAGE, {"image": ""}, title="After"),
        Node("ask", ASK, {"prompt": "List every difference between the first and the second image."}, is_paid=True),
        Node("answer", PREVIEW),
    ),
    links=(
        ("before.IMAGE", "ask.model.images.image_1"),
        ("after.IMAGE", "ask.model.images.image_2"),
        ("ask.text", "answer.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("before", "after"),)),),
        (Group(SHARED_TEXTS["ask"], (("ask",), ("answer",)), STAGE_COLOUR),),
    ),
)

SUMMARIZE_A_DOCUMENT = Workflow(
    slug="chat-05-summarize-a-document",
    nodes=(
        Node("document", f"{NODE_PREFIX}ChatAttachDocument", {"file": ""}),
        Node("ask", ASK, {"prompt": "Summarize this document in five bullet points."}, is_paid=True),
        Node("answer", PREVIEW),
    ),
    links=(("document.documents", "ask.documents"), ("ask.text", "answer.source")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("document",),)),),
        (Group(SHARED_TEXTS["ask"], (("ask",), ("answer",)), STAGE_COLOUR),),
    ),
)

IMPROVE_A_PROMPT = Workflow(
    slug="chat-06-improve-a-prompt",
    nodes=(
        Node(
            "write",
            ASK,
            {
                "prompt": "A cozy cabin in the snow at night.",
                "system": "You write prompts for image models. Answer with the prompt only.",
            },
            is_paid=True,
        ),
        Node("prompt", PREVIEW),
        Node("image", f"{NODE_PREFIX}ImageGenerate", is_paid=True),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/chat-06-improve-a-prompt"}),
    ),
    links=(("write.text", "image.prompt"), ("write.text", "prompt.source"), ("image.images", "save.images")),
    stacks=(
        (Group(SHARED_TEXTS["ask"], (("write",), ("prompt",)), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["image"], (("image",), ("save",)), STAGE_COLOUR),),
    ),
)

READ_PHOTO_FIELDS = Workflow(
    slug="chat-07-read-fields-from-a-photo",
    nodes=(
        Node("photo", IMAGE, {"image": ""}),
        Node(
            "ask",
            ASK,
            {"prompt": "Read the product name and price from this photo.", "model.answer_schema": ANSWER_SCHEMA},
            is_paid=True,
        ),
        Node("name", FIELD, {"key": "name"}),
        Node("price", FIELD, {"key": "price"}),
        Node("product", PREVIEW, title="Product"),
        Node("cost", PREVIEW, title="Price"),
    ),
    links=(
        ("photo.IMAGE", "ask.model.images.image_1"),
        ("ask.text", "name.json_string"),
        ("ask.text", "price.json_string"),
        ("name.STRING", "product.source"),
        ("price.STRING", "cost.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo",),)),),
        (Group(SHARED_TEXTS["ask"], (("ask",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["answer"], (("name", "price"), ("product", "cost"))),),
    ),
)

HOLD_A_CONVERSATION = Workflow(
    slug="chat-08-hold-a-conversation",
    nodes=(
        Node("first", ASK, {"prompt": "Suggest a name for a friendly robot."}, is_paid=True),
        Node("second", ASK, {"prompt": "Now write a two-line poem about it."}, is_paid=True),
        Node("answer", PREVIEW),
    ),
    links=(("first.conversation", "second.conversation"), ("second.text", "answer.source")),
    stacks=((Group(SHARED_TEXTS["ask"], (("first",), ("second",), ("answer",)), STAGE_COLOUR),),),
)

ANSWER_OUT_LOUD = Workflow(
    slug="chat-09-answer-out-loud",
    nodes=(
        Node(
            "ask",
            ASK,
            {"model": "openai/gpt-audio-mini", "prompt": "Tell a two-sentence story about a lighthouse."},
            is_paid=True,
        ),
        Node("listen", PREVIEW_AUDIO),
        Node("transcript", PREVIEW),
    ),
    links=(("ask.audio", "listen.audio"), ("ask.text", "transcript.source")),
    stacks=((Group(SHARED_TEXTS["ask"], (("ask",), ("listen", "transcript")), STAGE_COLOUR),),),
)

CHAT_WORKFLOWS = (
    ASK_A_QUESTION,
    DESCRIBE_AN_IMAGE,
    CAPTION_A_FOLDER,
    COMPARE_TWO_IMAGES,
    SUMMARIZE_A_DOCUMENT,
    IMPROVE_A_PROMPT,
    READ_PHOTO_FIELDS,
    HOLD_A_CONVERSATION,
    ANSWER_OUT_LOUD,
)

__all__ = ["CHAT_WORKFLOWS"]
