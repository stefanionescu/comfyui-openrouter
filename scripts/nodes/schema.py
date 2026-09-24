"""Describe this extension's nodes and the ComfyUI nodes the workflows use.

Runs under the ComfyUI interpreter with the ComfyUI folder on the path, without starting the server. The
built-in nodes are loaded, so the host nodes are described where ComfyUI registers them.
"""

from __future__ import annotations

import os
import sys
import json
import asyncio
import inspect
import tempfile
import nodes as host
from typing import cast
from comfy_api.latest import io
from src.nodes import NODE_TYPES
from src.nodes.base import PaidNode
from scripts.nodes.host import HostNode
from src.comfy.runtime import create_runtime
from src.config.storage import STATE_DIRECTORY_VARIABLE
from src.config.generation.inputs import RUN_NUMBER_INPUT


def _build_node_schema(schema: io.Schema) -> dict[str, object]:
    """Describe one node's public metadata and outputs, and each input with its type, widget flag and limits."""
    inputs: list[dict[str, object]] = []
    for item in schema.inputs:
        fields = cast("dict[str, object]", item.as_dict())
        is_widget = isinstance(item, io.WidgetInput | io.DynamicCombo.Input) and not fields.get("forceInput")
        inputs.append({"name": item.id, "type": item.io_type, "widget": is_widget, **fields})
    return {
        "display_name": schema.display_name,
        "description": schema.description,
        "category": schema.category,
        "inputs": inputs,
        "outputs": [
            # ComfyUI names an output by its display name, or by its type when it has none.
            {"name": item.display_name or item.io_type, "type": item.io_type, "is_list": item.is_output_list}
            for item in schema.outputs
        ],
    }


def _build_host_schema(name: str) -> dict[str, object]:
    """Describe a ComfyUI node by its schema or input table."""
    node_class = cast("type[object]", host.NODE_CLASS_MAPPINGS[name])
    define_schema = getattr(node_class, "define_schema", None)
    if callable(define_schema):
        return _build_node_schema(cast("io.Schema", define_schema()))
    inputs: list[dict[str, object]] = []
    table = cast("dict[str, dict[str, tuple[object, ...]]]", getattr(node_class, "INPUT_TYPES")())  # noqa: B009 -- reason: The host class is typed as an arbitrary class here.
    for group in ("required", "optional"):
        for input_name, (kind, *rest) in table.get(group, {}).items():
            settings = cast("dict[str, object]", rest[0]) if rest else {}
            is_combo = isinstance(kind, list)
            is_widget = is_combo or (kind in {"STRING", "INT", "FLOAT", "BOOLEAN"} and not settings.get("forceInput"))
            inputs.append(
                {
                    "name": input_name,
                    "type": "COMBO" if is_combo else str(kind),
                    "widget": is_widget,
                    "optional": group == "optional",
                    "default": settings.get("default"),
                    # A host list such as Load Image's names the files of this machine, so none is kept.
                    "options": [],
                    "image_upload": bool(settings.get("image_upload")),
                }
            )
    kinds = cast("tuple[str, ...]", getattr(node_class, "RETURN_TYPES"))  # noqa: B009 -- reason: The host class is typed as an arbitrary class here.
    names = cast("tuple[str, ...]", getattr(node_class, "RETURN_NAMES", kinds))
    outputs = [{"name": n, "type": t, "is_list": False} for n, t in zip(names, kinds, strict=True)]
    return {"inputs": inputs, "outputs": outputs}


def _build_registered_schemas() -> dict[str, dict[str, object]]:
    """Describe every registered node, refusing a mismatched schema.

    A paid node receives its inputs through send, and the run number through its base class.
    """
    schemas: dict[str, dict[str, object]] = {}
    for node_type in NODE_TYPES:
        schema = node_type.define_schema()
        if schema.node_id in schemas:
            message = f"Register {schema.node_id} once."
            raise ValueError(message)
        if issubclass(node_type, PaidNode):
            parameters = {RUN_NUMBER_INPUT, *inspect.signature(node_type.send).parameters}
        else:
            parameters = set(inspect.signature(node_type.execute).parameters)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] -- reason: The host leaves execute untyped.
        if parameters != {item.id for item in schema.inputs}:
            message = f"Match the execute parameters of {schema.node_id} to its inputs."
            raise ValueError(message)
        schemas[schema.node_id] = _build_node_schema(schema)
    return schemas


def main() -> None:
    """Print the node descriptions of this extension and of the host nodes the workflows place.

    The extension's state folder is a new empty one, so Video: Download lists no jobs and the export is the
    same on every machine.
    """
    asyncio.run(host.init_extra_nodes(init_custom_nodes=False))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType] -- reason: The host loader is untyped.
    with tempfile.TemporaryDirectory(prefix="comfyui-openrouter-schema-") as state_directory:
        os.environ[STATE_DIRECTORY_VARIABLE] = state_directory
        create_runtime()
        export: dict[str, object] = {
            "nodes": _build_registered_schemas(),
            "host": {name: _build_host_schema(name) for name in HostNode},
        }
    sys.stdout.write(json.dumps(export) + "\n")


if __name__ == "__main__":
    main()
