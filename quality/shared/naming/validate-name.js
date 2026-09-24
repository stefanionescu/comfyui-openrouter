import { matchesCase } from '#shared/naming/cases.js';

import {
  findBannedTerm,
  firstDuplicatePart,
  splitIdentifierParts,
} from '#shared/naming/identifier-parts.js';

function addNameViolation(violations, entry, rule, message) {
  const location = { file: entry.file, line: entry.line };
  const violation = {
    ...location,
    name: entry.name,
    kind: entry.kind,
    rule,
    message,
  };
  violations.push(violation);
}

function hasBannedTermExemption(entry, globalRules) {
  const name = String(entry.name);
  const key = globalRules.caseInsensitive ? name.toLowerCase() : name;
  return globalRules.bannedTermExemptions?.has(key) ?? false;
}

function reservedTermAllowed(entry, globalRules, bannedTerm) {
  for (const reservedTerm of globalRules.reservedTerms ?? []) {
    if (reservedTerm.term !== bannedTerm) {
      continue;
    }

    if (reservedTerm.allowedKinds.includes(entry.kind)) {
      return true;
    }

    if (reservedTerm.allowedKinds.includes('identifier word') && entry.category !== 'prose') {
      return true;
    }
  }

  return false;
}

/**
 * Check an identifier against its case, length, word, and term rules.
 * @param entry - Identifier record with its name, kind, language, and source location.
 * @param profile - Language-specific naming limits and case rules.
 * @param termEntries - Normalized banned terms and their word sequences.
 * @param globalRules - Repository-wide naming restrictions and exact exemptions.
 * @returns Naming violations for the supplied identifier.
 */
function validateName(entry, profile, termEntries, globalRules) {
  const violations = [];
  const label = `${entry.kind} "${entry.displayName ?? entry.name}"`;
  const limitName = entry.limitName ?? entry.name;
  const partsName = entry.partsName ?? entry.name;
  const digitsName = entry.digitsName ?? entry.name;
  const caseName = entry.caseName ?? entry.name;
  const parts = splitIdentifierParts(partsName);
  const caseNames = entry.caseNames ?? profile?.categories?.[entry.category] ?? [];

  if (caseNames.length > 0 && !caseNames.some(matchesCase.bind(null, caseName))) {
    addNameViolation(violations, entry, 'case', `${label} must use ${caseNames.join(', ')} case`);
  }

  if (globalRules.banDigits && /\d/u.test(digitsName)) {
    addNameViolation(violations, entry, 'digits', `${label} must not contain digits`);
  }

  const maxCharacters = entry.maxCharacters ?? profile?.maxCharacters;
  if (Number.isInteger(maxCharacters) && limitName.length > maxCharacters) {
    addNameViolation(violations, entry, 'length', `${label} exceeds ${maxCharacters} characters`);
  }

  const maxWords = entry.maxWords ?? profile?.maxWords;
  if (Number.isInteger(maxWords) && parts.length > maxWords) {
    addNameViolation(violations, entry, 'words', `${label} exceeds ${maxWords} words`);
  }

  checkTerms(violations, entry, parts, termEntries, globalRules);

  return violations;
}

function checkTerms(violations, entry, parts, termEntries, globalRules) {
  const label = `${entry.kind} "${entry.displayName ?? entry.name}"`;
  if (globalRules.banDuplicateWords) {
    const duplicatePart = firstDuplicatePart(parts);
    if (duplicatePart) {
      addNameViolation(
        violations,
        entry,
        'duplicate-words',
        `${label} repeats word "${duplicatePart}"`,
      );
    }
  }

  if (!hasBannedTermExemption(entry, globalRules)) {
    const bannedTerm = findBannedTerm(parts, termEntries);
    if (bannedTerm && !reservedTermAllowed(entry, globalRules, bannedTerm)) {
      addNameViolation(
        violations,
        entry,
        'banned-term',
        `${label} contains banned term "${bannedTerm}"`,
      );
    }
  }
}

export { validateName };
