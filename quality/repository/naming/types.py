"""Naming-domain records."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class NameCandidate(TypedDict):
    """One extracted repository name."""

    path: str
    line: int
    language: str
    category: str
    name: str


class NamingGlobalPolicy(TypedDict):
    """Repository-wide naming checks."""

    are_digits_banned: bool
    banned_term_exemptions: list[str]
    banned_terms: list[str]


class PythonNamingPolicy(TypedDict):
    """Case and size limits for Python names."""

    max_characters: int
    max_words: int
    files: list[str]
    directories: list[str]
    modules: list[str]
    packages: list[str]
    classes: list[str]
    exceptions: list[str]
    functions: list[str]
    methods: list[str]
    parameters: list[str]
    variables: list[str]
    constants: list[str]
    attributes: list[str]
    type_aliases: list[str]


class ShellNamingPolicy(TypedDict):
    """Case and size limits for shell names."""

    max_characters: int
    max_words: int
    files: list[str]
    directories: list[str]
    functions: list[str]
    variables: list[str]


class NamingLanguages(TypedDict):
    """Naming policies for supported source languages."""

    python: PythonNamingPolicy
    shell: ShellNamingPolicy


class NamingRule(TypedDict):
    """Conditional naming exclusion or normalization rule."""

    path_regexes: list[str]
    languages: NotRequired[list[str]]
    categories: NotRequired[list[str]]
    names: NotRequired[list[str]]
    structural_prefix_regexes: NotRequired[list[str]]
    is_excluded: NotRequired[bool]
    are_duplicate_words_allowed: NotRequired[bool]
    are_digits_allowed: NotRequired[bool]
    allowed_banned_terms: NotRequired[list[str]]
    reason: NotRequired[str]


class NamingPolicy(TypedDict):
    """Validated naming policy configuration."""

    version: int
    global_policy: NamingGlobalPolicy
    languages: NamingLanguages
    name_rules: list[NamingRule]
    excluded_paths: list[str]
    excluded_basenames: list[str]
