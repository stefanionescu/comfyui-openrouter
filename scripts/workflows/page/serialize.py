"""Turn workflow descriptions into the JSON ComfyUI saves."""

from __future__ import annotations

import uuid
from typing import cast, TYPE_CHECKING
from scripts.workflows.page.graph import NAMESPACE
from scripts.workflows.page.widgets import encode_widget_values
from scripts.workflows.page.palette import Palette, read_slot_type
from scripts.workflows.page.sizes import measure, list_shown_slots
from scripts.workflows.page.layout import place_stacks, place_columns
from scripts.workflows.page.config import (
    ANY_TYPE,
    PORT_GAP,
    MATCH_TYPE,
    PORT_WIDTH,
    BYPASS_MODE,
    INNER_ORIGIN,
    PAID_COLOURS,
    AUTOGROW_TYPE,
    SUBGRAPH_ID_STEP,
)

if TYPE_CHECKING:
    from scripts.types import Item, Json, Schema
    from collections.abc import Mapping, Sequence
    from scripts.workflows.page.graph import Node, Subgraph


def _encode_inputs(schema: Schema, linked: frozenset[str]) -> list[Json]:
    """Serialize a node's inputs; a growing row shows its linked slots and one more."""
    inputs: list[Json] = []
    for item in cast("list[Item]", schema["inputs"]):
        if item["type"] == AUTOGROW_TYPE:
            slot_type = read_slot_type(item)
            inputs += [
                {"label": slot.rsplit(".", 1)[1], "name": slot, "type": slot_type, "link": None, "shape": 7}
                for slot in list_shown_slots(str(item["name"]), item, linked)
            ]
            continue
        entry: Json = {"name": item["name"], "type": item["type"], "link": None}
        if item.get("widget"):
            entry["widget"] = {"name": item["name"]}
        elif item.get("optional"):
            entry["shape"] = 7
        inputs.append(entry)
    return inputs


def _encode_node(
    node: Node, number: int, palette: Palette, box: tuple[int, int, int, int], linked: frozenset[str]
) -> Json:
    """Serialize one node with nothing linked."""
    schema = palette.find_schema(node)
    is_subgraph = node.kind in palette.subgraphs
    inputs = _encode_inputs(schema, linked)
    outputs: list[Json] = [
        {"name": item["name"], "type": item["type"], **({"shape": 6} if item.get("is_list") else {}), "links": []}
        for item in cast("list[Item]", schema["outputs"])
    ]
    kind = palette.ids[node.kind] if is_subgraph else node.kind
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
        "widgets_values": encode_widget_values(schema, node.values, node.kind),
    }
    if node.title or is_subgraph:
        entry["title"] = node.title or node.kind
    if node.is_paid:
        entry.update(PAID_COLOURS)
    return entry


def _find_slot(entry: Json, side: str, name: str) -> int:
    """Find the position of a serialized input or output."""
    sockets = cast("list[Json]", entry[side])
    index = next((index for index, socket in enumerate(sockets) if socket["name"] == name), None)
    if index is None:
        message = f"{entry['type']} has no {side[:-1]} named {name}."
        raise KeyError(message)
    return index


def _find_switch_types(entries: Mapping[str, Json], links: tuple[tuple[str, str], ...]) -> dict[str, object]:
    """Find the type each switch passes on: the type of the values linked into its matched inputs.

    ComfyUI saves a switch's any-type sockets with the type of the values that feed it once they are linked.
    """
    matched: dict[str, object] = {}
    for start, end in links:
        source_key, output = start.split(".", 1)
        target_key, input_name = end.split(".", 1)
        target = entries[target_key]
        socket = cast("list[Json]", target["inputs"])[_find_slot(target, "inputs", input_name)]
        origin = entries[source_key]
        kind = cast("list[Json]", origin["outputs"])[_find_slot(origin, "outputs", output)]["type"]
        if socket["type"] == MATCH_TYPE and kind != MATCH_TYPE:
            matched[target_key] = kind
    return matched


def _encode_ports(
    subgraph: Subgraph, subgraph_id: str, entries: dict[str, Json], records: list[Json], side: str
) -> list[Json]:
    """Link the exposed inputs or outputs to the inner nodes."""
    ports: list[Json] = []
    port_node, inner_side = (-10, "inputs") if side == "inputs" else (-20, "outputs")
    for name, socket in getattr(subgraph, side):
        port = next((port for port in ports if port["name"] == name), None)
        if port is None:
            port_id = str(uuid.uuid5(NAMESPACE, f"{subgraph_id}.{side}.{name}"))
            port = cast("Json", {"id": port_id, "name": name, "type": "", "linkIds": [], "pos": [0, 0]})
            ports.append(port)
        index = ports.index(port)
        key, socket_name = socket.split(".", 1)
        entry = entries[key]
        position = _find_slot(entry, inner_side, socket_name)
        number = len(records) + 1
        inner = cast("list[Json]", entry[inner_side])[position]
        if side == "inputs":
            inner["link"] = number
            record = {"origin_id": port_node, "origin_slot": index, "target_id": entry["id"], "target_slot": position}
        else:
            cast("list[int]", inner["links"]).append(number)
            record = {"origin_id": entry["id"], "origin_slot": position, "target_id": port_node, "target_slot": index}
        if inner["type"] == MATCH_TYPE:
            inner["type"] = _read_switch_type(entry)
        records.append({"id": number, **record, "type": inner["type"]})
        # A port takes the most specific type among the sockets it feeds.
        if port["type"] in {"", ANY_TYPE, MATCH_TYPE}:
            port["type"] = inner["type"]
        cast("list[int]", port["linkIds"]).append(number)
    return ports


