"""The request options workflow: choose providers for a chat request."""

from __future__ import annotations

from scripts.config import PREVIEW
from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow

CHOOSE_PROVIDERS = Workflow(
    slug="options-01-choose-providers",
    nodes=(
        Node("options", f"{NODE_PREFIX}RequestOptions", {"sort": "price", "allow_fallbacks": "yes"}),
        Node(
            "ask",
            f"{NODE_PREFIX}ChatAsk",
            {"prompt": "Explain in three sentences how a rainbow forms."},
            is_paid=True,
        ),
        Node("answer", PREVIEW),
    ),
    links=(("options.options", "ask.options"), ("ask.text", "answer.source")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("options",),)),),
        (Group(SHARED_TEXTS["ask"], (("ask",), ("answer",)), STAGE_COLOUR),),
    ),
)

OPTIONS_WORKFLOWS = (CHOOSE_PROVIDERS,)

__all__ = ["OPTIONS_WORKFLOWS"]
