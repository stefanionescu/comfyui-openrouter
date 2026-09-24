"""The image workflows: generate, edit, combine, draw vectors, and draw with a chat model."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.config import IMAGE, SAVE_SVG, SAVE_IMAGE
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow

GENERATE = f"{NODE_PREFIX}ImageGenerate"

GENERATE_AN_IMAGE = Workflow(
    slug="image-01-generate-an-image",
    nodes=(
        Node(
            "image",
            GENERATE,
            {"prompt": "A red panda astronaut floating in space, studio lighting", "model.aspect_ratio": "16:9"},
            is_paid=True,
        ),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/image-01-generate-an-image"}),
    ),
    links=(("image.images", "save.images"),),
    stacks=((Group(SHARED_TEXTS["image"], (("image",), ("save",)), STAGE_COLOUR),),),
)

EDIT_AN_IMAGE = Workflow(
    slug="image-02-edit-an-image",
    nodes=(
        Node("photo", IMAGE, {"image": ""}),
        Node("image", GENERATE, {"prompt": "Turn this photo into a watercolor painting."}, is_paid=True),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/image-02-edit-an-image"}),
    ),
    links=(("photo.IMAGE", "image.model.references.reference_1"), ("image.images", "save.images")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo",),)),),
        (Group(SHARED_TEXTS["image"], (("image",), ("save",)), STAGE_COLOUR),),
    ),
)

COMBINE_TWO_IMAGES = Workflow(
    slug="image-03-combine-two-images",
    nodes=(
        Node("product", IMAGE, {"image": ""}, title="Product"),
        Node("scene", IMAGE, {"image": ""}, title="Scene"),
        Node(
            "image",
            GENERATE,
            {
                "prompt": (
                    "Place the product from the first image on the table in the second image. Keep the room unchanged."
                )
            },
            is_paid=True,
        ),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/image-03-combine-two-images"}),
    ),
    links=(
        ("product.IMAGE", "image.model.references.reference_1"),
        ("scene.IMAGE", "image.model.references.reference_2"),
        ("image.images", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("product", "scene"),)),),
        (Group(SHARED_TEXTS["image"], (("image",), ("save",)), STAGE_COLOUR),),
    ),
)

DRAW_A_VECTOR_LOGO = Workflow(
    slug="image-04-draw-a-vector-logo",
    nodes=(
        Node(
            "image",
            GENERATE,
            {"model": "recraft/recraft-v4.1-vector", "prompt": "A minimal fox logo, two colors"},
            is_paid=True,
        ),
        Node("save", SAVE_SVG, {"filename_prefix": "svg/openrouter/image-04-draw-a-vector-logo"}),
    ),
    links=(("image.svg", "save.svg"),),
    stacks=((Group(SHARED_TEXTS["image"], (("image",), ("save",)), STAGE_COLOUR),),),
)

DRAW_IN_CHAT = Workflow(
    slug="image-05-draw-with-a-chat-model",
    nodes=(
        Node(
            "ask",
            f"{NODE_PREFIX}ChatAsk",
            {
                "model": "google/gemini-3.1-flash-image",
                "prompt": "Paint a watercolor fox.",
            },
            is_paid=True,
        ),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/image-05-draw-with-a-chat-model"}),
    ),
    links=(("ask.images", "save.images"),),
    stacks=((Group(SHARED_TEXTS["ask"], (("ask",), ("save",)), STAGE_COLOUR),),),
)

IMAGE_WORKFLOWS = (
    GENERATE_AN_IMAGE,
    EDIT_AN_IMAGE,
    COMBINE_TWO_IMAGES,
    DRAW_A_VECTOR_LOGO,
    DRAW_IN_CHAT,
)

__all__ = ["IMAGE_WORKFLOWS"]
