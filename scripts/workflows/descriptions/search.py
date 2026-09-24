"""The search workflows: compare texts, rank documents, and pick the best of several generated images."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.config import PREVIEW, SAVE_IMAGE
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow

RANK = f"{NODE_PREFIX}SearchRank"
IMAGE_PROMPT = "A red panda astronaut floating in space, studio lighting"

COMPARE_TEXTS = Workflow(
    slug="search-01-compare-texts",
    nodes=(
        Node(
            "embed",
            f"{NODE_PREFIX}SearchEmbed",
            {
                "texts": (
                    "How do I reset my password?\n"
                    "Steps to change a forgotten login password\n"
                    "Our office is closed on public holidays\n"
                    "Recovering access to your account"
                )
            },
            is_paid=True,
        ),
        Node("similarities", PREVIEW, title="Similarities"),
    ),
    links=(("embed.similarities", "similarities.source"),),
    stacks=((Group(SHARED_TEXTS["search"], (("embed",), ("similarities",)), STAGE_COLOUR),),),
)

RANK_DOCUMENTS = Workflow(
    slug="search-02-rank-documents",
    nodes=(
        Node(
            "rank",
            RANK,
            {
                "query": "Which fruit is highest in vitamin C?",
                "documents": (
                    "Bananas are rich in potassium.\n"
                    "Kiwifruit holds more vitamin C than oranges.\n"
                    "Apples keep well for months when stored cold.\n"
                    "Guava has one of the highest vitamin C contents of any fruit.\n"
                    "Blueberries are small and sweet."
                ),
            },
            is_paid=True,
        ),
        Node("ranked", PREVIEW, title="Ranked"),
        Node("scores", PREVIEW, title="Scores"),
    ),
    links=(("rank.texts", "ranked.source"), ("rank.scores", "scores.source")),
    stacks=((Group(SHARED_TEXTS["search"], (("rank",), ("ranked", "scores")), STAGE_COLOUR),),),
)

PICK_THE_BEST_IMAGE = Workflow(
    slug="search-03-pick-the-best-image",
    nodes=(
        Node(
            "image",
            f"{NODE_PREFIX}ImageGenerate",
            {"model": "recraft/recraft-v4.1", "prompt": IMAGE_PROMPT, "model.count": 4},
            is_paid=True,
        ),
        Node(
            "rank",
            RANK,
            {"model": "nvidia/llama-nemotron-rerank-vl-1b-v2:free", "query": IMAGE_PROMPT, "top_n": 1},
            is_paid=True,
        ),
        Node("save", SAVE_IMAGE, {"filename_prefix": "image/openrouter/search-03-pick-the-best-image"}),
    ),
    links=(("image.images", "rank.model.images.image_1"), ("rank.images", "save.images")),
    stacks=(
        (Group(SHARED_TEXTS["image"], (("image",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["search"], (("rank",), ("save",)), STAGE_COLOUR),),
    ),
)

SEARCH_WORKFLOWS = (COMPARE_TEXTS, RANK_DOCUMENTS, PICK_THE_BEST_IMAGE)

__all__ = ["SEARCH_WORKFLOWS"]
