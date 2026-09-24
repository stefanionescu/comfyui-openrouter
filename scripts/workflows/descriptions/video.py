"""The video workflows: make a video, animate an image, draw then animate, and collect a recorded job."""

from __future__ import annotations

from scripts.config import IMAGE, SAVE_VIDEO
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow

GENERATE = f"{NODE_PREFIX}VideoGenerate"

MAKE_A_VIDEO = Workflow(
    slug="video-01-make-a-video",
    nodes=(
        Node("video", GENERATE, {"prompt": "A slow push-in on a lighthouse at dusk, waves below"}, is_paid=True),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/video-01-make-a-video"}),
    ),
    links=(("video.video", "save.video"),),
    stacks=((Group(SHARED_TEXTS["video"], (("video",), ("save",)), STAGE_COLOUR),),),
)

ANIMATE_AN_IMAGE = Workflow(
    slug="video-02-animate-an-image",
    nodes=(
        Node("frame", IMAGE, {"image": ""}),
        Node("video", GENERATE, {"prompt": "The scene comes to life with gentle wind."}, is_paid=True),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/video-02-animate-an-image"}),
    ),
    links=(("frame.IMAGE", "video.model.first_frame"), ("video.video", "save.video")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("frame",),)),),
        (Group(SHARED_TEXTS["video"], (("video",), ("save",)), STAGE_COLOUR),),
    ),
)

DRAW_THEN_ANIMATE = Workflow(
    slug="video-03-draw-then-animate",
    nodes=(
        Node(
            "image",
            f"{NODE_PREFIX}ImageGenerate",
            {"prompt": "A lighthouse on a cliff at dusk", "model.aspect_ratio": "16:9"},
            is_paid=True,
        ),
        Node("video", GENERATE, {"prompt": "Waves crash below as the light begins to turn."}, is_paid=True),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/video-03-draw-then-animate"}),
    ),
    links=(("image.images", "video.model.first_frame"), ("video.video", "save.video")),
    stacks=(
        (Group(SHARED_TEXTS["image"], (("image",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["video"], (("video",), ("save",)), STAGE_COLOUR),),
    ),
)

DOWNLOAD_A_VIDEO = Workflow(
    slug="video-04-download-a-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}VideoDownload", {"job": ""}),
        Node("save", SAVE_VIDEO, {"filename_prefix": "video/openrouter/video-04-download-a-video"}),
    ),
    links=(("download.video", "save.video"),),
    stacks=((Group(SHARED_TEXTS["video"], (("download",), ("save",)), STAGE_COLOUR),),),
)

VIDEO_WORKFLOWS = (MAKE_A_VIDEO, ANIMATE_AN_IMAGE, DRAW_THEN_ANIMATE, DOWNLOAD_A_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
