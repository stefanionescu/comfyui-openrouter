import { CASE_PATTERNS } from '#config/naming/identifiers.js';

const patterns = new Map(Object.entries(CASE_PATTERNS));

/**
 * Compare a name with the configured case convention.
 * @param value - Identifier or file name to check.
 * @param caseName - Case convention declared by the naming policy.
 * @returns Whether the name follows that convention.
 */
function matchesCase(value, caseName) {
  const pattern = patterns.get(caseName);
  if (!pattern) {
    return false;
  }
  return pattern.test(value);
}

export { matchesCase };
