"""Describe a workflow as nodes, links, groups and the subgraphs it places."""

from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from dataclasses import dataclass
from types import MappingProxyType
from scripts.workflows.page.config import INPUT_COLOUR

if TYPE_CHECKING:
    from collections.abc import Mapping

WidgetValue = str | int | float | bool | list[str]
NO_VALUES: Mapping[str, WidgetValue] = MappingProxyType({})
NAMESPACE = uuid.UUID("6f1c0c7e-3b2a-4f7e-9d3a-2f0b4e6a8c10")


@dataclass(frozen=True, slots=True)
class Node:
    """One node, with the widget values that differ from its defaults; a bypassed node ships switched off."""

    key: str
    kind: str
    values: Mapping[str, WidgetValue] = NO_VALUES
    title: str = ""
    is_paid: bool = False
    is_bypassed: bool = False


@dataclass(frozen=True, slots=True)
class Group:
    """One titled frame around columns of nodes."""

    title: str
    columns: tuple[tuple[str, ...], ...]
    colour: str = INPUT_COLOUR


@dataclass(frozen=True, slots=True)
class Subgraph:
    """A reusable graph placed as one node; each link runs from `node.output` to `node.input`."""

    name: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    columns: tuple[tuple[str, ...], ...] = ()
    inputs: tuple[tuple[str, str], ...] = ()
    outputs: tuple[tuple[str, str], ...] = ()
    description: str = ""
    stacks: tuple[tuple[Group, ...], ...] = ()

    @property
    def id(self) -> str:
        """Derive the subgraph ID from its name."""
        return str(uuid.uuid5(NAMESPACE, self.name))


@dataclass(frozen=True, slots=True)
class Workflow:
    """One shipped workflow; each link runs from `node.output` to `node.input`."""

    slug: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    stacks: tuple[tuple[Group, ...], ...]
    subgraphs: tuple[Subgraph, ...] = ()


__all__ = [
    "NO_VALUES",
    "Group",
    "Node",
    "Subgraph",
    "WidgetValue",
    "Workflow",
]
