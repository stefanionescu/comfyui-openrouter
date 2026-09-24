"""Load Python import and package policies."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from quality.lib.json_config import (
    require_int,
    require_bool,
    require_keys,
    JsonConfigError,
    require_sequence,
    read_json_mapping,
    require_string_list,
)
from quality.config.python.schema import (
    IMPORT_POLICY_PATH,
    PACKAGE_POLICY_PATH,
    PACKAGE_API_PAIR_SIZE,
    POLICY_SCHEMA_VERSION,
)

if TYPE_CHECKING:
    from pathlib import Path


class ImportPolicy(TypedDict):
    """Validated Python import policy."""

    version: int
    package_roots: list[str]
    are_relative_imports_allowed: bool
    allow_imports_after_statements: list[str]
    are_dynamic_imports_banned: bool


class PackagePolicy(TypedDict):
    """Validated package export policy."""

    version: int
    max_package_exports: int
    allow_package_api_imports: list[list[str]]
    allow_export_only_files: list[str]
    are_constant_aliases_banned: bool


def read_import_policy(root: Path) -> ImportPolicy:
    """Read the validated import placement and boundary policy."""
    payload = read_json_mapping(root / IMPORT_POLICY_PATH)
    require_keys(
        payload,
        required={
            "version",
            "package_roots",
            "are_relative_imports_allowed",
            "allow_imports_after_statements",
            "are_dynamic_imports_banned",
        },
        context=IMPORT_POLICY_PATH,
    )
    require_version(payload["version"], IMPORT_POLICY_PATH)
    package_roots = require_string_list(
        payload["package_roots"], f"{IMPORT_POLICY_PATH}.package_roots", is_nonempty=True
    )
    for package_root in package_roots:
        if not (root / package_root).is_dir():
            message = f"{IMPORT_POLICY_PATH}.package_roots references missing directory {package_root}"
            raise JsonConfigError(message)
    require_bool(payload["are_relative_imports_allowed"], f"{IMPORT_POLICY_PATH}.are_relative_imports_allowed")
    late_import_paths = require_string_list(
        payload["allow_imports_after_statements"],
        f"{IMPORT_POLICY_PATH}.allow_imports_after_statements",
    )
    for relative_path in late_import_paths:
        if not (root / relative_path).is_file():
            message = f"{IMPORT_POLICY_PATH}.allow_imports_after_statements references missing file {relative_path}"
            raise JsonConfigError(message)
    require_bool(payload["are_dynamic_imports_banned"], f"{IMPORT_POLICY_PATH}.are_dynamic_imports_banned")
    return {
        "version": require_int(payload["version"], f"{IMPORT_POLICY_PATH}.version", minimum=1),
        "package_roots": package_roots,
        "are_relative_imports_allowed": require_bool(
            payload["are_relative_imports_allowed"],
            f"{IMPORT_POLICY_PATH}.are_relative_imports_allowed",
        ),
        "allow_imports_after_statements": late_import_paths,
        "are_dynamic_imports_banned": require_bool(
            payload["are_dynamic_imports_banned"],
            f"{IMPORT_POLICY_PATH}.are_dynamic_imports_banned",
        ),
    }


def read_package_policy(root: Path) -> PackagePolicy:
    """Read the validated package export policy."""
    payload = read_json_mapping(root / PACKAGE_POLICY_PATH)
    require_keys(
        payload,
        required={
            "version",
            "max_package_exports",
            "allow_package_api_imports",
            "allow_export_only_files",
            "are_constant_aliases_banned",
        },
        context=PACKAGE_POLICY_PATH,
    )
    require_version(payload["version"], PACKAGE_POLICY_PATH)
    max_package_exports = require_int(
        payload["max_package_exports"],
        f"{PACKAGE_POLICY_PATH}.max_package_exports",
        minimum=1,
    )
    pairs = require_sequence(payload["allow_package_api_imports"], f"{PACKAGE_POLICY_PATH}.allow_package_api_imports")
    validated_pairs: list[list[str]] = []
    for index, pair in enumerate(pairs):
        values = require_string_list(
            pair, f"{PACKAGE_POLICY_PATH}.allow_package_api_imports[{index}]", is_nonempty=True
        )
        if len(values) != PACKAGE_API_PAIR_SIZE:
            message = f"{PACKAGE_POLICY_PATH}.allow_package_api_imports[{index}] must contain two names"
            raise JsonConfigError(message)
        validated_pairs.append(values)
    return {
        "version": require_int(payload["version"], f"{PACKAGE_POLICY_PATH}.version", minimum=1),
        "max_package_exports": max_package_exports,
        "allow_package_api_imports": validated_pairs,
        "allow_export_only_files": require_string_list(
            payload["allow_export_only_files"],
            f"{PACKAGE_POLICY_PATH}.allow_export_only_files",
        ),
        "are_constant_aliases_banned": require_bool(
            payload["are_constant_aliases_banned"],
            f"{PACKAGE_POLICY_PATH}.are_constant_aliases_banned",
        ),
    }


def require_version(value: object, context: str) -> None:
    """Require the supported policy schema version."""
    if require_int(value, f"{context}.version", minimum=1) != POLICY_SCHEMA_VERSION:
        message = f"{context}.version must be {POLICY_SCHEMA_VERSION}"
        raise JsonConfigError(message)
