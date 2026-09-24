"""Analyze repository names against policy."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.languages import source_language
from quality.repository.naming.parts import identifier_parts
from quality.repository.naming.validate import validate_name
from quality.config.naming.rules import DIGIT_CHECK_CATEGORIES
from quality.config.repository.paths import SHELL_TASK_PREFIXES
from quality.repository.naming.extractors.paths import extract_path_names
from quality.repository.naming.extractors.shell import extract_shell_names
from quality.repository.naming.extractors.python import extract_python_names
from quality.lib.files import read_utf8, git_files, VISIBLE_FILE_ARGUMENTS, STAGED_FILE_ARGUMENTS

if TYPE_CHECKING:
    from quality.lib.diagnostics import Diagnostic
    from quality.repository.naming.types import NameCandidate, NamingPolicy, NamingRule


def analyze_names(policy: NamingPolicy, scope: str = "all", root: str | Path = ".") -> list[Diagnostic]:
    """Return naming policy diagnostics."""
    root_path = Path(root)
    diagnostics: list[Diagnostic] = []
    paths = (
        git_files(STAGED_FILE_ARGUMENTS, root=root_path, is_existing_required=True)
        if scope == "staged"
        else git_files(VISIBLE_FILE_ARGUMENTS, root=root_path, is_existing_required=True)
    )
    for relative_path in paths:
        if is_excluded(relative_path, policy) or not in_scope(relative_path, scope):
            continue
        language = source_language(relative_path, are_task_paths_included=True)
        if language is None:
            continue
        path = root_path / relative_path
        source_text = read_utf8(path)
        candidates = extract_path_names(relative_path, language)
        if language == "python":
            candidates.extend(extract_python_names(relative_path, source_text))
        elif language == "shell":
            candidates.extend(extract_shell_names(relative_path, source_text))
        for candidate in candidates:
            diagnostics.extend(validate_candidate(candidate, policy))
    return sorted(diagnostics, key=lambda item: (item["path"], item["line"], item["message"]))


def is_excluded(relative_path: str, policy: NamingPolicy) -> bool:
    """Return whether a path is excluded by policy."""
    path_value = f"/{relative_path}"
    if Path(relative_path).name in set(policy["excluded_basenames"]):
        return True
    return any(pattern in path_value for pattern in policy["excluded_paths"])


def in_scope(relative_path: str, scope: str) -> bool:
    """Return whether a path belongs to the naming scope."""
    if scope in {"all", "", "staged"}:
        return True
    if scope == "python":
        return relative_path.endswith(".py")
    if scope == "shell":
        return relative_path.endswith(".sh") or relative_path.startswith(tuple(SHELL_TASK_PREFIXES))
    return relative_path.startswith(f"{scope.rstrip('/')}/")


def validate_candidate(candidate: NameCandidate, policy: NamingPolicy) -> list[Diagnostic]:
    """Return diagnostics for one naming candidate."""
    if is_rule_excluded(candidate, policy):
        return []
    language = candidate["language"]
    category = candidate["category"]
    name = normalized_candidate_name(candidate, policy)
    line = candidate["line"]
    path = candidate["path"]
    language_policy = policy["languages"]["python"] if language == "python" else policy["languages"]["shell"]
    cases = language_policy.get(category, [])
    messages = validate_name(name, cases, language_policy)
    if boolean_rule_matches(candidate, name, policy, "are_duplicate_words_allowed"):
        messages = [message for message in messages if message != "contains duplicate words"]
    allowed_terms: set[str] = set()
    for rule in policy["name_rules"]:
        if rule_applies(rule, candidate) and name in rule.get("names", []):
            allowed_terms.update(rule.get("allowed_banned_terms", []))
    messages.extend(banned_term_messages(name, policy, allowed_terms))
    messages.extend(digit_messages(candidate, name, policy))
    return [
        {
            "path": path,
            "line": line,
            "code": "naming.policy",
            "message": f'{language} {category.removesuffix("s")} "{name}" {message}',
        }
        for message in messages
    ]


def digit_messages(candidate: NameCandidate, name: str, policy: NamingPolicy) -> list[str]:
    """Return digit diagnostics for file and directory names."""
    messages: list[str] = []
    if (
        policy["global_policy"]["are_digits_banned"]
        and candidate["category"] in DIGIT_CHECK_CATEGORIES
        and not boolean_rule_matches(candidate, name, policy, "are_digits_allowed")
        and any(character.isdigit() for character in name)
    ):
        messages.append("contains digit")
    return messages


def boolean_rule_matches(
    candidate: NameCandidate,
    name: str,
    policy: NamingPolicy,
    flag_name: str,
) -> bool:
    """Return whether a boolean naming rule flag matches this candidate."""
    for rule in policy["name_rules"]:
        if rule.get(flag_name) is not True or not rule_applies(rule, candidate):
            continue
        names = rule.get("names", [])
        if not names or name in names or candidate["name"] in names:
            return True
    return False


def is_rule_excluded(candidate: NameCandidate, policy: NamingPolicy) -> bool:
    """Return whether a candidate is excluded by an explicit rule."""
    name = candidate["name"]
    for rule in policy["name_rules"]:
        if not rule_applies(rule, candidate):
            continue
        for prefix_pattern in rule.get("structural_prefix_regexes", []):
            name = re.sub(prefix_pattern, "", name)
        names = rule.get("names", [])
        if names and name not in names:
            continue
        if rule.get("is_excluded") is True:
            return True
    return False


def normalized_candidate_name(candidate: NameCandidate, policy: NamingPolicy) -> str:
    """Return a candidate name with configured structural prefixes removed."""
    path = candidate["path"]
    name = candidate["name"]
    language = candidate["language"]
    category = candidate["category"]
    for rule in policy["name_rules"]:
        if not rule_applies(
            rule,
            {"path": path, "language": language, "category": category},
        ):
            continue
        for prefix_pattern in rule.get("structural_prefix_regexes", []):
            name = re.sub(prefix_pattern, "", name)
    return name


def rule_applies(rule: NamingRule, candidate: NameCandidate | dict[str, str]) -> bool:
    """Return whether a naming policy rule applies to a candidate."""
    path = str(candidate["path"])
    language = str(candidate["language"])
    category = str(candidate["category"])
    return (
        all(re.search(pattern, path) for pattern in rule["path_regexes"])
        and ("languages" not in rule or language in rule["languages"])
        and ("categories" not in rule or category in rule["categories"])
    )


def banned_term_messages(name: str, policy: NamingPolicy, allowed_terms: set[str]) -> list[str]:
    """Return banned term diagnostics for a name."""
    exemptions = set(policy["global_policy"]["banned_term_exemptions"])
    if name in exemptions:
        return []
    name_words = identifier_parts(name)
    lower_name = name.lower()
    messages: list[str] = []
    for term in policy["global_policy"]["banned_terms"]:
        if term in allowed_terms:
            continue
        term_value = str(term).lower()
        term_words = identifier_parts(term_value)
        if not term_words:
            if term_value in lower_name:
                messages.append(f'contains banned term "{term}"')
            continue
        if contains_word_sequence(name_words, term_words):
            messages.append(f'contains banned term "{term}"')
    return messages


def contains_word_sequence(words: list[str], term_words: list[str]) -> bool:
    """Return whether words contain a term word sequence."""
    if not term_words:
        return False
    return any(
        words[index : index + len(term_words)] == term_words for index in range(len(words) - len(term_words) + 1)
    )
