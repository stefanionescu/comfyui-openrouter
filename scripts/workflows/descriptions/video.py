"""The video workflows: animate a product shot with the camera move Jev picks, and recover a cancelled video."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.schemas import build_numbered_schema
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow

ANIMATE_TEXTS = WORKFLOW_TEXTS["video-01-animate-a-product-shot"]
RECOVER_TEXTS = WORKFLOW_TEXTS["video-02-recover-a-cancelled-video"]

MOVE = Subgraph(
    name=SHARED_TEXTS["move"],
    nodes=(
        Node(
            "moves",
            f"{NODE_PREFIX}ChatAsk",
            {
                "model": "openai/gpt-6-sol",
                "answer_schema": build_numbered_schema("move", 3),
                "prompt": (
                    "This still is the first frame of a six-second product teaser. Write three different camera "
                    "moves for it. Each is one sentence a video model can follow, such as a slow push-in."
                ),
            },
            is_paid=True,
        ),
        Node("situation", HostNode.FORMAT, {"f_string": "Product shot:\n{a}\n\nCamera moves:\n{b}"}),
        Node("decide", f"{NODE_PREFIX}DecisionAsk", is_paid=True),
        Node("best", f"{NODE_PREFIX}DecisionReadAnswer", {"question": "best"}),
        Node("move", HostNode.FIELD),
    ),
    links=(
        ("moves.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "best.answers"),
        ("moves.text", "move.json_string"),
        ("best.answer", "move.key"),
    ),
    columns=(("moves",), ("situation", "decide"), ("best", "move")),
    inputs=(
        ("brief", "situation.values.a"),
        ("image", "moves.images"),
        ("questions", "decide.questions"),
    ),
    outputs=(("move", "move.STRING"), ("summary", "decide.summary")),
    description=ANIMATE_TEXTS["move_description"],
)

ANIMATE = Subgraph(
    name=SHARED_TEXTS["animate"],
    nodes=(
        Node(
            "animate",
            f"{NODE_PREFIX}VideoGenerate",
            {
                "model": "minimax/hailuo-3-max",
                "duration": 6,
                "resolution": "768p",
                "aspect_ratio": "16:9",
            },
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/openrouter/product-teaser"}),
    ),
    links=(("animate.video", "save.video"),),
    columns=(("animate",), ("save",)),
    inputs=(("image", "animate.first_frame"), ("move", "animate.prompt")),
    description=ANIMATE_TEXTS["animate_description"],
)

ANIMATE_PRODUCT = Workflow(
    slug="video-01-animate-a-product-shot",
    nodes=(
        Node(
            "brief",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A matte black espresso machine on a marble counter, soft morning light from a window, steam "
                    "rising from a small cup, shallow depth of field"
                )
            },
            title=SHARED_TEXTS["brief"],
        ),
        Node(
            "draw",
            f"{NODE_PREFIX}ImageGenerate",
            {"model": "microsoft/mai-image-2.6-flash", "aspect_ratio": "16:9"},
            is_paid=True,
        ),
        Node("frame", HostNode.PREVIEW_IMAGE, title=SHARED_TEXTS["frame"]),
        Node(
            "best",
            f"{NODE_PREFIX}DecisionAddQuestion",
            {
                "name": "best",
                "instructions": (
                    "Which camera move best shows the product in a six-second teaser, keeping it sharp and centred?"
                ),
                "answer_type": "one choice",
                "answer_type.options": "move_1\nmove_2\nmove_3",
            },
        ),
        Node("move", MOVE.name),
        Node("chosen", HostNode.PREVIEW, title=SHARED_TEXTS["move"]),
        Node("summary", HostNode.PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("animate", ANIMATE.name),
    ),
    links=(
        ("brief.STRING", "draw.prompt"),
        ("draw.images", "frame.images"),
        ("brief.STRING", "move.brief"),
        ("draw.images", "move.image"),
        ("best.questions", "move.questions"),
        ("move.move", "chosen.source"),
        ("move.summary", "summary.source"),
        ("draw.images", "animate.image"),
        ("move.move", "animate.move"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",),), note=ANIMATE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["frame"], (("draw",), ("frame",)), STAGE_COLOUR, ANIMATE_TEXTS["frame"]),),
        (
            Group(
                SHARED_TEXTS["move"],
                (("best", "move"), ("chosen", "summary")),
                STAGE_COLOUR,
                ANIMATE_TEXTS["move"],
            ),
        ),
        (Group(SHARED_TEXTS["animate"], (("animate",),), STAGE_COLOUR, ANIMATE_TEXTS["animate"]),),
    ),
    subgraphs=(MOVE, ANIMATE),
)

RECOVER_VIDEO = Workflow(
    slug="video-02-recover-a-cancelled-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}VideoDownload", {"job": ""}),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/openrouter/recovered"}),
    ),
    links=(("download.video", "save.video"),),
    stacks=((Group(SHARED_TEXTS["recover"], (("download",), ("save",)), STAGE_COLOUR, RECOVER_TEXTS["recover"]),),),
)

VIDEO_WORKFLOWS = (ANIMATE_PRODUCT, RECOVER_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
