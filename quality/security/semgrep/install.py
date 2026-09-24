"""Install verified Semgrep rule packs in ignored local storage."""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from functools import partial
from urllib.parse import urlsplit
from quality.lib.output import write_error
from concurrent.futures import ThreadPoolExecutor
from quality.security.semgrep.download import RulePin, read_rules, check_rule, download_rule
from quality.lib.json_config import (
    require_int,
    require_keys,
    require_string,
    require_mapping,
    require_sequence,
    read_json_mapping,
    require_string_list,
)


def read_packs(value: object) -> dict[str, list[RulePin]]:
    """Validate pack names, registry versions, and exact rule digests before download."""
    packs: dict[str, list[RulePin]] = {}
    for name, entries in require_mapping(value, "Semgrep packs").items():
        if re.fullmatch(r"[a-z]+(?:-[a-z]+)*", name) is None:
            message = "Semgrep pack names must use lowercase words separated by hyphens."
            raise ValueError(message)
        pins: list[RulePin] = []
        for record in require_sequence(entries, name):
            entry = require_mapping(record, name)
            require_keys(entry, required={"id", "version", "sha256"}, context=name)
            pin = RulePin(
                identifier=require_string(entry["id"], "rule identifier"),
                version=require_string(entry["version"], "rule version"),
                digest=require_string(entry["sha256"], "rule digest"),
            )
            if re.fullmatch(r"[A-Za-z0-9]+", pin.version) is None or re.fullmatch(r"[a-f0-9]{64}", pin.digest) is None:
                message = f"Invalid Semgrep rule version or digest in {name}."
                raise ValueError(message)
            pins.append(pin)
        if not pins:
            message = f"Semgrep pack {name} must contain pinned rules."
            raise ValueError(message)
        packs[name] = pins
    if not packs:
        message = "Configure the required Semgrep packs before installation."
        raise ValueError(message)
    return packs


def collect_rules(settings: dict[str, object], pins: list[RulePin]) -> dict[RulePin, dict[str, object]]:
    """Use matching pack entries and retrieve exact versions for entries that have changed."""
    registry = urlsplit(require_string(settings["registry"], "Semgrep registry"))
    if registry.scheme != "https" or not registry.hostname or registry.query or registry.fragment:
        message = "The Semgrep registry must be an HTTPS URL without a query or fragment."
        raise ValueError(message)
    timeout = require_int(settings["timeout_seconds"], "Semgrep timeout", minimum=1)
    adjustments = require_mapping(settings["adjustments"], "Semgrep rule adjustments")
    available: dict[str, dict[str, object]] = {}
    for source in require_string_list(settings["sources"], "Semgrep sources", is_nonempty=True):
        for rule in read_rules(registry.hostname, source, timeout):
            available[require_string(rule["id"], "rule identifier")] = rule
    rules: dict[RulePin, dict[str, object]] = {}
    missing: list[RulePin] = []
    for pin in pins:
        rule = available.get(pin.identifier)
        if rule is not None and check_rule(pin, rule, adjustments):
            rules[pin] = rule
        else:
            missing.append(pin)
    download = partial(
        download_rule,
        host=registry.hostname,
        prefix=registry.path,
        timeout=timeout,
        adjustments=adjustments,
    )
    workers = require_int(settings["workers"], "Semgrep download workers", minimum=1)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        rules.update(zip(missing, executor.map(download, missing), strict=True))
    return rules


def install_packs() -> None:
    """Write local rule packs only after every configured rule matches its content digest."""
    settings = read_json_mapping(Path("quality/config/security/semgrep/packs.json"))
    packs = read_packs(settings["packs"])
    pins = list(dict.fromkeys(pin for entries in packs.values() for pin in entries))
    rules = collect_rules(settings, pins)
    directory = Path(require_string(settings["directory"], "Semgrep rule directory"))
    directory.mkdir(parents=True, exist_ok=True)
    for name, entries in packs.items():
        content = json.dumps({"rules": [rules[pin] for pin in entries]}, sort_keys=True, separators=(",", ":"))
        (directory / f"{name}.json").write_text(content + "\n", encoding="utf-8")
    (directory / "LICENSE.md").write_text(
        "These downloaded rules retain their upstream license metadata.\n"
        "Rule IDs use their full registry names. The Slack webhook rule excludes the literal example token by regex.\n"
        "See https://semgrep.dev/legal/rules-license. Do not redistribute these local packs.\n",
        encoding="utf-8",
    )
    sys.stdout.write(f"Installed {len(packs)} Semgrep packs with {len(pins)} pinned rule versions.\n")


def main() -> int:
    """Report installation failures without leaving unverified rule packs."""
    try:
        install_packs()
    except (OSError, ValueError, RuntimeError) as error:
        write_error(f"Semgrep rule installation failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
