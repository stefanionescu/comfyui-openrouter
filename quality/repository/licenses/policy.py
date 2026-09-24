"""Load the closed dependency license policy schema."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from packaging.utils import canonicalize_name
from quality.config.repository.paths import LICENSE_POLICY_FILE
from quality.lib.json_config import (
    require_keys,
    JsonConfigError,
    require_mapping,
    require_sequence,
    read_json_mapping,
    require_string_list,
)

if TYPE_CHECKING:
    from pathlib import Path


class LicenseExemption(TypedDict):
    """One package license-metadata exemption."""

    package: str
    licenses: list[str]
    reason: str


class LicensePolicy(TypedDict):
    """Validated dependency license policy."""

    allowed_licenses: list[str]
    package_exemptions: list[LicenseExemption]


def read_license_policy(root: Path) -> LicensePolicy:
    """Read validated allowed-license and package-exemption lists."""
    payload = read_json_mapping(root / LICENSE_POLICY_FILE)
    require_keys(payload, required={"allowed_licenses", "package_exemptions"}, context=LICENSE_POLICY_FILE)
    allowed = require_string_list(
        payload["allowed_licenses"],
        f"{LICENSE_POLICY_FILE}.allowed_licenses",
        is_nonempty=True,
    )
    exemptions: list[LicenseExemption] = []
    seen_packages: set[str] = set()
    context = f"{LICENSE_POLICY_FILE}.package_exemptions"
    for index, item in enumerate(require_sequence(payload["package_exemptions"], context)):
        item_context = f"{context}[{index}]"
        exemptions.append(parse_license_exemption(item, item_context, seen_packages))
    return {"allowed_licenses": allowed, "package_exemptions": exemptions}


def parse_license_exemption(
    value: object,
    context: str,
    seen_packages: set[str],
) -> LicenseExemption:
    """Return one validated package license exemption."""
    exemption = require_mapping(value, context)
    require_keys(exemption, required={"package", "licenses", "reason"}, context=context)
    package = exemption["package"]
    reason = exemption["reason"]
    if not isinstance(package, str) or not package:
        message = f"{context}.package must be a non-empty string"
        raise JsonConfigError(message)
    if not isinstance(reason, str) or not reason:
        message = f"{context}.reason must be a non-empty string"
        raise JsonConfigError(message)
    canonical_package = str(canonicalize_name(package))
    if package != canonical_package:
        message = f"{context}.package must use canonical name {canonical_package}"
        raise JsonConfigError(message)
    if canonical_package in seen_packages:
        message = f"{context}.package duplicates {canonical_package}"
        raise JsonConfigError(message)
    seen_packages.add(canonical_package)
    licenses = require_string_list(exemption["licenses"], f"{context}.licenses", is_nonempty=True)
    if len(licenses) != len(set(licenses)):
        message = f"{context}.licenses must not contain duplicates"
        raise JsonConfigError(message)
    return {"package": canonical_package, "licenses": licenses, "reason": reason}