def _read_switch_type(entry: Json) -> object:
    """Read the type a switch passes on from its sockets that links inside the subgraph already typed."""
    sockets = [*cast("list[Json]", entry["inputs"]), *cast("list[Json]", entry["outputs"])]
    typed = (socket["type"] for socket in sockets if socket["name"] != "switch" and socket["type"] != MATCH_TYPE)
    return next(typed, MATCH_TYPE)


def encode_nodes(
    nodes: tuple[Node, ...],
    palette: Palette,
    boxes: Mapping[str, tuple[int, int, int, int]],
    targets: Sequence[str],
    first_id: int = 1,
) -> dict[str, Json]:
    """Serialize nodes with nothing linked yet; the targets are the `node.socket` names links will fill."""
    linked = [target.split(".", 1) for target in targets]
    entries = {
        node.key: _encode_node(
            node,
            number,
            palette,
            boxes[node.key],
            frozenset(socket for key, socket in linked if key == node.key),
        )
        for number, node in enumerate(nodes, first_id)
    }
    if len(entries) != len(nodes):
        message = "Give every node its own key."
        raise ValueError(message)
    return entries


def encode_links(entries: Mapping[str, Json], links: tuple[tuple[str, str], ...]) -> list[Json]:
    """Link serialized nodes, and give each switch the type of the values it passes on."""
    records: list[Json] = []
    matched = _find_switch_types(entries, links)
    for number, (start, end) in enumerate(links, 1):
        # The node key comes first; the rest is the socket's full name, which can name a slot of a growing row.
        source_key, output = start.split(".", 1)
        target_key, input_name = end.split(".", 1)
        origin, target = entries[source_key], entries[target_key]
        origin_slot = _find_slot(origin, "outputs", output)
        target_slot = _find_slot(target, "inputs", input_name)
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
    return records


def read_preview_exposures(subgraph: Subgraph, position: int) -> list[Json]:
    """List the previews of nodes inside a subgraph that its placed node shows, such as a saved image.

    The inner node IDs follow the numbering `encode_subgraph` gives them.
    """
    keys = [node.key for node in subgraph.nodes]
    first_id = position * SUBGRAPH_ID_STEP + 1
    return [
        {"name": name, "sourceNodeId": str(first_id + keys.index(key)), "sourcePreviewName": name}
        for key, name in subgraph.previews
    ]


def encode_subgraph(subgraph: Subgraph, palette: Palette, position: int) -> Json:
    """Serialize one subgraph definition with its input and output ports."""
    subgraph_id = palette.ids[subgraph.name]
    # The input ports link sockets too, so the growing rows they feed show those slots.
    targets = [end for _start, end in (*subgraph.links, *subgraph.inputs)]
    linked = [target.split(".", 1) for target in targets]
    sizes = {
        node.key: measure(
            node.kind,
            palette.find_schema(node),
            node.values,
            frozenset(socket for key, socket in linked if key == node.key),
        )
        for node in subgraph.nodes
    }
    if subgraph.stacks:
        placed, groups = place_stacks(subgraph.stacks, sizes, INNER_ORIGIN)
    else:
        placed, groups = place_columns(subgraph.columns, sizes, INNER_ORIGIN), []
    boxes = {key: (box.x, box.y, box.width, box.height) for key, box in placed.items()}
    entries = encode_nodes(subgraph.nodes, palette, boxes, targets, position * SUBGRAPH_ID_STEP + 1)
    records = encode_links(entries, subgraph.links)
    inputs = _encode_ports(subgraph, subgraph_id, entries, records, "inputs")
    outputs = _encode_ports(subgraph, subgraph_id, entries, records, "outputs")
    right = max(box.right for box in placed.values()) + PORT_GAP
    for index, port in enumerate(inputs):
        port["pos"] = [INNER_ORIGIN[0] - PORT_GAP, INNER_ORIGIN[1] + 20 * index]
    for index, port in enumerate(outputs):
        port["pos"] = [right, INNER_ORIGIN[1] + 20 * index]
    return {
        "id": subgraph_id,
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
            "bounding": [
                INNER_ORIGIN[0] - PORT_GAP - PORT_WIDTH,
                INNER_ORIGIN[1],
                PORT_WIDTH,
                20 * max(1, len(inputs)),
            ],
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


__all__ = ["encode_links", "encode_nodes", "encode_subgraph", "read_preview_exposures"]
