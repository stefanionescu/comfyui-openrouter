#!/usr/bin/env bun

import { readPolicy } from '#repository/naming/rules.js';
import { analyzeNaming } from '#repository/naming/names.js';
import { usage, scopeParts } from '#repository/naming/scope.js';

/**
 * Read and validate the requested naming scopes.
 * @param argv - Command-line arguments after the script name.
 * @returns Validated comma-separated scope names.
 */
function parseScope(argv) {
  let scope = 'all';

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv.at(index);
    if (arg === '--scope') {
      scope = argv.at(index + 1) ?? '';
      index += 1;
      continue;
    }
    if (arg.startsWith('--scope=')) {
      scope = arg.slice('--scope='.length);
      continue;
    }
    if (arg.startsWith('--')) {
      throw new Error(`unknown flag "${arg}"`);
    }
  }

  scopeParts(scope);
  return scope;
}

/**
 * Print naming failures and return a command exit code.
 * @param scope - Comma-separated repository scopes to check.
 * @param violations - Naming failures with source locations and messages.
 * @returns Zero on success, or one when naming violations exist.
 */
function reportViolations(scope, violations) {
  if (violations.length === 0) {
    console.log(`Naming lint passed (${scope}).`);
    return 0;
  }

  console.error('Naming lint violations:');
  for (const violation of violations) {
    console.error(`- ${violation.file}:${violation.line}: ${violation.message}`);
  }
  console.error(`\n${violations.length} violation(s) found.`);
  return 1;
}

try {
  const scope = parseScope(process.argv.slice(2));
  const policy = readPolicy();
  process.exitCode = reportViolations(scope, analyzeNaming(scope, policy));
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`error: ${message}`);
  console.error(usage);
  process.exitCode = 1;
}

export { parseScope, reportViolations };
