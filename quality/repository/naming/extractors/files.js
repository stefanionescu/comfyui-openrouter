import path from 'node:path';

import {
  JAVASCRIPT_DIRECTORY_PREFIXES,
  SHELL_DIRECTORY_PREFIXES,
} from '#config/naming/identifiers.js';
import {
  JAVASCRIPT_EXTENSIONS,
  SHELL_EXTENSIONS,
  SHELL_SHEBANG_REGEX,
} from '#config/repository/extensions.js';

const javascriptExtensionSet = new Set(JAVASCRIPT_EXTENSIONS);
const shellExtensionSet = new Set(SHELL_EXTENSIONS);

/**
 * Identify JavaScript, TypeScript, or shell files from their suffix or shebang.
 * @param relativePath - File path relative to the repository root.
 * @param sourceText - Complete source text for the file.
 * @returns The JavaScript or shell profile, or null for other files.
 */
function languageForPath(relativePath, sourceText = '') {
  const extension = path.extname(relativePath).toLowerCase();
  const firstLine = sourceText.split(/\r?\n/u, 1)[0] ?? '';

  if (
    shellExtensionSet.has(extension) ||
    (extension === '' && SHELL_SHEBANG_REGEX.test(firstLine))
  ) {
    return 'shell';
  }
  if (javascriptExtensionSet.has(extension)) {
    return 'javascript';
  }

  return null;
}

function shellStem(stem, relativePath) {
  if (stem === '_default') {
    return path.posix.basename(path.posix.dirname(relativePath.replaceAll('\\', '/')));
  }

  return stem;
}

/**
 * Build naming records for source filenames.
 * @param relativePath - File path relative to the repository root.
 * @param sourceText - Complete source text for the file.
 * @returns Filename records, or an empty array for other languages.
 */
function collectFileNames(relativePath, sourceText = '') {
  const language = languageForPath(relativePath, sourceText);
  if (!language) {
    return [];
  }

  const extension = path.extname(relativePath);
  const stem = path.basename(relativePath, relativePath.endsWith('.d.ts') ? '.d.ts' : extension);

  if (language === 'shell') {
    return [
      {
        file: relativePath,
        line: 1,
        language,
        category: 'files',
        kind: 'shell file stem',
        name: shellStem(stem, relativePath),
        displayName: stem,
      },
    ];
  }

  return [
    {
      file: relativePath,
      line: 1,
      language,
      category: 'files',
      kind: `${language} file stem`,
      name: stem,
    },
  ];
}

function languageForDirectoryPath(relativePath) {
  const normalized = relativePath.replaceAll('\\', '/');

  for (const prefix of JAVASCRIPT_DIRECTORY_PREFIXES) {
    if (normalized.startsWith(prefix)) return 'javascript';
  }

  for (const prefix of SHELL_DIRECTORY_PREFIXES) {
    if (normalized.startsWith(prefix)) return 'shell';
  }

  return null;
}

/**
 * Build naming records for each visible directory in a source path.
 * @param relativePath - File path relative to the repository root.
 * @returns Directory records with their source paths.
 */
function collectDirectoryNames(relativePath) {
  const normalized = relativePath.replaceAll('\\', '/');
  const language = languageForDirectoryPath(normalized);
  const entries = [];

  if (!language) {
    return entries;
  }

  const directories = normalized.split('/').slice(0, -1);
  for (const [index, name] of directories.entries()) {
    if (!name || name.startsWith('.')) {
      continue;
    }

    entries.push({
      file: normalized,
      line: 1,
      language,
      category: 'directories',
      kind: `${language} directory`,
      name,
      path: directories.slice(0, index + 1).join('/'),
    });
  }

  return entries;
}

export { collectDirectoryNames, collectFileNames, languageForPath };
