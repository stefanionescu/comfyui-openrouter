"""The video workflows: animate a product shot with the camera move Jev picks, and collect a job later."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.workflows.descriptions.schemas import numbered_schema
from scripts.config import FIELD, FORMAT, PREVIEW, SAVE_VIDEO, TEXT_BLOCK

ANIMATE_PRODUCT = Workflow(
    slug="video-01-animate-a-product-shot",
    nodes=(
        Node(
            "brief",
            TEXT_BLOCK,
            {
                "value": (
                    "A matte black espresso machine on a marble counter, soft morning light from a window, steam "
                    "rising from a small cup, shallow depth of field"
                )
            },
            title="Product Brief",
        ),
        Node(
            "best",
            f"{NODE_PREFIX}DecisionAddQuestion",
            {
                "name": "best_move",
                "instructions": (
                    "Which camera move best shows the product in a six-second teaser, keeping it sharp and centred?"
                ),
                "answer_type": "one choice",
                "answer_type.options": "move_1\nmove_2\nmove_3",
            },
            title="Best Move",
        ),
        Node(
            "frame",
            f"{NODE_PREFIX}ImageGenerate",
            {"model": "microsoft/mai-image-2.6-flash", "model.aspect_ratio": "16:9"},
            title="First Frame",
            is_paid=True,
        ),
        Node(
            "moves",
            f"{NODE_PREFIX}ChatAsk",
            {
                "model": "openai/gpt-6-sol",
                "model.answer_schema": numbered_schema("move", 3),
                "prompt": (
                    "This still is the first frame of a six-second product teaser. Write three different camera "
                    "moves for it. Each is one sentence a video model can follow, such as a slow push-in."
                ),
            },
            title="Write Camera Moves",
            is_paid=True,
        ),
        Node("situation", FORMAT, {"f_string": "Product shot:\n{a}\n\nCamera moves:\n{b}"}, title="Shot and Moves"),
        Node("decide", f"{NODE_PREFIX}DecisionAsk", title="Choose a Move", is_paid=True),
        Node("read", f"{NODE_PREFIX}DecisionReadAnswer", {"question": "best_move"}, title="Read Best Move"),
        Node("move", FIELD, title="Extract the Move"),
        Node("chosen", PREVIEW, title="Chosen Move"),
        Node(
            "animate",
            f"{NODE_PREFIX}VideoGenerate",
            {
                "model": "minimax/hailuo-3-max",
                "model.duration": "6",
                "model.resolution": "768p",
                "model.aspect_ratio": "16:9",
            },
            title="Animate",
            is_paid=True,
        ),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/product-teaser"}, title="Save the Teaser"),
    ),
    links=(
        ("brief.STRING", "frame.prompt"),
        ("brief.STRING", "situation.values.a"),
        ("frame.images", "moves.model.images.image_1"),
        ("moves.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("best.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("moves.text", "move.json_string"),
        ("read.answer", "move.key"),
        ("move.STRING", "chosen.source"),
        ("move.STRING", "animate.prompt"),
        ("frame.images", "animate.model.first_frame"),
        ("animate.video", "save.video"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief", "best"),)),),
        (Group(SHARED_TEXTS["frame"], (("frame", "moves"),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["choose"], (("situation", "decide"), ("read", "move", "chosen")), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["video"], (("animate", "save"),), STAGE_COLOUR),),
    ),
)

COLLECT_VIDEO = Workflow(
    slug="video-02-collect-a-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}VideoDownload", {"job": ""}, title="Unfinished Job"),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/collected"}, title="Save the Video"),
    ),
    links=(("download.video", "save.video"),),
    stacks=((Group(SHARED_TEXTS["video"], (("download",), ("save",)), STAGE_COLOUR),),),
)

VIDEO_WORKFLOWS = (ANIMATE_PRODUCT, COLLECT_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
