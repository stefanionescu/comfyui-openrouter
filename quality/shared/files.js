import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

function isRegularFile(root, relative) {
  // reason: Git supplies repository-relative filenames; the following checks reject symbolic links.
  // bearer:disable javascript_lang_path_traversal
  const absolute = path.join(root, relative);
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Git supplies this repository path; existence is checked before examining its components.
  if (!fs.existsSync(absolute)) return false;
  // A file reached through a symbolic link may expose content outside the repository.
  for (let current = absolute; current !== root; current = path.dirname(current)) {
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Inspect each Git path component without following symbolic links.
    if (fs.lstatSync(current).isSymbolicLink()) {
      throw new Error(`Use a regular repository file instead of a symbolic link: ${relative}`);
    }
  }
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Every component of this Git path has been checked for symbolic links.
  return fs.statSync(absolute).isFile();
}

/**
 * List existing files that Git tracks or would include from the worktree.
 * @param root - Repository root used for the Git query and file checks.
 * @returns Sorted, unique paths relative to the repository root.
 */
export function visibleFiles(root) {
  const output = execFileSync(
    'git',
    ['-C', root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
    { encoding: 'utf8' },
  );
  const files = new Set();
  for (const relative of output.split('\0')) {
    if (relative && isRegularFile(root, relative)) files.add(relative);
  }
  return [...files].sort();
}
