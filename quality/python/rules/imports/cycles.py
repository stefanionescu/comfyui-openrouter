"""Import-cycle traversal."""

from __future__ import annotations


class CycleTraversal:
    """Tarjan traversal state for import cycle checks."""

    def __init__(self, edges: dict[str, set[str]]) -> None:
        """Initialize traversal state."""
        self.edges = edges
        self.index = 0
        self.stack: list[str] = []
        self.on_stack: set[str] = set()
        self.index_by_node: dict[str, int] = {}
        self.lowlink_by_node: dict[str, int] = {}
        self.components: list[list[str]] = []

    def components_for(self, modules: set[str]) -> list[list[str]]:
        """Return cycle components for the provided modules."""
        for module in sorted(modules):
            if module not in self.index_by_node:
                self.visit(module)
        return self.components

    def visit(self, node: str) -> None:
        """Visit one node in the traversal."""
        self.index_by_node[node] = self.index
        self.lowlink_by_node[node] = self.index
        self.index += 1
        self.stack.append(node)
        self.on_stack.add(node)
        for neighbor in self.edges.get(node, set()):
            self.visit_neighbor(node, neighbor)
        if self.lowlink_by_node[node] == self.index_by_node[node]:
            self.finish_component(node)

    def visit_neighbor(self, node: str, neighbor: str) -> None:
        """Update lowlink state for one outgoing edge."""
        if neighbor not in self.index_by_node:
            self.visit(neighbor)
            self.lowlink_by_node[node] = min(self.lowlink_by_node[node], self.lowlink_by_node[neighbor])
        elif neighbor in self.on_stack:
            self.lowlink_by_node[node] = min(self.lowlink_by_node[node], self.index_by_node[neighbor])

    def finish_component(self, node: str) -> None:
        """Record one completed cycle component."""
        component: list[str] = []
        while self.stack:
            popped = self.stack.pop()
            self.on_stack.remove(popped)
            component.append(popped)
            if popped == node:
                break
        self.components.append(component)
