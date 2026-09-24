"""Repository configuration-boundary policy."""

CONFIG_IMPORT_ROOTS = {
    "__future__",
    "collections.abc",
    "src.config",
    "quality.config",
    "typing",
}

DECLARATIVE_EXCLUSIONS: tuple[str, ...] = ()
