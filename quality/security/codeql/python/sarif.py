"""Require CodeQL SARIF runs to contain no findings."""

from __future__ import annotations

import sys
import json
from typing import cast
from pathlib import Path
from quality.lib.files import read_utf8
from quality.lib.output import write_error
from collections.abc import Mapping, Sequence


def validate_sarif_results(path: Path) -> int:
    """Validate strict SARIF structure and report every CodeQL finding."""
    try:
        payload: object = json.loads(read_utf8(path))
        findings = sarif_findings(payload)
    except (RuntimeError, TypeError, ValueError) as error:
        write_error(f"Invalid CodeQL SARIF: {error}")
        return 2
    if not findings:
        return 0
    write_error("CodeQL findings:")
    for rule_id, uri, line, _message in findings:
        write_error(f"- {rule_id}: {uri}:{line}")
    return 1


def sarif_findings(payload: object) -> list[tuple[str, str, int, str]]:
    """Return validated finding details from a SARIF payload."""
    root = require_mapping(payload, "SARIF root")
    runs = require_sequence(required_member(root, "runs", "SARIF root"), "SARIF runs")
    if not runs:
        msg = "CodeQL returned no analysis runs."
        raise ValueError(msg)
    findings: list[tuple[str, str, int, str]] = []
    for run_index, run_value in enumerate(runs):
        run_context = f"SARIF runs[{run_index}]"
        run = require_mapping(run_value, run_context)
        for invocation in require_sequence(run.get("invocations", []), f"{run_context}.invocations"):
            if require_mapping(invocation, "CodeQL invocation").get("executionSuccessful") is False:
                msg = "CodeQL did not complete its analysis."
                raise ValueError(msg)
        results = require_sequence(required_member(run, "results", run_context), f"{run_context}.results")
        for result_index, result_value in enumerate(results):
            finding = parse_result(result_value, f"{run_context}.results[{result_index}]")
            findings.append(finding)
    return findings


def parse_result(value: object, context: str) -> tuple[str, str, int, str]:
    """Return one fully validated SARIF result."""
    result = require_mapping(value, context)
    rule_id = require_nonempty_string(required_member(result, "ruleId", context), f"{context}.ruleId")
    message_value = require_mapping(required_member(result, "message", context), f"{context}.message")
    result_text = result_message(message_value, f"{context}.message")
    locations = require_sequence(required_member(result, "locations", context), f"{context}.locations")
    if not locations:
        error_message = f"{context}.locations must contain at least one location"
        raise ValueError(error_message)
    location = require_mapping(locations[0], f"{context}.locations[0]")
    physical = require_mapping(
        required_member(location, "physicalLocation", f"{context}.locations[0]"),
        f"{context}.locations[0].physicalLocation",
    )
    artifact = require_mapping(
        required_member(physical, "artifactLocation", f"{context}.locations[0].physicalLocation"),
        f"{context}.locations[0].physicalLocation.artifactLocation",
    )
    uri = require_nonempty_string(
        required_member(artifact, "uri", f"{context}.locations[0].physicalLocation.artifactLocation"),
        f"{context}.locations[0].physicalLocation.artifactLocation.uri",
    )
    region = require_mapping(
        required_member(physical, "region", f"{context}.locations[0].physicalLocation"),
        f"{context}.locations[0].physicalLocation.region",
    )
    line = require_positive_int(
        required_member(region, "startLine", f"{context}.locations[0].physicalLocation.region"),
        f"{context}.locations[0].physicalLocation.region.startLine",
    )
    return rule_id, uri, line, result_text


def result_message(value: Mapping[str, object], context: str) -> str:
    """Return the text or Markdown message from one SARIF result."""
    for key in ("text", "markdown"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    message = f"{context} must contain non-empty text or markdown"
    raise ValueError(message)


def required_member(value: Mapping[str, object], key: str, context: str) -> object:
    """Return one required mapping member."""
    if key not in value:
        message = f"{context} is missing {key}"
        raise ValueError(message)
    return value[key]


def require_mapping(value: object, context: str) -> Mapping[str, object]:
    """Return a string-keyed mapping."""
    if not isinstance(value, Mapping):
        message = f"{context} must be an object"
        raise TypeError(message)
    mapping = cast("Mapping[object, object]", value)
    if any(not isinstance(key, str) for key in mapping):
        message = f"{context} must be an object with string keys"
        raise ValueError(message)
    return cast("Mapping[str, object]", value)


def require_sequence(value: object, context: str) -> Sequence[object]:
    """Return a non-string sequence."""
    if not isinstance(value, Sequence) or isinstance(value, str):
        message = f"{context} must be an array"
        raise TypeError(message)
    return cast("Sequence[object]", value)


def require_nonempty_string(value: object, context: str) -> str:
    """Return a non-empty string."""
    if not isinstance(value, str) or not value:
        message = f"{context} must be a non-empty string"
        raise ValueError(message)
    return value


def require_positive_int(value: object, context: str) -> int:
    """Return a positive integer while rejecting Boolean values."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        message = f"{context} must be a positive integer"
        raise ValueError(message)
    return value


def main(argument_values: list[str] | None = None) -> int:
    """Validate one CodeQL SARIF file."""
    arguments = sys.argv[1:] if argument_values is None else argument_values
    if len(arguments) != 1:
        write_error("Usage: python -m quality.security.codeql.python.sarif SARIF_PATH")
        return 2
    return validate_sarif_results(Path(arguments[0]))


if __name__ == "__main__":
    raise SystemExit(main())
