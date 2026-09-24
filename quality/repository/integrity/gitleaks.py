"""Validate reviewed Gitleaks baseline metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, cast
from quality.lib.files import read_utf8
from datetime import UTC, date, datetime
from quality.lib.diagnostics import report_violations
from quality.lib.json_config import JsonConfigError, read_json_mapping, require_keys, require_mapping

if TYPE_CHECKING:
    from collections.abc import Mapping

BASELINE_PATH = Path("quality/config/security/gitleaks/baseline.json")
REASONS_PATH = Path("quality/config/security/gitleaks/reasons.json")


def _baseline_fingerprints(path: Path) -> tuple[set[str], list[str]]:
    """Return baseline fingerprints and structural violations."""
    try:
        payload: object = json.loads(read_utf8(path))
    except (RuntimeError, json.JSONDecodeError) as error:
        return set(), [f"{path.as_posix()}: invalid JSON: {error}"]
    if not isinstance(payload, list):
        return set(), [f"{path.as_posix()}: baseline must be an array"]

    entries = cast("list[object]", payload)
    fingerprints: set[str] = set()
    violations: list[str] = []
    for index, value in enumerate(entries):
        context = f"{path.as_posix()}[{index}]"
        if not isinstance(value, dict):
            violations.append(f"{context}: entry must be an object")
            continue
        entry: Mapping[object, object] = cast("Mapping[object, object]", value)
        fingerprint = entry.get("Fingerprint")
        if not isinstance(fingerprint, str) or not fingerprint:
            violations.append(f"{context}: Fingerprint must be a non-empty string")
        elif fingerprint in fingerprints:
            violations.append(f"{context}: duplicate fingerprint {fingerprint}")
        else:
            fingerprints.add(fingerprint)
    return fingerprints, violations


def _reason_fingerprints(path: Path, today: date) -> tuple[set[str], list[str]]:
    """Return reviewed reason fingerprints and schema violations."""
    try:
        payload = read_json_mapping(path)
    except JsonConfigError as error:
        return set(), [str(error)]
    violations: list[str] = []
    fingerprints: set[str] = set()
    for fingerprint, value in payload.items():
        context = f"{path.as_posix()}.{fingerprint}"
        violations.extend(reason_record_violations(value, context, today))
        fingerprints.add(fingerprint)
    return fingerprints, violations


def reason_record_violations(value: object, context: str, today: date) -> list[str]:
    """Return schema and expiry violations for one review record."""
    try:
        record = require_mapping(value, context)
        require_keys(record, required={"reason", "review_by"}, context=context)
    except JsonConfigError as error:
        return [str(error)]
    violations: list[str] = []
    reason = record["reason"]
    review_by = record["review_by"]
    if not isinstance(reason, str) or not reason.strip():
        violations.append(f"{context}.reason must be a non-empty string")
    if not isinstance(review_by, str):
        violations.append(f"{context}.review_by must be an ISO date")
        return violations
    try:
        review_date = date.fromisoformat(review_by)
    except ValueError:
        violations.append(f"{context}.review_by must be an ISO date")
    else:
        if review_date < today:
            violations.append(f"{context}.review_by expired on {review_by}")
    return violations


def gitleaks_metadata_violations(root: Path, *, today: date | None = None) -> list[str]:
    """Return baseline/reason mismatch, schema, and review-date violations."""
    review_date = datetime.now(tz=UTC).date() if today is None else today
    baseline, baseline_violations = _baseline_fingerprints(root / BASELINE_PATH)
    reasons, reason_violations = _reason_fingerprints(root / REASONS_PATH, review_date)
    violations = [*baseline_violations, *reason_violations]
    violations.extend(f"{REASONS_PATH.as_posix()}: missing reason for {item}" for item in sorted(baseline - reasons))
    violations.extend(f"{REASONS_PATH.as_posix()}: unknown fingerprint {item}" for item in sorted(reasons - baseline))
    return violations


def main() -> int:
    """Run Gitleaks baseline metadata integrity."""
    return report_violations(
        "Gitleaks baseline metadata violations:",
        gitleaks_metadata_violations(Path.cwd()),
    )


if __name__ == "__main__":
    raise SystemExit(main())
