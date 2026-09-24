import fs from 'node:fs';
import path from 'node:path';
import { CODEQL_SCAN_FILE } from '#config/security/codeql/paths.js';

const repoRoot = process.cwd();
const errors = [];

const scanPolicyPath = path.join(repoRoot, CODEQL_SCAN_FILE);
// eslint-disable-next-line security/detect-non-literal-fs-filename -- CODEQL_SCAN_FILE selects the repository-owned scanner configuration.
const lines = fs.readFileSync(scanPolicyPath, 'utf8').split('\n');
let inPathsSection = false;

for (const rawLine of lines) {
  const line = rawLine.trim();
  if (line.startsWith('paths-ignore:')) {
    break;
  }
  if (line.startsWith('paths:')) {
    inPathsSection = true;
    continue;
  }
  if (!inPathsSection || !line.startsWith('- ')) {
    continue;
  }

  const scanPath = line
    .slice(2)
    .trim()
    .replaceAll(/^['"]|['"]$/gu, '');
  const absolutePath = path.join(repoRoot, scanPath);
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Only check whether a path declared in the scanner configuration exists.
  if (!fs.existsSync(absolutePath)) {
    errors.push(`${CODEQL_SCAN_FILE}: paths entry "${scanPath}" does not exist in the repository`);
  }
}

if (errors.length > 0) {
  console.error('CodeQL scan path policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('CodeQL scan path policy passed.');
