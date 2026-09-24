"""Validate installed dependency licenses."""

from __future__ import annotations

import sys
from pathlib import Path
import importlib.metadata
from packaging.utils import canonicalize_name
from quality.repository.licenses.policy import LicenseExemption, read_license_policy

UNKNOWN_LICENSE = "UNKNOWN"

LICENSE_ALIASES = {
    "Apache License 2.0": "Apache-2.0",
    "Apache 2.0 License": "Apache-2.0",
    "Apache Software License": "Apache-2.0",
    "PSF-2.0": "Python-2.0",
    "PSFL": "Python-2.0",
    "Python Software Foundation License": "Python-2.0",
}
CLASSIFIER_LICENSES = (
    ("License :: OSI Approved :: MIT", "MIT"),
    ("License :: OSI Approved :: Apache", "Apache-2.0"),
    ("License :: OSI Approved :: BSD", "BSD"),
    ("License :: OSI Approved :: ISC", "ISC"),
    ("License :: OSI Approved :: Mozilla Public License 2.0", "MPL-2.0"),
)


def normalized_license(metadata: importlib.metadata.PackageMetadata) -> str:
    """Return the best available license identifier."""
    expression = (metadata.get_all("License-Expression") or [""])[0]
    license_name = expression
    if not license_name:
        classifiers = metadata.get_all("Classifier") or []
        license_name = next(
            (
                license_value
                for classifier in classifiers
                for classifier_prefix, license_value in CLASSIFIER_LICENSES
                if classifier.startswith(classifier_prefix)
            ),
            "",
        )
    if not license_name:
        raw_license = (metadata.get_all("License") or [""])[0] or UNKNOWN_LICENSE
        license_name = raw_license.splitlines()[0].strip()
    return LICENSE_ALIASES.get(license_name, license_name)


def license_violation(
    package_name: str,
    observed_license: str,
    allowed_licenses: set[str],
    exemptions: dict[str, LicenseExemption],
) -> str | None:
    """Return one license policy violation, including exemption drift."""
    canonical_name = str(canonicalize_name(package_name))
    exemption = exemptions.get(canonical_name)
    if exemption is not None:
        if observed_license in exemption["licenses"]:
            return None
        expected = ", ".join(sorted(exemption["licenses"]))
        return f"{package_name}: license metadata changed; expected {expected}, observed {observed_license}"
    if observed_license not in allowed_licenses:
        return f"{package_name}: {observed_license}"
    return None


def main() -> int:
    """Run dependency license policy."""
    policy = read_license_policy(Path.cwd())
    allowed = set(policy["allowed_licenses"])
    exemptions = {item["package"]: item for item in policy["package_exemptions"]}
    violations: list[str] = []
    for distribution in importlib.metadata.distributions():
        name = (distribution.metadata.get_all("Name") or [""])[0]
        license_name = normalized_license(distribution.metadata)
        violation = license_violation(name, license_name, allowed, exemptions)
        if violation is not None:
            violations.append(violation)
    if not violations:
        return 0
    sys.stderr.write("License policy violations:\n")
    for violation in sorted(violations):
        sys.stderr.write(f"- {violation}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
