"""Naming quality-policy location and closed schema members."""

NAMING_POLICY_PATH = "quality/config/naming/policy.json"
NAMING_TERMS_PATH = "quality/config/naming/terms.json"
NAMING_POLICY_VERSION = 1
NAMING_CASES = {"kebab", "pascal", "snake", "upper-snake"}
NAMING_LANGUAGE_KEYS = {
    "python": {
        "max_characters",
        "max_words",
        "files",
        "directories",
        "modules",
        "packages",
        "classes",
        "exceptions",
        "functions",
        "methods",
        "parameters",
        "variables",
        "constants",
        "attributes",
        "type_aliases",
    },
    "shell": {"max_characters", "max_words", "files", "directories", "functions", "variables"},
}
NAMING_RULE_OPTIONAL_KEYS = {
    "languages",
    "categories",
    "names",
    "structural_prefix_regexes",
    "is_excluded",
    "are_duplicate_words_allowed",
    "are_digits_allowed",
    "allowed_banned_terms",
    "reason",
}
