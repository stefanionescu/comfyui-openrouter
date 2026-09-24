"""Place nodes in groups and groups in stacks, and frame the groups."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass
from types import MappingProxyType
from scripts.workflows.page.config import GUTTER, NODE_GAP, GROUP_TOP, STACK_GAP, CANVAS_ORIGIN

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
    group: Group, sizes: Mapping[str, tuple[int, int]], origin: tuple[int, int], note: str | None
) -> tuple[dict[str, Box], Box]:
    """Place a group's note across its top and its columns below, and return the frame."""
    boxes: dict[str, Box] = {}
    top = origin[1] + GROUP_TOP
    if note is not None:
        boxes[note] = Box(origin[0] + GUTTER, top, *sizes[note])
        top = boxes[note].bottom + STACK_GAP
    boxes |= place_columns(group.columns, sizes, (origin[0] + GUTTER, top))
    right = max(box.right for box in boxes.values()) + GUTTER
    bottom = max(box.bottom for box in boxes.values()) + GUTTER
    return boxes, Box(origin[0], origin[1], right - origin[0], bottom - origin[1])


def place_stacks(
    stacks: Sequence[Sequence[Group]],
    sizes: Mapping[str, tuple[int, int]],
    origin: tuple[int, int] = CANVAS_ORIGIN,
    notes: Mapping[str, str] = MappingProxyType({}),
) -> tuple[dict[str, Box], list[dict[str, object]]]:
    """Place the stacks side by side, each group with its note, and serialize each group's frame.

    The notes map a group's title to the key of the note placed across its top.
    """
    boxes: dict[str, Box] = {}
    frames: list[dict[str, object]] = []
    x = origin[0]
    for stack in stacks:
        y = origin[1]
        width = 0
        for group in stack:
            placed, frame = place_group(group, sizes, (x, y), notes.get(group.title))
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


__all__ = ["place_columns", "place_stacks"]
