import fs from 'node:fs';
import path from 'node:path';

import {
  PACKAGE_JSON_DEFAULT_FILES,
  PACKAGE_JSON_DEPENDENCY_KEYS,
  PACKAGE_JSON_FIX_FLAG,
  PACKAGE_JSON_LINT_MESSAGES,
  PACKAGE_JSON_RANGE_PATTERN,
} from '#config/package-json/manifest.js';

const repoRoot = process.cwd();
const fix = process.argv.includes(PACKAGE_JSON_FIX_FLAG);
const files = [];
for (const argument of process.argv.slice(2)) {
  if (!argument.startsWith('--')) files.push(path.resolve(argument));
}
if (!files.length) {
  for (const relativeFile of PACKAGE_JSON_DEFAULT_FILES) {
    files.push(path.join(repoRoot, relativeFile));
  }
}

/**
 * Checks that dependency versions do not use range prefixes (^, ~, >=, etc.).
 * @param lines - Manifest text split into lines.
 * @param file - Manifest path used to locate dependency failures.
 * @returns Dependency version failures with manifest locations.
 */
const checkExactVersions = (lines, file) => {
  const errors = [];
  const sections = new Map(Object.entries(JSON.parse(lines.join('\n'))));

  for (const key of PACKAGE_JSON_DEPENDENCY_KEYS) {
    const deps = sections.get(key);
    if (!deps) continue;

    for (const [pkg, version] of Object.entries(deps)) {
      if (PACKAGE_JSON_RANGE_PATTERN.test(version)) {
        const lineNum = findDependencyLine(lines, pkg, null);
        errors.push({
          file: path.relative(repoRoot, file),
          line: lineNum + 1,
          message: `${PACKAGE_JSON_LINT_MESSAGES.rangePrefixIntro} ${key}: "${pkg}": "${version}" ${PACKAGE_JSON_LINT_MESSAGES.rangePrefixReplacement} "${version.replace(PACKAGE_JSON_RANGE_PATTERN, '')}"`,
        });
      }
    }
  }

  return errors;
};

/**
 * Strips range prefixes from dependency versions, pinning them to exact versions.
 * @param lines - Manifest text split into lines.
 * @returns The same line array with version range prefixes removed.
 */
const fixExactVersions = (lines) => {
  const sections = new Map(Object.entries(JSON.parse(lines.join('\n'))));
  const dependencies = [];
  for (const key of PACKAGE_JSON_DEPENDENCY_KEYS) {
    dependencies.push(...Object.entries(sections.get(key) ?? {}));
  }
  for (const [pkg, version] of dependencies) {
    if (!PACKAGE_JSON_RANGE_PATTERN.test(version)) continue;
    const pinned = version.replace(PACKAGE_JSON_RANGE_PATTERN, '');
    const index = findDependencyLine(lines, pkg, version);
    if (index !== -1) {
      lines.splice(index, 1, lines.at(index).replace(`"${version}"`, `"${pinned}"`));
    }
  }

  return lines;
};

function findDependencyLine(lines, packageName, version) {
  for (const [index, line] of lines.entries()) {
    if (line.includes(`"${packageName}"`) && (version === null || line.includes(`"${version}"`))) {
      return index;
    }
  }
  return -1;
}

let allErrors = [];

for (const file of files) {
  let content;
  try {
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- This local CLI reads the fixed package manifests or paths explicitly supplied by its caller.
    content = fs.readFileSync(file, 'utf8');
  } catch (error) {
    if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
      console.error(
        `${PACKAGE_JSON_LINT_MESSAGES.fileNotFoundPrefix} ${path.relative(repoRoot, file)}`,
      );
      process.exitCode = 1;
      continue;
    }
    throw error;
  }

  let lines = content.split('\n');

  if (fix) {
    lines = fixExactVersions(lines);
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Only explicit --fix mode rewrites the manifest selected by this CLI's caller.
    fs.writeFileSync(file, lines.join('\n'), 'utf8');
    console.log(`${PACKAGE_JSON_LINT_MESSAGES.fixedPrefix} ${path.relative(repoRoot, file)}`);
  } else {
    const versionErrors = checkExactVersions(lines, file);
    allErrors.push(...versionErrors);
  }
}

if (!fix) {
  if (allErrors.length) {
    console.error(PACKAGE_JSON_LINT_MESSAGES.violationsHeader);
    for (const err of allErrors) {
      console.error(`  ${err.file}:${err.line}: ${err.message}`);
    }
    console.error(`\n${allErrors.length} ${PACKAGE_JSON_LINT_MESSAGES.violationsSuffix}`);
    process.exitCode = 1;
  } else {
    console.log(PACKAGE_JSON_LINT_MESSAGES.pass);
  }
}
