"""Download immutable rule versions and verify their complete contents."""

from __future__ import annotations

import json
import yaml
import hashlib
import http.client
from http import HTTPStatus
from dataclasses import dataclass
from quality.lib.json_config import require_mapping, require_sequence


@dataclass(frozen=True, slots=True)
class RulePin:
    """Registry version and content digest for one named rule.

    Attributes:
        identifier: Registry rule identity.
        version: Pinned registry version.
        digest: Expected content SHA-256.

    """

    identifier: str
    version: str
    digest: str


def read_rules(host: str, path: str, timeout: int) -> list[dict[str, object]]:
    """Read a public registry response without redirects or executable YAML constructors."""
    connection = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        connection.request("GET", path, headers={"Accept": "application/json"})
        response = connection.getresponse()
        if response.status != HTTPStatus.OK:
            message = f"Semgrep registry returned HTTP {response.status} for {path}."
            raise RuntimeError(message)
        document = require_mapping(yaml.safe_load(response.read()), "Semgrep response")
    finally:
        connection.close()
    rules = require_sequence(document.get("rules"), "Semgrep rules")
    return [require_mapping(rule, "Semgrep rule") for rule in rules]


def check_rule(pin: RulePin, rule: dict[str, object], adjustments: dict[str, object]) -> bool:
    """Apply the configured example-token exclusions and verify the full rule content."""
    rule["id"] = pin.identifier
    rule.update(require_mapping(adjustments.get(pin.identifier, {}), "Semgrep rule adjustments"))
    encoded = json.dumps(rule, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest() == pin.digest


def download_rule(
    pin: RulePin, *, host: str, prefix: str, timeout: int, adjustments: dict[str, object]
) -> dict[str, object]:
    """Reject a downloaded rule unless its complete contents match the pinned digest."""
    rules = read_rules(host, prefix + pin.version, timeout)
    if len(rules) != 1:
        message = f"Expected one pinned Semgrep rule for {pin.identifier}."
        raise ValueError(message)
    rule = rules[0]
    if not check_rule(pin, rule, adjustments):
        message = f"Semgrep rule {pin.identifier} differs from its pinned content."
        raise ValueError(message)
    return rule
