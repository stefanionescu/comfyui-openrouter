export const VALID_SCOPES = ['all', 'frontend', 'hooks', 'quality', 'mise'];
export const VALID_SCOPE_USAGE = VALID_SCOPES.join('|');

export const SCOPE_PREFIXES = {
  all: [''],
  frontend: ['web/scripts/', 'web/styles/', 'resources/'],
  hooks: ['.githooks/'],
  quality: ['quality/'],
  mise: ['.mise/'],
};
