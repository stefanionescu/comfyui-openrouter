export const PACKAGE_JSON_DEFAULT_FILES = ['package.json', 'quality/package.json'];

export const PACKAGE_JSON_DEPENDENCY_KEYS = [
  'dependencies',
  'devDependencies',
  'peerDependencies',
  'optionalDependencies',
  'overrides',
];
export const PACKAGE_JSON_RANGE_PATTERN = /^[\^~><=*]+/u;
export const PACKAGE_JSON_FIX_FLAG = '--fix';

export const PACKAGE_JSON_LINT_MESSAGES = {
  fileNotFoundPrefix: 'File not found:',
  rangePrefixIntro: 'Range prefix in',
  rangePrefixReplacement: 'use',
  fixedPrefix: 'Fixed:',
  violationsHeader: 'package.json lint violations:\n',
  violationsSuffix: 'violation(s) found. Run with --fix to auto-correct.',
  pass: 'package.json lint rules passed.',
};
