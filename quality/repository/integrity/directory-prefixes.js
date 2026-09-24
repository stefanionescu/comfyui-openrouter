import fs from 'node:fs';

const directoryCache = new Map();

/**
 * Derive a grouping prefix from a file or directory base name.
 *
 * The prefix stops at the first `-` or `.` so related entries such as
 * `asset-card.js` and `asset.card.js` both map to `asset`.
 *
 * @param fileStem File or directory name without extension.
 * @returns Normalized prefix used for collision/grouping checks.
 */
export function getPrefix(fileStem) {
  const separator = fileStem.search(/[-.]/u);
  if (separator === -1) {
    return fileStem;
  }
  return fileStem.slice(0, separator);
}

/**
 * Analyze one directory and group files/directories by derived prefix.
 *
 * @param dirAbsPath Absolute path to the directory being analyzed.
 * @param options Analysis options.
 * @param options.ignorePaths Directory names to skip when scanning children.
 * @param options.skipIndexFiles When `true`, `index.*` files are excluded from grouping.
 * @returns Cached analysis result containing a prefix-to-entries map.
 */
export function analyzeDirectory(dirAbsPath, options = {}) {
  const { ignorePaths = [], skipIndexFiles = false } = options;
  const cacheKey = `${dirAbsPath}::${ignorePaths.join(',')}::${skipIndexFiles ? '1' : '0'}`;

  if (directoryCache.has(cacheKey)) {
    return directoryCache.get(cacheKey);
  }

  const prefixMap = new Map();
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- ESLint supplies the source file's directory; unreadable directories must fail the check.
  const entries = fs.readdirSync(dirAbsPath, { withFileTypes: true });

  for (const entry of entries) {
    const record = classifyEntry(entry, ignorePaths, skipIndexFiles);
    if (record === null) continue;
    const prefix = getPrefix(record.stem);
    if (!prefix) continue;
    const list = prefixMap.get(prefix) ?? [];
    list.push({ name: record.name, type: record.type });
    prefixMap.set(prefix, list);
  }

  const result = { prefixMap };
  directoryCache.set(cacheKey, result);
  return result;
}

function classifyEntry(entry, ignorePaths, skipIndexFiles) {
  if (entry.isDirectory()) {
    if (entry.name.startsWith('.') || ignorePaths.includes(entry.name)) return null;
    return { stem: entry.name, name: entry.name, type: 'dir' };
  }
  if (!entry.isFile()) return null;
  const stem = entry.name.replace(/\.[^.]+$/u, '');
  if (skipIndexFiles && stem === 'index') return null;
  return { stem, name: skipIndexFiles ? stem : entry.name, type: 'file' };
}
