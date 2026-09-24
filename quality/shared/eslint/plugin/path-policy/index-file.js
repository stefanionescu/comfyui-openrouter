import { normalizePath } from '#shared/eslint/plugin/path-policy/normalization.js';

/**
 * Determines whether the given path points to an `index` module.
 *
 * @param filename The file path to inspect.
 * @returns `true` when the file is an `index` entry file; otherwise, `false`.
 */
export const isIndexFile = (filename) => {
  const normalized = normalizePath(filename);
  if (
    normalized === 'index.ts' ||
    normalized === 'index.tsx' ||
    normalized === 'index.js' ||
    normalized === 'index.jsx'
  ) {
    return true;
  }
  return (
    normalized.endsWith('/index.ts') ||
    normalized.endsWith('/index.tsx') ||
    normalized.endsWith('/index.js') ||
    normalized.endsWith('/index.jsx')
  );
};
