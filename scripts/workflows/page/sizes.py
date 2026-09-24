"""Size nodes the way ComfyUI's page computes them, so a loaded workflow keeps its layout."""

from __future__ import annotations

import re
import math
from typing import cast, TYPE_CHECKING
from scripts.workflows.page.config import (
    DOM_SIZES,
    NODE_WIDTH,
    WIDGET_GAP,
    SLOT_HEIGHT,
    NODE_PADDING,
    NOTE_PADDING,
    WIDGET_TYPES,
    AUTOGROW_TYPE,
    DROPDOWN_TYPE,
    WIDGET_HEIGHT,
    NOTE_MIN_HEIGHT,
    WIDGETS_PADDING,
    MULTILINE_HEIGHT,
    NOTE_LINE_HEIGHT,
    NOTE_LIST_INDENT,
    NOTE_SIDE_PADDING,
    MULTISELECT_HEIGHT,
    NOTE_PARAGRAPH_GAP,
    NOTE_CHARACTER_WIDTH,
    NOTE_CODE_CHARACTER_WIDTH,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


def read_slots(name: str, settings: Mapping[str, object]) -> list[str]:
    """Name every slot of a growing row: listed by name, or numbered from 0 after a prefix."""
    template = cast("dict[str, object]", settings["template"])
    if "names" in template:
        return [f"{name}.{slot}" for slot in cast("list[str]", template["names"])]
    return [f"{name}.{template['prefix']}{number}" for number in range(cast("int", template["max"]))]


def count_slots(name: str, settings: Mapping[str, object], linked: frozenset[str]) -> int:
    """Count the sockets a growing row shows: every slot up to the last linked one and one more, or its minimum."""
    slots = read_slots(name, settings)
    shown = max((index + 1 for index, slot in enumerate(slots) if slot in linked), default=0) + 1
    minimum = cast("int", cast("dict[str, object]", settings["template"]).get("min", 0))
    return min(len(slots), max(shown, minimum))


def read_option_inputs(item: Mapping[str, object], chosen: object) -> dict[str, dict[str, list[object]]]:
    """Read the inputs a dropdown's chosen option adds, or its first option's when the value names none."""
    options = cast("list[dict[str, object]]", item.get("options") or [])
    option = next((option for option in options if option["key"] == chosen), options[0] if options else None)
    if option is None:
        return {}
    return cast("dict[str, dict[str, list[object]]]", option["inputs"])


def measure(
    kind: str, schema: Mapping[str, object], values: Mapping[str, object], linked: frozenset[str]
) -> tuple[int, int]:
    """Size a node as the page does: a row per socket, then each widget and its gap; panels are measured.

    A dropdown adds the sockets and widgets of its chosen option, and a growing row shows its linked slots
    and one more.
    """
    if kind in DOM_SIZES:
        return DOM_SIZES[kind]
    sockets, widgets = _count_inputs(cast("list[dict[str, object]]", schema["inputs"]), values, linked)
    rows = max(sockets, len(cast("list[object]", schema["outputs"])), 1)
    height = rows * SLOT_HEIGHT + NODE_PADDING
    if widgets:
        height += sum(widget + WIDGET_GAP for widget in widgets) + WIDGETS_PADDING
    return NODE_WIDTH, height


def measure_note(text: str, width: int) -> int:
    """Height of a note that fits its text: each line wraps at the note's width, and a blank line is a gap.

    A numbered step wraps sooner, since the list is indented.
    """
    height = NOTE_PADDING
    for line in text.splitlines():
        if not line:
            height += NOTE_PARAGRAPH_GAP
            continue
        # Bold and code marks take no space once the page renders them, and code is set in a wider font.
        code = sum(len(span) for span in re.findall(r"`([^`]*)`", line))
        shown = len(re.sub(r"\*\*|`", "", line))
        drawn = (shown - code) * NOTE_CHARACTER_WIDTH + code * NOTE_CODE_CHARACTER_WIDTH
        indent = NOTE_LIST_INDENT if re.match(r"\d+\. ", line) else 0
        height += NOTE_LINE_HEIGHT * math.ceil(drawn / (width - NOTE_SIDE_PADDING - indent))
    return max(height, NOTE_MIN_HEIGHT)


def _count_inputs(
    inputs: list[dict[str, object]], values: Mapping[str, object], linked: frozenset[str]
) -> tuple[int, list[int]]:
    """Count a node's socket rows and list its widget heights, a seed's control widget included."""
    sockets = 0
    widgets: list[int] = []
    for item in inputs:
        name = str(item["name"])
        if not item.get("widget"):
            # The page keeps a row free below a node's own growing row, one more than it computes.
            sockets += count_slots(name, item, linked) + 1 if item["type"] == AUTOGROW_TYPE else 1
            continue
        widgets.append(_measure_widget(item))
        if item.get("control_after_generate"):
            widgets.append(WIDGET_HEIGHT)
        if item["type"] == DROPDOWN_TYPE:
            option_sockets, option_widgets = _count_option(item, values.get(name), linked)
            sockets += option_sockets
            widgets += option_widgets
    return sockets, widgets


def _count_option(item: Mapping[str, object], chosen: object, linked: frozenset[str]) -> tuple[int, list[int]]:
    """Count the socket rows and list the widget heights of a dropdown's chosen option."""
    sockets = 0
    widgets: list[int] = []
    children = read_option_inputs(item, chosen)
    for group in ("required", "optional"):
        for child, (kind, settings) in children.get(group, {}).items():
            fields = cast("dict[str, object]", settings)
            if kind in WIDGET_TYPES:
                widgets.append(_measure_widget(fields))
            elif kind == AUTOGROW_TYPE:
                sockets += count_slots(f"{item['name']}.{child}", fields, linked)
            else:
                sockets += 1
    return sockets, widgets


def _measure_widget(item: Mapping[str, object]) -> int:
    """Height of one widget before its gap: a multi-line text and a multi-select list are taller."""
    if item.get("multiline"):
        return MULTILINE_HEIGHT
    if item.get("multiselect"):
        return MULTISELECT_HEIGHT
    return WIDGET_HEIGHT


__all__ = ["count_slots", "measure", "measure_note", "read_option_inputs", "read_slots"]
