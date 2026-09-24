"""Python rule policy."""

from __future__ import annotations

FORBIDDEN_EXPORT_HOOKS = {
    "__getattr__",
    "__dir__",
    "__getattribute__",
}

RUNTIME_ROOT_PACKAGE = "src"
MUTABLE_RECORD_TYPES = {"list", "dict", "set", "bytearray", "Counter", "collections.Counter"}
FORBIDDEN_RUNTIME_IMPORT_ROOTS = {"tests", "quality", "scripts"}
DOCSTRING_SOURCE_PREFIXES = ("src/", "config/", "scripts/", "quality/")
PLACEHOLDER_DOCSTRING_PREFIXES = ("Handle ", "Provide ")

SINGLETON_CLASS_SUFFIX = "Singleton"
SINGLETON_FUNCTION_NAMES = {
    "get_instance",
    "reset_instance",
}
SINGLETON_STATE_NAMES = {
    "_STATE",
    "STATE",
    "_INSTANCE",
    "INSTANCE",
}
