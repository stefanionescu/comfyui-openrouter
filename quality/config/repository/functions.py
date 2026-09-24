"""Function policy location, closed schema members and the host methods it exempts."""

FUNCTION_POLICY_PATH = "quality/config/repository/functions.json"
FUNCTION_POLICY_VERSION = 1
# ComfyUI calls these methods on a node class itself, so they cannot be inlined at a caller.
# The paid nodes reach ComfyNode through the extension's shared base class.
HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode")
HOST_NODE_HOOKS = ("define_schema", "execute", "fingerprint_inputs", "validate_inputs")
