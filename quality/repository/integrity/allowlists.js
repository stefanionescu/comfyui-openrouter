import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import {
  PREFIX_COLLISION_ALLOWLIST,
  SINGLE_FILE_FOLDER_PATTERNS,
} from '#config/repository/directories.js';

const repoRoot = process.cwd();

/**
 * Check that each configured folder exception still has an existing owner.
 * @returns Diagnostics for exception paths that no longer exist.
 */
function validateFolderPolicy() {
  const errors = [];
  const singleFileFolders = SINGLE_FILE_FOLDER_PATTERNS.map((pattern) =>
    path.posix.dirname(pattern),
  );
  for (const [name, entries] of [
    ['single-file folder allowlist', singleFileFolders],
    ['prefix-collision allowlist', PREFIX_COLLISION_ALLOWLIST],
  ]) {
    for (const relativePath of entries) {
      const absolutePath = path.join(repoRoot, relativePath);
      // eslint-disable-next-line security/detect-non-literal-fs-filename -- This checks paths declared in the repository folder policy; it reads no file content.
      if (!fs.existsSync(absolutePath)) {
        errors.push(
          `stale ${name} entry in quality/config/repository/directories.js: "${relativePath}" does not exist`,
        );
      }
    }
  }

  return errors;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  const errors = validateFolderPolicy();
  if (errors.length > 0) {
    console.error('folder policy integrity failed:');
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log('folder policy integrity passed.');
}

export { validateFolderPolicy };
