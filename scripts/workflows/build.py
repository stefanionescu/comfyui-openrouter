"""Build the shipped workflows, or check that the shipped files match."""

from __future__ import annotations

import sys
import json
import uuid
import argparse
from scripts.config import NOTE
from src.paths import EXTENSION_ROOT
from typing import cast, TYPE_CHECKING
from scripts.nodes.check import read_schemas
from scripts.workflows.page.config import NOTE_WIDTH
from scripts.workflows.page.layout import place_stacks
from scripts.workflows.page.graph import Node, NAMESPACE
from scripts.workflows.descriptions.chat import CHAT_WORKFLOWS
from scripts.workflows.page.sizes import measure, measure_note
from scripts.workflows.descriptions.audio import AUDIO_WORKFLOWS
from scripts.workflows.descriptions.image import IMAGE_WORKFLOWS
from scripts.workflows.descriptions.video import VIDEO_WORKFLOWS
from scripts.workflows.descriptions.design import DESIGN_WORKFLOWS
from scripts.workflows.descriptions.search import SEARCH_WORKFLOWS
from scripts.workflows.descriptions.decision import DECISION_WORKFLOWS
from scripts.workflows.descriptions.texts import SHARED_TEXTS, WORKFLOW_TEXTS
from scripts.workflows.page.serialize import Json, Palette, serialize_graph, serialize_subgraph

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Iterable
    from scripts.workflows.page.graph import Workflow

WORKFLOWS = (
    *CHAT_WORKFLOWS,
    *IMAGE_WORKFLOWS,
    *DESIGN_WORKFLOWS,
    *VIDEO_WORKFLOWS,
    *AUDIO_WORKFLOWS,
    *SEARCH_WORKFLOWS,
    *DECISION_WORKFLOWS,
)


def build_palette(export: dict[str, object]) -> Palette:
    """Build the table of every node the workflows may place."""
    schemas = cast("dict[str, dict[str, object]]", export["nodes"]) | cast(
        "dict[str, dict[str, object]]", export["host"]
    )
    subgraphs = {subgraph.name: subgraph for workflow in WORKFLOWS for subgraph in workflow.subgraphs}
    return Palette(schemas, subgraphs)


def check_coverage(node_ids: Iterable[str]) -> list[str]:
    """Report every workflow the README does not link and every node no workflow places."""
    readme = (EXTENSION_ROOT / "README.md").read_text(encoding="utf-8")
    problems = [
        f"Link example_workflows/{workflow.slug}.json from README.md."
        for workflow in WORKFLOWS
        if f"(example_workflows/{workflow.slug}.json)" not in readme
    ]
    placed = {node.kind for workflow in WORKFLOWS for node in workflow.nodes}
    problems += [f"Add a workflow for {node_id}." for node_id in sorted(node_ids) if node_id not in placed]
    return problems


def serialize_workflow(workflow: Workflow, palette: Palette) -> Json:
    """Serialize one workflow: its two notes, placed nodes, links, group frames and subgraph definitions."""
    texts = WORKFLOW_TEXTS[workflow.slug]
    notes = (
        Node("note", NOTE, {"text": texts["start"]}, title=SHARED_TEXTS["start"]),
        Node("using", NOTE, {"text": texts["using"]}, title=SHARED_TEXTS["using"]),
    )
    sizes = {note.key: (NOTE_WIDTH, measure_note(str(note.values["text"]))) for note in notes}
    # A growing row of sockets shows each linked slot and one more, so the links decide a node's height.
    targets = [end.split(".", 1) for _start, end in workflow.links]
    sizes |= {
        node.key: measure(
            node.kind,
            palette.schema(node),
            node.values,
            frozenset(socket for key, socket in targets if key == node.key),
        )
        for node in workflow.nodes
    }
    boxes, groups = place_stacks(workflow.stacks, sizes, notes=[note.key for note in notes])
    grouped = sum(len(column) for stack in workflow.stacks for group in stack for column in group.columns)
    if set(boxes) != set(sizes) or len(boxes) != grouped + len(notes):
        message = f"Place every node of {workflow.slug} in exactly one group."
        raise ValueError(message)
    entries, records = serialize_graph(
        (*notes, *workflow.nodes),
        workflow.links,
        palette,
        {key: (box.x, box.y, box.width, box.height) for key, box in boxes.items()},
    )
    links = [[r["id"], r["origin_id"], r["origin_slot"], r["target_id"], r["target_slot"], r["type"]] for r in records]
    serialized: Json = {
        "id": str(uuid.uuid5(NAMESPACE, workflow.slug)),
        "revision": 0,
        "last_node_id": len(entries),
        "last_link_id": len(links),
        "nodes": list(entries.values()),
        "links": links,
        "groups": groups,
        "config": {},
        "extra": {"ds": {"scale": 0.5, "offset": [30, 30]}},
        "version": 0.4,
    }
    if workflow.subgraphs:
        subgraphs = [serialize_subgraph(s, palette, position) for position, s in enumerate(workflow.subgraphs, 1)]
        serialized["definitions"] = {"subgraphs": subgraphs}
    return serialized


def compare_shipped_file(path: Path, content: Json) -> str | None:
    """Say whether a shipped file matches its build."""
    if not path.is_file():
        return f"Build {path.relative_to(EXTENSION_ROOT)} with mise run comfy:workflows:build."
    is_same = json.loads(path.read_text(encoding="utf-8")) == content
    return None if is_same else f"Rebuild {path.relative_to(EXTENSION_ROOT)} with mise run comfy:workflows:build."


def main() -> int:
    """Build every workflow, or report the shipped files that differ."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    export = read_schemas()
    palette = build_palette(export)
    outputs: dict[Path, Json] = {
        EXTENSION_ROOT / "example_workflows" / f"{workflow.slug}.json": serialize_workflow(workflow, palette)
        for workflow in WORKFLOWS
    }
    problems = [
        f"Remove or describe {path.relative_to(EXTENSION_ROOT)}."
        for path in (EXTENSION_ROOT / "example_workflows").glob("*.json")
        if path not in outputs
    ]
    problems += check_coverage(cast("dict[str, object]", export["nodes"]))
    for path, content in outputs.items():
        if arguments.check:
            problem = compare_shipped_file(path, content)
            if problem:
                problems.append(problem)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
