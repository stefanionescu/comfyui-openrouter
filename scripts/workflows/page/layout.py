"""Place nodes in groups and groups in stacks, and frame the groups."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast, TYPE_CHECKING
from scripts.workflows.page.config import (
    GUTTER,
    NODE_GAP,
    DOM_SIZES,
    GROUP_TOP,
    STACK_GAP,
    NODE_WIDTH,
    SLOT_HEIGHT,
    TITLE_HEIGHT,
    CANVAS_ORIGIN,
    WIDGET_HEIGHT,
    MULTILINE_HEIGHT,
    MULTISELECT_HEIGHT,
    CHILD_WIDGET_HEIGHT,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from scripts.workflows.page.graph import Group


@dataclass(frozen=True, slots=True)
class Box:
    """A node's place on the page."""

    x: int
    y: int
    width: int
    height: int

    @property
    def bottom(self) -> int:
        """The row just below the box."""
        return self.y + self.height

    @property
    def right(self) -> int:
        """The column just right of the box."""
        return self.x + self.width


def measure(kind: str, schema: Mapping[str, object]) -> tuple[int, int]:
    """Size a node from its schema: a row per socket, then its widgets; nodes with their own panel are measured."""
    if kind in DOM_SIZES:
        return DOM_SIZES[kind]
    inputs = cast("list[dict[str, object]]", schema["inputs"])
    outputs = cast("list[object]", schema["outputs"])
    widgets = [item for item in inputs if item.get("widget")]
    rows = max(len(inputs) - len(widgets), len(outputs))
    height = TITLE_HEIGHT + rows * SLOT_HEIGHT + sum(_measure_widget(item) for item in widgets)
    return NODE_WIDTH, height


def _measure_widget(item: Mapping[str, object]) -> int:
    """Height of one widget row, with the child rows of a dynamic dropdown's first option."""
    if item.get("multiline"):
        return MULTILINE_HEIGHT
    if item.get("multiselect"):
        return MULTISELECT_HEIGHT
    options = cast("list[dict[str, object]]", item.get("options") or [])
    if item["type"] == "COMFY_DYNAMICCOMBO_V3" and options:
        children = cast("dict[str, dict[str, object]]", options[0]["inputs"])
        return WIDGET_HEIGHT + CHILD_WIDGET_HEIGHT * sum(len(group) for group in children.values())
    return WIDGET_HEIGHT


def place_columns(
    columns: Sequence[Sequence[str]], sizes: Mapping[str, tuple[int, int]], origin: tuple[int, int]
) -> dict[str, Box]:
    """Place columns of nodes side by side."""
    boxes: dict[str, Box] = {}
    x = origin[0]
    for column in columns:
        y = origin[1]
        width = max(sizes[key][0] for key in column)
        for key in column:
            boxes[key] = Box(x, y, *sizes[key])
            y = boxes[key].bottom + STACK_GAP
        x += width + NODE_GAP
    return boxes


def place_group(
    group: Group, sizes: Mapping[str, tuple[int, int]], origin: tuple[int, int]
) -> tuple[dict[str, Box], Box]:
    """Place a group's columns inside its frame and return the frame."""
    boxes = place_columns(group.columns, sizes, (origin[0] + GUTTER, origin[1] + GROUP_TOP))
    right = max(box.right for box in boxes.values()) + GUTTER
    bottom = max(box.bottom for box in boxes.values()) + GUTTER
    return boxes, Box(origin[0], origin[1], right - origin[0], bottom - origin[1])


def place_stacks(
    stacks: Sequence[Sequence[Group]], sizes: Mapping[str, tuple[int, int]], origin: tuple[int, int] = CANVAS_ORIGIN
) -> tuple[dict[str, Box], list[dict[str, object]]]:
    """Place the stacks side by side below the note, and serialize each group's frame."""
    boxes: dict[str, Box] = {}
    frames: list[dict[str, object]] = []
    top = origin[1]
    if "note" in sizes:
        boxes["note"] = Box(origin[0], top, *sizes["note"])
        top = boxes["note"].bottom + GUTTER
    x = origin[0]
    for stack in stacks:
        y = top
        width = 0
        for group in stack:
            placed, frame = place_group(group, sizes, (x, y))
            boxes |= placed
            frames.append(
                {
                    "id": len(frames) + 1,
                    "title": group.title,
                    "bounding": [frame.x, frame.y, frame.width, frame.height],
                    "color": group.colour,
                    "font_size": 24,
                    "flags": {},
                }
            )
            width = max(width, frame.width)
            y = frame.bottom + GUTTER
        x += width + GUTTER
    return boxes, frames


__all__ = ["GUTTER", "measure", "place_columns", "place_stacks"]
