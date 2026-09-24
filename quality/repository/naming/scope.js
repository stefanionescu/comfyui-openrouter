import path from 'node:path';
import { GENERATED_SOURCE_FILES } from '#config/repository/extensions.js';
import { SCOPE_PREFIXES, VALID_SCOPES, VALID_SCOPE_USAGE } from '#config/repository/scopes.js';

const repoRoot = process.cwd();
const usage = `Usage: bun quality/repository/naming/check.js [--scope ${VALID_SCOPE_USAGE}]`;
const generatedFiles = new Set(GENERATED_SOURCE_FILES);
const scopePrefixes = new Map(Object.entries(SCOPE_PREFIXES));

function toPosix(value) {
  if (typeof value !== 'string') {
    throw new TypeError(`path must be a string, received ${typeof value}`);
  }

  return value.replaceAll('\\', '/');
}

/**
 * Split the requested scopes and reject unknown names.
 * @param scope - Comma-separated repository scopes to check.
 * @returns Validated scope names as an array.
 */
function scopeParts(scope) {
  const parts = [];
  for (const part of String(scope).split(',')) {
    const name = part.trim();
    if (!name) continue;
    if (!VALID_SCOPES.includes(name)) throw new Error(`Unknown naming scope: ${name}.`);
    parts.push(name);
  }
  if (parts.length === 0) {
    throw new Error(`invalid scope "${scope}". expected ${VALID_SCOPE_USAGE}`);
  }

  return parts;
}

/**
 * Check whether a file belongs to any requested scope.
 * @param relativePath - File path relative to the repository root.
 * @param scope - Comma-separated repository scopes to check.
 * @returns Whether at least one selected scope contains the file.
 */
function pathHasScope(relativePath, scope) {
  const parts = scopeParts(scope);
  if (parts.includes('all')) {
    return true;
  }

  const normalized = toPosix(relativePath);
  for (const part of parts) {
    for (const prefix of scopePrefixes.get(part)) {
      if (normalized.startsWith(prefix)) return true;
    }
  }
  return false;
}

function matchesPattern(patterns, value) {
  for (const pattern of patterns) {
    if (pattern.test(value)) return true;
  }
  return false;
}

function nameRuleApplies(rule, relativePath, entry) {
  if (!matchesPattern(rule.pathRegexes, relativePath)) {
    return false;
  }
  if (
    rule.entryPathRegexes.length > 0 &&
    !matchesPattern(rule.entryPathRegexes, entry.path ?? '')
  ) {
    return false;
  }
  const fields = [
    [rule.languages, entry.language],
    [rule.categories, entry.category],
    [rule.kinds, entry.kind],
    [rule.names, entry.name],
  ];
  for (const [values, value] of fields) {
    if (values.length > 0 && !values.includes(value)) return false;
  }

  return rule.nameRegexes.length === 0 || matchesPattern(rule.nameRegexes, entry.name);
}

/**
 * Select naming rules that apply to one identifier.
 * @param policy - Validated repository naming policy.
 * @param relativePath - File path relative to the repository root.
 * @param entry - Identifier record with its name, kind, language, and source location.
 * @returns Policy rules matching the identifier and its source path.
 */
function nameRulesForEntry(policy, relativePath, entry) {
  const matchingRules = [];
  for (const rule of policy.nameRules) {
    if (nameRuleApplies(rule, relativePath, entry)) {
      matchingRules.push(rule);
    }
  }
  return matchingRules;
}

/**
 * Combine global and scoped banned terms for a source file.
 * @param policy - Validated repository naming policy.
 * @param relativePath - File path relative to the repository root.
 * @returns Global and applicable scoped term records.
 */
function termEntriesForPath(policy, relativePath) {
  const entries = [...policy.global.termEntries];
  for (const scopeEntry of policy.pathTermEntries) {
    if (pathHasScope(relativePath, scopeEntry.scopes.join(','))) {
      entries.push(...scopeEntry.termEntries);
    }
  }
  return entries;
}

/**
 * Check generated-file and path exclusions before naming analysis.
 * @param relativePath - File path relative to the repository root.
 * @param policy - Validated repository naming policy.
 * @returns Whether the file is excluded from naming checks.
 */
function isPathExcluded(relativePath, policy) {
  const normalized = `/${toPosix(relativePath)}`;
  const basename = path.basename(relativePath);

  if (generatedFiles.has(toPosix(relativePath)) || policy.excludedBasenames.has(basename)) {
    return true;
  }

  for (const part of policy.excludedPathParts) {
    if (normalized.includes(part)) return true;
  }
  return false;
}

export {
  repoRoot,
  usage,
  isPathExcluded,
  nameRulesForEntry,
  pathHasScope,
  scopeParts,
  termEntriesForPath,
};
