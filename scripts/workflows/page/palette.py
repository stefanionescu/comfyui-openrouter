"""Describe every node a workflow may place, and a subgraph as one node."""

from __future__ import annotations

from scripts.config import NOTE
from dataclasses import dataclass
from typing import cast, TYPE_CHECKING
from scripts.workflows.page.sizes import read_option_inputs
from scripts.workflows.page.config import MATCH_TYPE, AUTOGROW_TYPE
from scripts.workflows.page.widgets import Item, Schema, read_widget_default

if TYPE_CHECKING:
    from collections.abc import Mapping
    from scripts.workflows.page.graph import Node, Subgraph

# The page defines these nodes itself, so the schema export cannot describe them.
BUILT_IN: dict[str, Schema] = {
    NOTE: {"inputs": [{"name": "text", "type": "STRING", "widget": True, "default": ""}], "outputs": []},
}


@dataclass(frozen=True, slots=True)
class Palette:
    """The node descriptions a workflow may place, and its subgraphs with their IDs."""

    schemas: Mapping[str, Schema]
    subgraphs: Mapping[str, Subgraph]
    ids: Mapping[str, str]

    def schema(self, node: Node) -> Schema:
        """Describe one node or placed subgraph."""
        if node.kind in self.subgraphs:
            return build_subgraph_schema(self.subgraphs[node.kind], self)
        if node.kind in self.schemas:
            return self.schemas[node.kind]
        if node.kind in BUILT_IN:
            return BUILT_IN[node.kind]
        message = f"{node.kind} is not a node the workflows can place."
        raise KeyError(message)


def find_socket(schema: Schema, side: str, name: str, owner: str) -> tuple[int, Item]:
    """Find an input or output by name, with its position."""
    for index, item in enumerate(cast("list[Item]", schema[side])):
        if item["name"] == name:
            return index, item
    message = f"{owner} has no {side[:-1]} named {name}."
    raise KeyError(message)


def find_node(subgraph: Subgraph, key: str) -> Node:
    """Find one node of a subgraph by its key."""
    node = next((node for node in subgraph.nodes if node.key == key), None)
    if node is None:
        message = f"{subgraph.name} has no node keyed {key}."
        raise KeyError(message)
    return node


def read_slot_type(settings: Mapping[str, object]) -> object:
    """Read the type of every slot in a growing row."""
    template = cast("dict[str, dict[str, dict[str, list[object]]]]", settings["template"])
    socket = template["input"]
    return next(iter((socket.get("required") or socket.get("optional") or {}).values()))[0]


def find_input(node: Node, schema: Schema, socket: str) -> Item:
    """Find an input by its full name: the node's own, a slot of a growing row, or a dropdown option's socket."""
    parent, _, rest = socket.partition(".")
    _, item = find_socket(schema, "inputs", parent, node.kind)
    if not rest:
        return item
    if item["type"] == AUTOGROW_TYPE:
        return {"name": socket, "type": read_slot_type(item), "optional": True}
    child = rest.split(".", 1)[0]
    for group in read_option_inputs(item, node.values.get(parent)).values():
        if child in group:
            kind, settings = group[child]
            slot_type = read_slot_type(cast("dict[str, object]", settings)) if kind == AUTOGROW_TYPE else kind
            return {"name": socket, "type": slot_type, "optional": True}
    message = f"{node.kind} has no input named {socket}."
    raise KeyError(message)


def build_subgraph_schema(subgraph: Subgraph, palette: Palette) -> Schema:
    """Describe a subgraph as one node; an input linked to a widget inside shows as that widget."""
    inputs: list[Item] = []
    for name, target in subgraph.inputs:
        if any(item["name"] == name for item in inputs):
            continue
        key, socket = target.split(".", 1)
        node = find_node(subgraph, key)
        item = find_input(node, palette.schema(node), socket)
        default = node.values.get(socket, read_widget_default(item))
        inputs.append({**item, "name": name, "default": default, "optional": False})
    outputs: list[Item] = []
    for name, source in subgraph.outputs:
        key, socket = source.split(".", 1)
        node = find_node(subgraph, key)
        _, item = find_socket(palette.schema(node), "outputs", socket, node.kind)
        outputs.append({**item, "name": name, "type": read_output_type(subgraph, palette, key, item)})
    return {"inputs": inputs, "outputs": outputs}


def read_output_type(subgraph: Subgraph, palette: Palette, key: str, item: Item) -> object:
    """Read an output's type; a switch passes on the type of a node linked into it inside the subgraph."""
    if item["type"] != MATCH_TYPE:
        return item["type"]
    for start, end in subgraph.links:
        source_key, output = start.split(".", 1)
        if end.startswith(f"{key}.") and not end.endswith(".switch"):
            source = find_node(subgraph, source_key)
            _, source_item = find_socket(palette.schema(source), "outputs", output, source.kind)
            return source_item["type"]
    return item["type"]


__all__ = ["Palette", "find_node", "read_slot_type"]
