"""Turn workflow descriptions into the JSON ComfyUI saves."""

from __future__ import annotations

import uuid
from scripts.config import NOTE
from dataclasses import dataclass
from typing import cast, TYPE_CHECKING
from scripts.workflows.page.graph import Node, Subgraph, NAMESPACE
from scripts.workflows.page.layout import GUTTER, measure, place_stacks, place_columns
from scripts.workflows.page.widgets import Item, Schema, read_widget_default, serialize_widget_values
from scripts.workflows.page.config import (
    PORT_WIDTH,
    BYPASS_MODE,
    INNER_ORIGIN,
    PAID_COLOURS,
    SUBGRAPH_ID_STEP,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

Json = dict[str, object]
# A dropdown whose options add controls, a row of sockets that grows as they are linked, and the widget types.
DROPDOWN_TYPE = "COMFY_DYNAMICCOMBO_V3"
AUTOGROW_TYPE = "COMFY_AUTOGROW_V3"
# The any-type sockets of a switch, which take the type of the values linked into them.
MATCH_TYPE = "COMFY_MATCHTYPE_V3"
WIDGET_TYPES = frozenset({"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO", DROPDOWN_TYPE})
# The page defines these nodes itself, so the schema export cannot describe them.
BUILT_IN: dict[str, Schema] = {
    NOTE: {"inputs": [{"name": "text", "type": "STRING", "widget": True, "default": ""}], "outputs": []},
}


@dataclass(frozen=True, slots=True)
class Palette:
    """The node descriptions and subgraphs a workflow may place."""

    schemas: Mapping[str, Schema]
    subgraphs: Mapping[str, Subgraph]

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


def build_subgraph_schema(subgraph: Subgraph, palette: Palette) -> Schema:
    """Describe a subgraph as one node."""
    inputs: list[Item] = []
    for name, target in subgraph.inputs:
        if any(item["name"] == name for item in inputs):
            continue
        key, socket = target.split(".")
        node = find_node(subgraph, key)
        _, item = find_socket(palette.schema(node), "inputs", socket, node.kind)
        default = node.values.get(socket, read_widget_default(item))
        inputs.append({**item, "name": name, "default": default, "optional": False})
    outputs: list[Item] = []
    for name, source in subgraph.outputs:
        key, socket = source.split(".")
        node = find_node(subgraph, key)
        _, item = find_socket(palette.schema(node), "outputs", socket, node.kind)
        outputs.append({**item, "name": name})
    return {"inputs": inputs, "outputs": outputs}


def serialize_option_sockets(item: Item, chosen: object, linked: frozenset[str]) -> list[Json]:
    """Serialize the sockets of a dropdown's chosen option: each growing row shows its linked slots and one more."""
    options = cast("list[dict[str, object]]", item.get("options") or [])
    option = next((option for option in options if option["key"] == chosen), options[0] if options else None)
    if option is None:
        return []
    sockets: list[Json] = []
    children = cast("dict[str, dict[str, list[object]]]", option["inputs"])
    for group in ("required", "optional"):
        for child, (kind, settings) in children.get(group, {}).items():
            name = f"{item['name']}.{child}"
            if kind in WIDGET_TYPES:
                continue
            if kind == AUTOGROW_TYPE:
                sockets += serialize_autogrow(name, cast("dict[str, object]", settings), linked)
            else:
                sockets.append({"name": name, "type": kind, "link": None, "shape": 7})
    return sockets


def serialize_autogrow(name: str, settings: Mapping[str, object], linked: frozenset[str]) -> list[Json]:
    """Serialize a growing row of sockets: every slot up to the last linked one, and one more."""
    template = cast("dict[str, object]", settings["template"])
    slots = [f"{name}.{slot}" for slot in cast("list[str]", template["names"])]
    shown = max((index + 1 for index, slot in enumerate(slots) if slot in linked), default=0) + 1
    socket = cast("dict[str, dict[str, list[object]]]", template["input"])
    slot_type = next(iter((socket.get("required") or socket.get("optional") or {}).values()))[0]
    return [
        {"label": slot.rsplit(".", 1)[1], "name": slot, "type": slot_type, "link": None, "shape": 7}
        for slot in slots[:shown]
    ]


def serialize_inputs(node: Node, schema: Schema, linked: frozenset[str], *, is_subgraph: bool) -> list[Json]:
    """Serialize a node's inputs; a dropdown's chosen option adds the sockets it shows after it."""
    inputs: list[Json] = []
    for item in cast("list[Item]", schema["inputs"]):
        if item.get("widget") and is_subgraph:
            continue
        if item["type"] == AUTOGROW_TYPE:
            inputs += serialize_autogrow(str(item["name"]), item, linked)
            continue
        entry: Json = {"name": item["name"], "type": item["type"], "link": None}
        if item.get("widget"):
            entry["widget"] = {"name": item["name"]}
        elif item.get("optional"):
            entry["shape"] = 7
        inputs.append(entry)
        if item["type"] == DROPDOWN_TYPE:
            options = cast("list[dict[str, object]]", item.get("options") or [])
            chosen = node.values.get(str(item["name"]), options[0]["key"] if options else "")
            inputs += serialize_option_sockets(item, chosen, linked)
    return inputs


def serialize_node(
    node: Node, number: int, palette: Palette, box: tuple[int, int, int, int], linked: frozenset[str]
) -> Json:
    """Serialize one node with nothing linked; a dropdown's chosen option adds the sockets it shows."""
    schema = palette.schema(node)
    is_subgraph = node.kind in palette.subgraphs
    inputs = serialize_inputs(node, schema, linked, is_subgraph=is_subgraph)
    outputs: list[Json] = [
        {"name": item["name"], "type": item["type"], **({"shape": 6} if item.get("is_list") else {}), "links": []}
        for item in cast("list[Item]", schema["outputs"])
    ]
    kind = palette.subgraphs[node.kind].id if is_subgraph else node.kind
    entry: Json = {
        "id": number,
        "type": kind,
        "pos": [box[0], box[1]],
        "size": [box[2], box[3]],
        "flags": {},
        "order": number - 1,
        "mode": BYPASS_MODE if node.is_bypassed else 0,
        "inputs": inputs,
        "outputs": outputs,
        "properties": {} if is_subgraph else {"Node name for S&R": kind},
        "widgets_values": serialize_widget_values(schema, node.values, node.kind),
    }
    if node.title or is_subgraph:
        entry["title"] = node.title or node.kind
    if node.is_paid:
        entry.update(PAID_COLOURS)
    return entry


def find_slot_index(entry: Json, side: str, name: str) -> int:
    """Find the position of a serialized input or output."""
    sockets = cast("list[Json]", entry[side])
    index = next((index for index, socket in enumerate(sockets) if socket["name"] == name), None)
    if index is None:
        message = f"{entry['type']} has no {side[:-1]} named {name}."
        raise KeyError(message)
    return index


def serialize_graph(
    nodes: tuple[Node, ...],
    links: tuple[tuple[str, str], ...],
    palette: Palette,
    boxes: Mapping[str, tuple[int, int, int, int]],
    first_id: int = 1,
) -> tuple[dict[str, Json], list[Json]]:
    """Serialize nodes and the links between them."""
    numbered = enumerate(nodes, first_id)
    targets = [end.split(".", 1) for _start, end in links]
    entries = {
        node.key: serialize_node(
            node,
            number,
            palette,
            boxes[node.key],
            frozenset(socket for key, socket in targets if key == node.key),
        )
        for number, node in numbered
    }
    if len(entries) != len(nodes):
        message = "Give every node its own key."
        raise ValueError(message)
    records: list[Json] = []
    matched = match_types(entries, links)
    for number, (start, end) in enumerate(links, 1):
        # The node key comes first; the rest is the socket's full name, which can hold a dropdown's child.
        source_key, output = start.split(".", 1)
        target_key, input_name = end.split(".", 1)
        origin, target = entries[source_key], entries[target_key]
        origin_slot = find_slot_index(origin, "outputs", output)
        target_slot = find_slot_index(target, "inputs", input_name)
        cast("list[int]", cast("list[Json]", origin["outputs"])[origin_slot]["links"]).append(number)
        cast("list[Json]", target["inputs"])[target_slot]["link"] = number
        kind = cast("list[Json]", origin["outputs"])[origin_slot]["type"]
        if kind == MATCH_TYPE:
            kind = matched[source_key]
            cast("list[Json]", origin["outputs"])[origin_slot]["type"] = kind
        if cast("list[Json]", target["inputs"])[target_slot]["type"] == MATCH_TYPE:
            cast("list[Json]", target["inputs"])[target_slot]["type"] = kind
        records.append(
            {
                "id": number,
                "origin_id": origin["id"],
                "origin_slot": origin_slot,
                "target_id": target["id"],
                "target_slot": target_slot,
                "type": kind,
            }
        )
    return entries, records


def match_types(entries: Mapping[str, Json], links: tuple[tuple[str, str], ...]) -> dict[str, object]:
    """Find the type each switch passes on: the type of the values linked into its matched inputs.

    ComfyUI saves a switch's any-type sockets with the type of the values that feed it once they are linked.
    """
    matched: dict[str, object] = {}
    for start, end in links:
        source_key, output = start.split(".", 1)
        target_key, input_name = end.split(".", 1)
        target = entries[target_key]
        socket = cast("list[Json]", target["inputs"])[find_slot_index(target, "inputs", input_name)]
        origin = entries[source_key]
        kind = cast("list[Json]", origin["outputs"])[find_slot_index(origin, "outputs", output)]["type"]
        if socket["type"] == MATCH_TYPE and kind != MATCH_TYPE:
            matched[target_key] = kind
    return matched


def link_subgraph_ports(subgraph: Subgraph, entries: dict[str, Json], records: list[Json], side: str) -> list[Json]:
    """Link the exposed inputs or outputs to the inner nodes."""
    ports: list[Json] = []
    port_node, inner_side = (-10, "inputs") if side == "inputs" else (-20, "outputs")
    for name, socket in getattr(subgraph, side):
        port = next((port for port in ports if port["name"] == name), None)
        if port is None:
            port_id = str(uuid.uuid5(NAMESPACE, f"{subgraph.id}.{side}.{name}"))
            port = cast("Json", {"id": port_id, "name": name, "type": "", "linkIds": [], "pos": [0, 0]})
            ports.append(port)
        index = ports.index(port)
        key, socket_name = socket.split(".")
        entry = entries[key]
        position = find_slot_index(entry, inner_side, socket_name)
        number = len(records) + 1
        inner = cast("list[Json]", entry[inner_side])[position]
        if side == "inputs":
            inner["link"] = number
            record = {"origin_id": port_node, "origin_slot": index, "target_id": entry["id"], "target_slot": position}
        else:
            cast("list[int]", inner["links"]).append(number)
            record = {"origin_id": entry["id"], "origin_slot": position, "target_id": port_node, "target_slot": index}
        records.append({"id": number, **record, "type": inner["type"]})
        port["type"] = inner["type"]
        cast("list[int]", port["linkIds"]).append(number)
    return ports


def serialize_subgraph(subgraph: Subgraph, palette: Palette, position: int) -> Json:
    """Serialize one subgraph definition with its input and output ports."""
    sizes = {node.key: measure(node.kind, palette.schema(node)) for node in subgraph.nodes}
    if subgraph.stacks:
        placed, groups = place_stacks(subgraph.stacks, sizes, INNER_ORIGIN)
    else:
        placed, groups = place_columns(subgraph.columns, sizes, INNER_ORIGIN), []
    boxes = {key: (box.x, box.y, box.width, box.height) for key, box in placed.items()}
    entries, records = serialize_graph(subgraph.nodes, subgraph.links, palette, boxes, position * SUBGRAPH_ID_STEP + 1)
    inputs = link_subgraph_ports(subgraph, entries, records, "inputs")
    outputs = link_subgraph_ports(subgraph, entries, records, "outputs")
    right = max(box.right for box in placed.values()) + GUTTER
    for index, port in enumerate(inputs):
        port["pos"] = [INNER_ORIGIN[0] - GUTTER, INNER_ORIGIN[1] + 20 * index]
    for index, port in enumerate(outputs):
        port["pos"] = [right, INNER_ORIGIN[1] + 20 * index]
    return {
        "id": subgraph.id,
        "version": 1,
        "state": {
            "lastGroupId": 0,
            "lastNodeId": position * SUBGRAPH_ID_STEP + len(entries),
            "lastLinkId": len(records),
            "lastRerouteId": 0,
        },
        "revision": 0,
        "config": {},
        "name": subgraph.name,
        "inputNode": {
            "id": -10,
            "bounding": [INNER_ORIGIN[0] - GUTTER - PORT_WIDTH, INNER_ORIGIN[1], PORT_WIDTH, 20 * max(1, len(inputs))],
        },
        "outputNode": {"id": -20, "bounding": [right, INNER_ORIGIN[1], PORT_WIDTH, 20 * max(1, len(outputs))]},
        "inputs": inputs,
        "outputs": outputs,
        "widgets": [],
        "nodes": list(entries.values()),
        "groups": groups,
        "links": records,
        "extra": {"description": subgraph.description} if subgraph.description else {},
    }


__all__ = ["Json", "Palette", "Schema", "serialize_graph", "serialize_subgraph"]
