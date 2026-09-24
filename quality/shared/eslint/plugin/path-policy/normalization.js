import { fileURLToPath } from 'node:url';

/**
 * Normalizes a file input by stripping query/hash suffixes and resolving `file://` URLs.
 *
 * @param filename The file path to inspect.
 * @returns A normalized filesystem path.
 */
export const normalizeFilename = (filename) => {
  const cleaned = filename.replace(/[?#].*$/, '');
  if (cleaned.startsWith('file://')) {
    return fileURLToPath(cleaned);
  }
  return cleaned;
};

/**
 * Normalizes path separators to POSIX style.
 *
 * @param value The input path value.
 * @returns The normalized path string.
 */
export function normalizePath(value) {
  const pathText = value;
  if (!pathText.includes('\\')) {
    return pathText;
  }
  return pathText.replaceAll('\\', '/');
}

/**
 * Checks whether a normalized filename belongs to a configured source directory.
 * @param filename Absolute filename with forward slashes.
 * @param scope Directory segments governed by the rule.
 * @returns Whether any configured directory contains the file.
 */
export function isInScope(filename, scope) {
  for (const segment of scope) {
    if (filename.includes(`/${segment}/`)) return true;
  }
  return false;
}
