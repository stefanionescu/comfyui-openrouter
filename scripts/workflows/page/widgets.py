"""Check a node's widget values against its schema and serialize them in the order the page stores them."""

from __future__ import annotations
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from scripts.types import Item, Schema, WidgetValue

# A node's schema as the export describes it, and one of its inputs or outputs.


def _validate_widget_value(item: Item, value: object, owner: str) -> None:
    """Refuse a widget value its input does not accept."""
    kind = item["type"]
    options = cast("list[object]", item.get("options") or [])
    if kind == "COMBO" and item.get("multiselect"):
        is_valid = isinstance(value, list) and (not options or set(cast("list[object]", value)) <= set(options))
    elif kind == "COMBO":
        # An empty choice leaves the person to pick one, as for a folder or file listed from this machine.
        is_valid = not options or value in options or value == ""
    elif kind in {"INT", "FLOAT"}:
        low = cast("float", item.get("min", float("-inf")))
        high = cast("float", item.get("max", float("inf")))
        is_valid = type(value) in {int, float} and low <= cast("float", value) <= high
    elif kind == "BOOLEAN":
        is_valid = isinstance(value, bool)
    elif kind == "STRING":
        is_valid = isinstance(value, str)
    else:
        is_valid = True
    if not is_valid:
        message = f"{owner}.{item['name']} does not accept {value!r}."
        raise ValueError(message)


def _encode_dropdown_values(item: Item, values: Mapping[str, WidgetValue], owner: str) -> list[object]:
    """Serialize a dynamic dropdown with the values of its option."""
    name = str(item["name"])
    options = cast("list[dict[str, object]]", item["options"])
    chosen = values.get(name, options[0]["key"])
    option = next((option for option in options if option["key"] == chosen), None)
    if option is None:
        message = f"{owner}.{name} does not offer {chosen!r}."
        raise ValueError(message)
    result: list[object] = [chosen]
    children = cast("dict[str, dict[str, list[object]]]", option["inputs"])
    for group in ("required", "optional"):
        for child, (kind, settings) in children.get(group, {}).items():
            # Only plain widgets are saved here; a nested dropdown, such as Save Video's codec, is left to the page.
            if kind not in {"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"}:
                continue
            child_item = {"name": f"{name}.{child}", "type": kind, **cast("dict[str, object]", settings)}
            value = values.get(f"{name}.{child}", read_widget_default(child_item))
            _validate_widget_value(child_item, value, owner)
            result.append(value)
            if child_item.get("control_after_generate"):
                result.append("fixed")
    return result


def read_widget_default(item: Item) -> object:
    """Read a widget's starting value; a widget without a default starts empty, as ComfyUI draws it."""
    default = item.get("default")
    if default is not None:
        return default
    if item["type"] == "COMBO":
        options = cast("list[object]", item.get("options") or [])
        return [] if item.get("multiselect") else options[0] if options else ""
    return {"STRING": "", "BOOLEAN": False}.get(str(item["type"]), item.get("min", 0))


def encode_widget_values(schema: Schema, values: Mapping[str, WidgetValue], owner: str) -> list[object]:
    """Serialize a node's widget values in schema order."""
    # ComfyUI builds a node's widgets from its required inputs first, then its optional ones.
    widgets = sorted(
        (item for item in cast("list[Item]", schema["inputs"]) if item.get("widget")),
        key=lambda item: bool(item.get("optional")),
    )
    known = {str(item["name"]) for item in widgets}
    for name in values:
        if name.split(".")[0] not in known:
            message = f"{owner} has no widget named {name}."
            raise KeyError(message)
    result: list[object] = []
    for item in widgets:
        if item["type"] == "COMFY_DYNAMICCOMBO_V3":
            result.extend(_encode_dropdown_values(item, values, owner))
            continue
        value = values.get(str(item["name"]), read_widget_default(item))
        _validate_widget_value(item, value, owner)
        result.append(value)
        if item.get("control_after_generate"):
            # A paid node's seed ships fixed, so opening an example never sends a new request by itself.
            result.append("fixed")
        if item.get("image_upload"):
            # The page adds an upload button after an upload dropdown.
            result.append("image")
    return result


__all__ = ["encode_widget_values", "read_widget_default"]
