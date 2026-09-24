export const DEFAULT_SCOPE = ['web/scripts', 'quality'];
export const PREFIXED_FILES_SCOPE = [
  'config',
  'web/scripts',
  'scripts',
  'quality',
  '.githooks',
  '.mise/tasks',
];
export const ALIAS_ROOTS = [
  { segment: 'quality/config', aliasPrefix: '#config/' },
  { segment: 'quality/web', aliasPrefix: '#web/' },
  { segment: 'quality/shared', aliasPrefix: '#shared/' },
  { segment: 'quality/repository', aliasPrefix: '#repository/' },
  { segment: 'web/scripts', aliasPrefix: '#web/' },
  { segment: 'web/styles', aliasPrefix: '#styles/' },
];
export const INTERNAL_PREFIXES = [
  './',
  '../',
  '#config/',
  '#web/',
  '#shared/',
  '#styles/',
  '#repository/',
];
