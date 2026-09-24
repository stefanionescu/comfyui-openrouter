"""The design workflows: Jev picks the edit idea or logo prompt a chat model writes, and an image model draws it."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.workflows.descriptions.schemas import numbered_schema
from scripts.config import (
    TEXT,
    FIELD,
    IMAGE,
    FORMAT,
    SWITCH,
    PREVIEW,
    SAVE_SVG,
    JOIN_ALPHA,
    MASK_IMAGE,
    SAVE_IMAGE,
    TEXT_BLOCK,
    PREVIEW_IMAGE,
)

ASK = f"{NODE_PREFIX}ChatAsk"
GENERATE = f"{NODE_PREFIX}ImageGenerate"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
WRITER = "openai/gpt-6-sol"
GPT_IMAGE = "openai/gpt-image-2.5-flare"

EDIT_BEST_IDEA = Workflow(
    slug="image-03-edit-with-the-best-idea",
    nodes=(
        Node("photo", IMAGE, {"image": ""}, title="Product Photo"),
        Node(
            "campaign",
            TEXT_BLOCK,
            {"value": "Autumn sale for young city commuters. Warm evening light, a sense of movement, premium feel."},
            title="Campaign",
        ),
        Node(
            "best",
            QUESTION,
            {
                "name": "best_idea",
                "instructions": "Which editing idea fits the campaign best while keeping the product unchanged?",
                "answer_type": "one choice",
                "answer_type.options": "idea_1\nidea_2\nidea_3",
            },
            title="Best Idea",
        ),
        Node(
            "on_brief",
            QUESTION,
            {"name": "on_brief", "instructions": "Does the chosen idea suit the campaign?"},
            title="On Brief",
        ),
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "Campaign: {a}\n\nWrite three different ideas for editing this product photo into a campaign "
                    "image. Each idea is one detailed editing instruction that keeps the product exactly as it is."
                )
            },
            title="Idea Request",
        ),
        Node(
            "ideas",
            ASK,
            {"model": WRITER, "model.answer_schema": numbered_schema("idea", 3)},
            title="Write Edit Ideas",
            is_paid=True,
        ),
        Node("situation", FORMAT, {"f_string": "Campaign:\n{a}\n\nIdeas:\n{b}"}, title="Campaign and Ideas"),
        Node("decide", DECIDE, title="Choose an Idea", is_paid=True),
        Node("read_best", READ, {"question": "best_idea"}, title="Read Best Idea"),
        Node("read_brief", READ, {"question": "on_brief"}, title="Read On Brief"),
        Node("idea", FIELD, title="Extract the Idea"),
        Node(
            "edit",
            GENERATE,
            {"model": GPT_IMAGE, "model.quality": "medium"},
            title="Apply the Idea",
            is_paid=True,
        ),
        Node("chosen", PREVIEW, title="Chosen Idea"),
        Node("approved", TEXT, {"value": "campaign/approved"}, title="Approved Folder"),
        Node("review", TEXT, {"value": "campaign/review"}, title="Review Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_IMAGE, title="Save the Edit"),
    ),
    links=(
        ("campaign.STRING", "request.values.a"),
        ("campaign.STRING", "situation.values.a"),
        ("request.STRING", "ideas.prompt"),
        ("photo.IMAGE", "ideas.model.images.image_1"),
        ("ideas.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("best.questions", "on_brief.questions"),
        ("on_brief.questions", "decide.questions"),
        ("decide.answers", "read_best.answers"),
        ("decide.answers", "read_brief.answers"),
        ("ideas.text", "idea.json_string"),
        ("read_best.answer", "idea.key"),
        ("idea.STRING", "edit.prompt"),
        ("idea.STRING", "chosen.source"),
        ("photo.IMAGE", "edit.model.references.reference_1"),
        ("read_brief.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("edit.images", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo", "campaign"), ("best", "on_brief"))),),
        (
            Group(
                SHARED_TEXTS["choose"],
                (("request", "ideas"), ("situation", "decide"), ("read_best", "read_brief", "idea")),
                STAGE_COLOUR,
            ),
        ),
        (Group(SHARED_TEXTS["edit"], (("edit", "chosen"), ("approved", "review", "folder", "save")), STAGE_COLOUR),),
    ),
)

DESIGN_LOGO = Workflow(
    slug="image-04-design-a-logo",
    nodes=(
        Node(
            "brand",
            TEXT_BLOCK,
            {
                "value": (
                    "Fernwood, a small tea shop in an old greenhouse. Calm, hand-made, a little botanical. "
                    "The logo must read well at the size of a coffee-cup sleeve."
                )
            },
            title="Brand Brief",
        ),
        Node(
            "best",
            QUESTION,
            {
                "name": "best_prompt",
                "instructions": "Which prompt will give the simplest, most memorable logo for this brand?",
                "answer_type": "one choice",
                "answer_type.options": "prompt_1\nprompt_2\nprompt_3",
            },
            title="Best Prompt",
        ),
        Node(
            "prompts",
            ASK,
            {
                "model": WRITER,
                "model.answer_schema": numbered_schema("prompt", 3),
                "system": (
                    "Write three different prompts for a flat, two-colour logo mark for the brand the person "
                    "describes. Each prompt describes one simple symbol and its colours, with no text in the mark."
                ),
            },
            title="Write Logo Prompts",
            is_paid=True,
        ),
        Node("situation", FORMAT, {"f_string": "Brand:\n{a}\n\nPrompts:\n{b}"}, title="Brand and Prompts"),
        Node("decide", DECIDE, title="Choose a Prompt", is_paid=True),
        Node("read", READ, {"question": "best_prompt"}, title="Read Best Prompt"),
        Node("prompt", FIELD, title="Extract the Prompt"),
        Node(
            "vector",
            GENERATE,
            {"model": "recraft/recraft-v4.1-vector", "model.aspect_ratio": "1:1"},
            title="Vector Logo",
            is_paid=True,
        ),
        Node(
            "sticker",
            GENERATE,
            {
                "model": GPT_IMAGE,
                "model.aspect_ratio": "1:1",
                "model.background": "transparent",
                "model.quality": "medium",
            },
            title="Sticker",
            is_paid=True,
        ),
        Node("save_vector", SAVE_SVG, {"filename_prefix": "logo/fernwood"}, title="Save Logo"),
        Node("join", JOIN_ALPHA, title="Add Transparency"),
        Node("save_sticker", SAVE_IMAGE, {"filename_prefix": "logo/fernwood-sticker"}, title="Save Sticker"),
        Node("mask", MASK_IMAGE, title="Mask as Image"),
        Node("preview_mask", PREVIEW_IMAGE, title="Sticker Mask"),
    ),
    links=(
        ("brand.STRING", "prompts.prompt"),
        ("brand.STRING", "situation.values.a"),
        ("prompts.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("best.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("prompts.text", "prompt.json_string"),
        ("read.answer", "prompt.key"),
        ("prompt.STRING", "vector.prompt"),
        ("prompt.STRING", "sticker.prompt"),
        ("vector.svg", "save_vector.svg"),
        ("sticker.images", "join.image"),
        ("sticker.masks", "join.alpha"),
        ("join.IMAGE", "save_sticker.images"),
        ("sticker.masks", "mask.mask"),
        ("mask.IMAGE", "preview_mask.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brand", "best"),)),),
        (Group(SHARED_TEXTS["choose"], (("prompts", "situation"), ("decide", "read", "prompt")), STAGE_COLOUR),),
        (
            Group(
                SHARED_TEXTS["logo"],
                (("vector", "save_vector"), ("sticker", "join", "save_sticker"), ("mask", "preview_mask")),
                STAGE_COLOUR,
            ),
        ),
    ),
)

DESIGN_WORKFLOWS = (EDIT_BEST_IDEA, DESIGN_LOGO)

__all__ = ["DESIGN_WORKFLOWS"]
