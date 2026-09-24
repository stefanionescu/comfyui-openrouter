export const CASE_PATTERNS = {
  camel: /^[a-z][A-Za-z]*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  kebab: /^[a-z]+(?:-[a-z]+)*$/,
  pascal: /^[A-Z][A-Za-z]*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  snake: /^[a-z]+(?:_[a-z]+)*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  'upper-snake': /^[A-Z]+(?:_[A-Z]+)*$/,
};

export const JAVASCRIPT_DIRECTORY_PREFIXES = ['web/scripts/', 'scripts/', 'quality/'];
export const SHELL_DIRECTORY_PREFIXES = ['.mise/', '.githooks/', 'quality/'];
export const NAMING_EXCEPTION_RULES = [
  'case',
  'digits',
  'length',
  'words',
  'duplicate-words',
  'banned-term',
];

export const NAMING_POLICY_FIELDS = [
  'matching',
  'global',
  'local',
  'languages',
  'nameRules',
  'excludedPaths',
  'excludedBasenames',
];
export const NAMING_RULE_FIELDS = [
  'entryPathRegexes',
  'languages',
  'categories',
  'kinds',
  'names',
  'nameRegexes',
  'caseNames',
  'structuralPrefixRegexes',
  'allowedViolations',
  'reason',
];
export const JAVASCRIPT_NAME_CATEGORIES = [
  'classes',
  'directories',
  'files',
  'functions',
  'parameters',
  'properties',
  'variables',
];
