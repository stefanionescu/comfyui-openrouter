"""Load and validate the closed repository naming policy."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, cast
from quality.lib.json_config import JsonConfigError
from quality.lib.json_config import (
    require_int,
    require_bool,
    require_keys,
    require_mapping,
    require_sequence,
    read_json_mapping,
    require_string_list,
)
from quality.config.naming.schema import (
    NAMING_CASES,
    NAMING_TERMS_PATH,
    NAMING_POLICY_PATH,
    NAMING_LANGUAGE_KEYS,
    NAMING_POLICY_VERSION,
    NAMING_RULE_OPTIONAL_KEYS,
)

if TYPE_CHECKING:
    from quality.repository.naming.types import NamingPolicy


def read_policy(root: str | Path = ".") -> NamingPolicy:
    """Read a schema-validated naming policy."""
    path = Path(root) / NAMING_POLICY_PATH
    payload = read_json_mapping(path)
    require_keys(
        payload,
        required={
            "version",
            "global_policy",
            "languages",
            "name_rules",
            "excluded_paths",
            "excluded_basenames",
        },
        context=NAMING_POLICY_PATH,
    )
    if require_int(payload["version"], f"{NAMING_POLICY_PATH}.version", minimum=1) != NAMING_POLICY_VERSION:
        message = f"{NAMING_POLICY_PATH}.version must be {NAMING_POLICY_VERSION}"
        raise JsonConfigError(message)
    global_policy = require_mapping(payload["global_policy"], f"{NAMING_POLICY_PATH}.global_policy")
    validate_global_policy(global_policy)
    vocabulary = read_json_mapping(Path(root) / NAMING_TERMS_PATH)
    require_keys(vocabulary, required={"banned_terms"}, context=NAMING_TERMS_PATH)
    banned_terms = require_string_list(
        vocabulary["banned_terms"], f"{NAMING_TERMS_PATH}.banned_terms", is_nonempty=True
    )
    global_policy["banned_terms"] = banned_terms
    validate_languages(require_mapping(payload["languages"], f"{NAMING_POLICY_PATH}.languages"))
    rules_context = f"{NAMING_POLICY_PATH}.name_rules"
    rules = [
        require_mapping(item, f"{rules_context}[{index}]")
        for index, item in enumerate(require_sequence(payload["name_rules"], rules_context))
    ]
    validate_rules(rules, set(banned_terms))
    excluded_paths = require_string_list(
        payload["excluded_paths"],
        f"{NAMING_POLICY_PATH}.excluded_paths",
        is_nonempty=True,
    )
    if any(not value.startswith("/") or not value.endswith("/") for value in excluded_paths):
        message = f"{NAMING_POLICY_PATH}.excluded_paths entries must start and end with /"
        raise JsonConfigError(message)
    require_string_list(payload["excluded_basenames"], f"{NAMING_POLICY_PATH}.excluded_basenames", is_nonempty=True)
    return cast("NamingPolicy", payload)


def validate_global_policy(policy: dict[str, object]) -> None:
    """Validate repository-wide naming members."""
    context = f"{NAMING_POLICY_PATH}.global_policy"
    require_keys(policy, required={"are_digits_banned", "banned_term_exemptions"}, context=context)
    require_bool(policy["are_digits_banned"], f"{context}.are_digits_banned")
    require_string_list(policy["banned_term_exemptions"], f"{context}.banned_term_exemptions")


def validate_languages(languages: dict[str, object]) -> None:
    """Validate exact language categories, cases, and limits."""
    require_keys(languages, required=set(NAMING_LANGUAGE_KEYS), context=f"{NAMING_POLICY_PATH}.languages")
    for language, keys in NAMING_LANGUAGE_KEYS.items():
        context = f"{NAMING_POLICY_PATH}.languages.{language}"
        policy = require_mapping(languages[language], context)
        require_keys(policy, required=keys, context=context)
        require_int(policy["max_characters"], f"{context}.max_characters", minimum=1)
        require_int(policy["max_words"], f"{context}.max_words", minimum=1)
        for category in keys - {"max_characters", "max_words"}:
            cases = require_string_list(policy[category], f"{context}.{category}", is_nonempty=True)
            unknown = sorted(set(cases) - NAMING_CASES)
            if unknown:
                message = f"{context}.{category} has unknown cases: {', '.join(unknown)}"
                raise JsonConfigError(message)


def validate_rules(rules: list[dict[str, object]], banned_terms: set[str]) -> None:
    """Validate conditional naming rules and compile their patterns."""
    for index, rule in enumerate(rules):
        context = f"{NAMING_POLICY_PATH}.name_rules[{index}]"
        require_keys(rule, required={"path_regexes"}, optional=NAMING_RULE_OPTIONAL_KEYS, context=context)
        validate_regexes(
            require_string_list(rule["path_regexes"], f"{context}.path_regexes", is_nonempty=True), context
        )
        for key in ("languages", "categories", "names"):
            if key in rule:
                require_string_list(rule[key], f"{context}.{key}", is_nonempty=True)
        if "structural_prefix_regexes" in rule:
            patterns = require_string_list(rule["structural_prefix_regexes"], f"{context}.structural_prefix_regexes")
            validate_regexes(patterns, f"{context}.structural_prefix_regexes")
        for key in ("is_excluded", "are_duplicate_words_allowed", "are_digits_allowed"):
            if key in rule:
                require_bool(rule[key], f"{context}.{key}")
        if "allowed_banned_terms" in rule:
            validate_term_exception(rule, context, banned_terms)


def validate_term_exception(rule: dict[str, object], context: str, banned_terms: set[str]) -> None:
    """Limit vocabulary exceptions to named declarations and exact banned terms."""
    names = require_string_list(rule.get("names"), f"{context}.names", is_nonempty=True)
    terms = require_string_list(rule["allowed_banned_terms"], f"{context}.allowed_banned_terms", is_nonempty=True)
    reason = rule.get("reason")
    if any(not name.strip() for name in names) or not isinstance(reason, str) or not reason.strip():
        message = f"{context} requires exact nonempty names and a reason"
        raise JsonConfigError(message)
    if set(terms) - banned_terms:
        message = f"{context}.allowed_banned_terms contains terms outside the banned vocabulary"
        raise JsonConfigError(message)


def validate_regexes(patterns: list[str], context: str) -> None:
    """Compile configured patterns so malformed regular expressions fail startup."""
    for pattern in patterns:
        try:
            re.compile(pattern)
        except re.error as exception:
            message = f"{context} contains invalid regular expression {pattern}: {exception}"
            raise JsonConfigError(message) from exception
