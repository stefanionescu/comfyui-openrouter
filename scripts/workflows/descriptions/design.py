"""The design workflows: Jev picks the edit idea or logo prompt a chat model writes, and an image model draws it."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.schemas import build_numbered_schema
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow

ASK = f"{NODE_PREFIX}ChatAsk"
GENERATE = f"{NODE_PREFIX}ImageGenerate"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
WRITER = "openai/gpt-6-sol"
GPT_IMAGE = "openai/gpt-image-2.5-flare"
EDIT_TEXTS = WORKFLOW_TEXTS["image-03-edit-with-the-best-idea"]
LOGO_TEXTS = WORKFLOW_TEXTS["image-04-design-a-logo"]

IDEAS = Subgraph(
    name=SHARED_TEXTS["ideas"],
    nodes=(
        Node(
            "request",
            HostNode.FORMAT,
            {
                "f_string": (
                    "Campaign: {a}\n\nWrite three different ideas for editing this product photo into a campaign "
                    "image. Each idea is one detailed editing instruction that keeps the product exactly as it is."
                )
            },
        ),
        Node("ideas", ASK, {"model": WRITER, "answer_schema": build_numbered_schema("idea", 3)}, is_paid=True),
    ),
    links=(("request.STRING", "ideas.prompt"),),
    columns=(("request",), ("ideas",)),
    inputs=(("image", "ideas.images"), ("campaign", "request.values.a")),
    outputs=(("ideas", "ideas.text"),),
    description=EDIT_TEXTS["ideas_description"],
)

CHOOSE_IDEA = Subgraph(
    name=SHARED_TEXTS["choose"],
    nodes=(
        Node("situation", HostNode.FORMAT, {"f_string": "Campaign:\n{a}\n\nIdeas:\n{b}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("best", READ, {"question": "best"}),
        Node("on_brief", READ, {"question": "on_brief"}),
        Node("idea", HostNode.FIELD),
    ),
    links=(
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "best.answers"),
        ("decide.answers", "on_brief.answers"),
        ("best.answer", "idea.key"),
    ),
    columns=(("situation", "decide"), ("best", "on_brief"), ("idea",)),
    inputs=(
        ("campaign", "situation.values.a"),
        ("ideas", "idea.json_string"),
        ("ideas", "situation.values.b"),
        ("questions", "decide.questions"),
    ),
    outputs=(("idea", "idea.STRING"), ("on_brief", "on_brief.is_yes"), ("summary", "decide.summary")),
    description=EDIT_TEXTS["choose_description"],
)

EDIT = Subgraph(
    name=SHARED_TEXTS["edit"],
    nodes=(
        Node("edit", GENERATE, {"model": GPT_IMAGE, "quality": "medium"}, is_paid=True),
        Node("approved", HostNode.TEXT, {"value": "campaign/approved"}, title=SHARED_TEXTS["approved"]),
        Node("review", HostNode.TEXT, {"value": "campaign/review"}, title=SHARED_TEXTS["review"]),
        Node("folder", HostNode.SWITCH),
        Node("save", HostNode.SAVE_IMAGE),
    ),
    links=(
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("edit.images", "save.images"),
    ),
    columns=(("edit",), ("approved", "review", "folder"), ("save",)),
    inputs=(
        ("image", "edit.references"),
        ("idea", "edit.prompt"),
        ("on_brief", "folder.switch"),
        ("approved", "approved.value"),
        ("review", "review.value"),
    ),
    description=EDIT_TEXTS["edit_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

EDIT_BEST_IDEA = Workflow(
    slug="image-03-edit-with-the-best-idea",
    nodes=(
        Node("photo", HostNode.IMAGE, {"image": ""}),
        Node(
            "campaign",
            HostNode.TEXT_BLOCK,
            {"value": "Autumn sale for young city commuters. Warm evening light, a sense of movement, premium feel."},
            title=SHARED_TEXTS["campaign"],
        ),
        Node("ideas", IDEAS.name),
        Node(
            "best",
            QUESTION,
            {
                "name": "best",
                "instructions": "Which editing idea fits the campaign best while keeping the product unchanged?",
                "answer_type": "one choice",
                "answer_type.options": "idea_1\nidea_2\nidea_3",
            },
        ),
        Node(
            "on_brief",
            QUESTION,
            {"name": "on_brief", "instructions": "Does the chosen idea suit the campaign?"},
        ),
        Node("choose", CHOOSE_IDEA.name),
        Node("idea", HostNode.PREVIEW, title=SHARED_TEXTS["idea"]),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("edit", EDIT.name),
    ),
    links=(
        ("photo.IMAGE", "ideas.image"),
        ("campaign.STRING", "ideas.campaign"),
        ("campaign.STRING", "choose.campaign"),
        ("ideas.ideas", "choose.ideas"),
        ("best.questions", "on_brief.questions"),
        ("on_brief.questions", "choose.questions"),
        ("choose.idea", "idea.source"),
        ("choose.summary", "summary.source"),
        ("photo.IMAGE", "edit.image"),
        ("choose.idea", "edit.idea"),
        ("choose.on_brief", "edit.on_brief"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo", "campaign"),), note=EDIT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["ideas"], (("ideas",),), STAGE_COLOUR, EDIT_TEXTS["ideas"]),),
        (
            Group(
                SHARED_TEXTS["choose"],
                (("best", "on_brief"), ("choose", "idea"), ("summary",)),
                STAGE_COLOUR,
                EDIT_TEXTS["choose"],
            ),
        ),
        (Group(SHARED_TEXTS["edit"], (("edit",),), STAGE_COLOUR, EDIT_TEXTS["edit"]),),
    ),
    subgraphs=(IDEAS, CHOOSE_IDEA, EDIT),
)

PROMPTS = Subgraph(
    name=SHARED_TEXTS["prompts"],
    nodes=(
        Node(
            "prompts",
            ASK,
            {
                "model": WRITER,
                "answer_schema": build_numbered_schema("prompt", 3),
                "system_prompt": (
                    "Write three different prompts for a flat, two-colour logo mark for the brand the person "
                    "describes. Each prompt describes one simple symbol and its colours, with no text in the mark."
                ),
            },
            is_paid=True,
        ),
        Node("situation", HostNode.FORMAT, {"f_string": "Brand:\n{a}\n\nPrompts:\n{b}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("best", READ, {"question": "best"}),
        Node("prompt", HostNode.FIELD),
    ),
    links=(
        ("prompts.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "best.answers"),
        ("prompts.text", "prompt.json_string"),
        ("best.answer", "prompt.key"),
    ),
    columns=(("prompts",), ("situation", "decide"), ("best", "prompt")),
    inputs=(("brand", "prompts.prompt"), ("brand", "situation.values.a"), ("questions", "decide.questions")),
    outputs=(("prompt", "prompt.STRING"), ("summary", "decide.summary")),
    description=LOGO_TEXTS["prompts_description"],
)

SVG = Subgraph(
    name=SHARED_TEXTS["svg"],
    nodes=(
        Node(
            "svg",
            GENERATE,
            {"model": "recraft/recraft-v4.1-vector", "aspect_ratio": "1:1"},
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_SVG, {"filename_prefix": "logo/fernwood"}),
    ),
    links=(("svg.svg", "save.svg"),),
    columns=(("svg",), ("save",)),
    inputs=(("prompt", "svg.prompt"),),
    description=LOGO_TEXTS["svg_description"],
)

PNG = Subgraph(
    name=SHARED_TEXTS["png"],
    nodes=(
        Node(
            "png",
            GENERATE,
            {
                "model": GPT_IMAGE,
                "aspect_ratio": "1:1",
                "background": "transparent",
                "quality": "medium",
            },
            is_paid=True,
        ),
        Node("join", HostNode.JOIN_ALPHA),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "logo/fernwood"}),
        Node("mask", HostNode.MASK_IMAGE),
        Node("preview", HostNode.PREVIEW_IMAGE, title=SHARED_TEXTS["mask"]),
    ),
    links=(
        ("png.images", "join.image"),
        ("png.masks", "join.alpha"),
        ("join.IMAGE", "save.images"),
        ("png.masks", "mask.mask"),
        ("mask.IMAGE", "preview.images"),
    ),
    columns=(("png",), ("join", "mask"), ("save", "preview")),
    inputs=(("prompt", "png.prompt"),),
    description=LOGO_TEXTS["png_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

DESIGN_LOGO = Workflow(
    slug="image-04-design-a-logo",
    nodes=(
        Node(
            "brand",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "Fernwood, a small tea shop in an old greenhouse. Calm, hand-made, a little botanical. "
                    "The logo must read well at the size of a coffee-cup sleeve."
                )
            },
            title=SHARED_TEXTS["brand"],
        ),
        Node(
            "best",
            QUESTION,
            {
                "name": "best",
                "instructions": "Which prompt will give the simplest, most memorable logo for this brand?",
                "answer_type": "one choice",
                "answer_type.options": "prompt_1\nprompt_2\nprompt_3",
            },
        ),
        Node("prompts", PROMPTS.name),
        Node("prompt", HostNode.PREVIEW, title=SHARED_TEXTS["prompt"]),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("svg", SVG.name),
        Node("png", PNG.name),
    ),
    links=(
        ("brand.STRING", "prompts.brand"),
        ("best.questions", "prompts.questions"),
        ("prompts.prompt", "prompt.source"),
        ("prompts.summary", "summary.source"),
        ("prompts.prompt", "svg.prompt"),
        ("prompts.prompt", "png.prompt"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brand",),), note=LOGO_TEXTS["input"]),),
        (
            Group(
                SHARED_TEXTS["prompts"],
                (("best", "prompts"), ("prompt", "summary")),
                STAGE_COLOUR,
                LOGO_TEXTS["prompts"],
            ),
        ),
        (Group(SHARED_TEXTS["svg"], (("svg",),), STAGE_COLOUR, LOGO_TEXTS["svg"]),),
        (Group(SHARED_TEXTS["png"], (("png",),), STAGE_COLOUR, LOGO_TEXTS["png"]),),
    ),
    subgraphs=(PROMPTS, SVG, PNG),
)

DESIGN_WORKFLOWS = (EDIT_BEST_IDEA, DESIGN_LOGO)

__all__ = ["DESIGN_WORKFLOWS"]
