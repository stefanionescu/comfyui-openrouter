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
from scripts.workflows.page.palette import Palette
from scripts.workflows.page.graph import Node, NAMESPACE
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.chat import CHAT_WORKFLOWS
from scripts.workflows.page.sizes import measure, measure_note
from scripts.workflows.descriptions.audio import AUDIO_WORKFLOWS
from scripts.workflows.descriptions.image import IMAGE_WORKFLOWS
from scripts.workflows.descriptions.video import VIDEO_WORKFLOWS
from scripts.workflows.descriptions.design import DESIGN_WORKFLOWS
from scripts.workflows.descriptions.search import SEARCH_WORKFLOWS
from scripts.workflows.page.layout import place_stacks, place_columns
from scripts.workflows.descriptions.decision import DECISION_WORKFLOWS
from scripts.workflows.page.serialize import (
    Json,
    link_nodes,
    serialize_nodes,
    serialize_subgraph,
    read_preview_exposures,
)

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Mapping, Iterable
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


def build_palette(export: dict[str, object], workflow: Workflow) -> Palette:
    """Build the table of every node one workflow may place.

    A subgraph's ID comes from its workflow and name, so two workflows can each define their own Check.
    """
    schemas = cast("dict[str, dict[str, object]]", export["nodes"]) | cast(
        "dict[str, dict[str, object]]", export["host"]
    )
    subgraphs = {subgraph.name: subgraph for subgraph in workflow.subgraphs}
    ids = {name: str(uuid.uuid5(NAMESPACE, f"{workflow.slug}/{name}")) for name in subgraphs}
    return Palette(schemas, subgraphs, ids)


def check_coverage(node_ids: Iterable[str]) -> list[str]:
    """Report every workflow the README does not link and every node no workflow places."""
    readme = (EXTENSION_ROOT / "README.md").read_text(encoding="utf-8")
    problems = [
        f"Link example_workflows/{workflow.slug}.json from README.md."
        for workflow in WORKFLOWS
        if f"(example_workflows/{workflow.slug}.json)" not in readme
    ]
    placed = {node.kind for workflow in WORKFLOWS for node in workflow.nodes}
    placed |= {node.kind for workflow in WORKFLOWS for subgraph in workflow.subgraphs for node in subgraph.nodes}
    problems += [f"Add a workflow for {node_id}." for node_id in sorted(node_ids) if node_id not in placed]
    return problems


def make_notes(
    workflow: Workflow, sizes: Mapping[str, tuple[int, int]]
) -> tuple[dict[str, Node], dict[str, tuple[int, int]]]:
    """Make each group's note, keyed by the group's title, with its size.

    A note is as wide as its group's columns, and every note is as tall as the tallest, so the nodes below the
    notes start on one line across the groups.
    """
    groups = [group for stack in workflow.stacks for group in stack]
    if len({group.title for group in groups}) != len(groups) or not all(group.note for group in groups):
        message = f"Give every group of {workflow.slug} its own title and a note."
        raise ValueError(message)
    notes = {
        group.title: Node(
            f"note_{number}",
            NOTE,
            {"text": group.note},
            title=SHARED_TEXTS["start"] if number == 1 else SHARED_TEXTS["note"],
        )
        for number, group in enumerate(groups, 1)
    }
    # A group's columns, placed from the left edge, end at its width.
    widths = {
        group.title: max(box.right for box in place_columns(group.columns, sizes, (0, 0)).values()) for group in groups
    }
    height = max(measure_note(group.note, widths[group.title]) for group in groups)
    return notes, {notes[title].key: (width, height) for title, width in widths.items()}


def serialize_workflow(workflow: Workflow, palette: Palette) -> Json:
    """Serialize one workflow: a note in every group, the placed nodes, links, group frames and subgraphs."""
    # A growing row of sockets shows each linked slot and one more, so the links decide a node's height.
    targets = [end.split(".", 1) for _start, end in workflow.links]
    sizes = {
        node.key: measure(
            node.kind,
            palette.schema(node),
            node.values,
            frozenset(socket for key, socket in targets if key == node.key),
        )
        for node in workflow.nodes
    }
    notes, note_sizes = make_notes(workflow, sizes)
    sizes |= note_sizes
    boxes, groups = place_stacks(workflow.stacks, sizes, notes={title: note.key for title, note in notes.items()})
    grouped = sum(len(column) for stack in workflow.stacks for group in stack for column in group.columns)
    if set(boxes) != set(sizes) or len(boxes) != grouped + len(notes):
        message = f"Place every node of {workflow.slug} in exactly one group."
        raise ValueError(message)
    entries = serialize_nodes(
        (*notes.values(), *workflow.nodes),
        palette,
        {key: (box.x, box.y, box.width, box.height) for key, box in boxes.items()},
        [end for _start, end in workflow.links],
    )
    records = link_nodes(entries, workflow.links)
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
    # A placed subgraph shows the results saved inside it, so a run can be read without opening it.
    for position, subgraph in enumerate(workflow.subgraphs, 1):
        exposures = read_preview_exposures(subgraph, position)
        for node in workflow.nodes:
            if node.kind == subgraph.name and exposures:
                cast("Json", entries[node.key]["properties"])["previewExposures"] = exposures
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
    outputs: dict[Path, Json] = {
        EXTENSION_ROOT / "example_workflows" / f"{workflow.slug}.json": serialize_workflow(
            workflow, build_palette(export, workflow)
        )
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
