"""The shapes the build scripts pass around: node descriptions, their inputs, and workflow JSON."""

# The description of a node as the schema export gives it, and one of its inputs or outputs.
type Schema = dict[str, object]
type Item = dict[str, object]
# One node, link, or subgraph as ComfyUI saves it in a workflow file.
type Json = dict[str, object]
# A value a workflow description gives the widget of a node.
type WidgetValue = str | int | float | bool | list[str]

# Other modules import the type aliases by name; __all__ lists runtime names.
__all__: list[str] = []
