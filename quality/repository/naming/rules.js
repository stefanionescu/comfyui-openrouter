import { VALID_SCOPES } from '#config/repository/scopes.js';
import { requireDictionary, requireKeys } from '#shared/json.js';
import { buildTermEntries } from '#shared/naming/identifier-parts.js';
import vocabulary from '#config/naming/terms.json' with { type: 'json' };
import rawPolicy from '#config/naming/javascript.json' with { type: 'json' };

import {
  CASE_PATTERNS,
  NAMING_EXCEPTION_RULES,
  NAMING_POLICY_FIELDS,
  NAMING_RULE_FIELDS,
  JAVASCRIPT_NAME_CATEGORIES,
} from '#config/naming/identifiers.js';

function policyRecord(value, required, optional, context) {
  const record = requireDictionary(value, context);
  requireKeys(record, required, optional, context);
  return record;
}

function assertArray(value, key) {
  if (!Array.isArray(value)) {
    throw new Error(`${key} must be an array`);
  }

  return value;
}

function normalizeTerms(terms, key) {
  const normalized = normalizeOptionalTerms(terms, key);
  if (normalized.length === 0) {
    throw new Error(`${key} must not be empty`);
  }

  return normalized;
}

function normalizeOptionalTerms(value, key) {
  if (value === undefined) return [];
  const terms = new Set();
  for (const term of assertArray(value, key)) {
    if (typeof term !== 'string' || term.trim().length === 0) {
      throw new Error(`${key} must contain nonempty strings.`);
    }
    terms.add(term.trim());
  }
  return [...terms];
}

function normalizeNameList(names, caseInsensitive, key) {
  const normalized = new Set();
  for (const name of normalizeOptionalTerms(names, key)) {
    normalized.add(caseInsensitive ? name.toLowerCase() : name);
  }
  return normalized;
}

function normalizeRegexList(value, key) {
  const patterns = [];
  for (const pattern of normalizeOptionalTerms(value, key)) {
    // eslint-disable-next-line security/detect-non-literal-regexp -- Patterns come from the reviewed repository policy.
    patterns.push(new RegExp(pattern, 'u'));
  }
  return patterns;
}

function normalizeCases(value, context) {
  const names = value === undefined ? [] : normalizeTerms(value, context);
  for (const name of names) {
    if (!Object.hasOwn(CASE_PATTERNS, name)) throw new Error(`${context}: unknown case ${name}.`);
  }
  return names;
}

function buildNameRules(nameRules) {
  const rules = [];
  for (const [index, entry] of assertArray(nameRules, 'nameRules').entries()) {
    const rule = policyRecord(entry, ['pathRegexes'], NAMING_RULE_FIELDS, `nameRules[${index}]`);
    const pathRegexes = normalizeRegexList(rule.pathRegexes, `nameRules[${index}].pathRegexes`);
    if (pathRegexes.length === 0)
      throw new Error(`nameRules[${index}].pathRegexes must not be empty`);
    rules.push({
      pathRegexes,
      entryPathRegexes: normalizeRegexList(
        rule.entryPathRegexes,
        `nameRules[${index}].entryPathRegexes`,
      ),
      languages: normalizeOptionalTerms(rule.languages, `nameRules[${index}].languages`),
      categories: normalizeOptionalTerms(rule.categories, `nameRules[${index}].categories`),
      kinds: normalizeOptionalTerms(rule.kinds, `nameRules[${index}].kinds`),
      names: normalizeOptionalTerms(rule.names, `nameRules[${index}].names`),
      nameRegexes: normalizeRegexList(rule.nameRegexes, `nameRules[${index}].nameRegexes`),
      caseNames: normalizeCases(rule.caseNames, `nameRules[${index}].caseNames`),
      structuralPrefixRegexes: normalizeRegexList(
        rule.structuralPrefixRegexes,
        `nameRules[${index}].structuralPrefixRegexes`,
      ),
      allowedViolations: readExceptions(rule, `nameRules[${index}]`),
    });
  }
  return rules;
}

function readExceptions(rule, context) {
  const codes = normalizeOptionalTerms(rule.allowedViolations, `${context}.allowedViolations`);
  if (codes.length === 0) return codes;
  normalizeTerms(rule.names, `${context}.names`);
  if (typeof rule.reason !== 'string' || !rule.reason.trim()) {
    throw new Error(`${context}: naming exceptions require exact names and a reason.`);
  }
  for (const code of codes) {
    if (!NAMING_EXCEPTION_RULES.includes(code)) {
      throw new Error(`${context}: unknown naming exception ${code}.`);
    }
  }
  return codes;
}

function buildLocalTerms(localTerms) {
  const entries = [];
  for (const [index, value] of assertArray(localTerms, 'local.bannedTerms').entries()) {
    const entry = policyRecord(value, ['scopes', 'terms'], [], `local.bannedTerms[${index}]`);
    const scopes = normalizeTerms(entry.scopes, `local.bannedTerms[${index}].scopes`);

    for (const scope of scopes) {
      if (!VALID_SCOPES.includes(scope)) {
        throw new Error(`local.bannedTerms[${index}] has invalid scope "${scope}"`);
      }
    }

    const terms = normalizeTerms(entry.terms, `local.bannedTerms[${index}].terms`);

    entries.push({
      scopes,
      termEntries: buildTermEntries(terms),
    });
  }
  return entries;
}

function validateLanguage(value) {
  const profile = policyRecord(
    value,
    ['categories', 'maxCharacters', 'maxWords'],
    [],
    'javascript',
  );
  for (const limit of [profile.maxCharacters, profile.maxWords]) {
    if (!Number.isInteger(limit) || limit < 1) {
      throw new Error('JavaScript naming limits must be positive integers.');
    }
  }
  const categories = policyRecord(
    profile.categories,
    JAVASCRIPT_NAME_CATEGORIES,
    [],
    'javascript.categories',
  );
  for (const [category, names] of Object.entries(categories)) {
    normalizeCases(names, category);
  }
}

function reservedTerms(value) {
  const terms = [];
  for (const [index, item] of assertArray(value, 'global.reservedTerms').entries()) {
    const context = `global.reservedTerms[${index}]`;
    const entry = policyRecord(item, ['term', 'allowedKinds'], [], context);
    const [term] = normalizeTerms([entry.term], `${context}.term`);
    const allowedKinds = normalizeTerms(entry.allowedKinds, `${context}.allowedKinds`);
    terms.push({ term: term.toLowerCase(), allowedKinds });
  }
  return terms;
}

/**
 * Load and validate the repository naming policy.
 * @returns Validated rules, normalized terms, and path exclusions.
 */
function readPolicy() {
  const parsed = policyRecord(rawPolicy, NAMING_POLICY_FIELDS, [], 'naming policy');
  const global = policyRecord(
    parsed.global,
    ['bannedTermExemptions', 'reservedTerms', 'banDigits', 'banDuplicateWords'],
    [],
    'global',
  );
  const local = policyRecord(parsed.local, ['bannedTerms'], [], 'local');
  const languages = policyRecord(parsed.languages, ['javascript'], [], 'languages');
  const matching = policyRecord(parsed.matching, ['caseInsensitive'], [], 'matching');
  validateLanguage(languages.javascript);
  const caseInsensitive = matching.caseInsensitive;
  for (const flag of [caseInsensitive, global.banDigits, global.banDuplicateWords]) {
    if (typeof flag !== 'boolean') throw new Error('Naming policy flags must be booleans.');
  }
  const globalTerms = normalizeTerms(vocabulary.banned_terms, 'banned_terms');

  return {
    ...parsed,
    global: {
      ...global,
      reservedTerms: reservedTerms(global.reservedTerms),
      bannedTermExemptions: normalizeNameList(
        global.bannedTermExemptions,
        caseInsensitive,
        'global.bannedTermExemptions',
      ),
      caseInsensitive,
      termEntries: buildTermEntries(globalTerms),
    },
    pathTermEntries: buildLocalTerms(local.bannedTerms),
    nameRules: buildNameRules(parsed.nameRules),
    excludedPathParts: normalizeTerms(parsed.excludedPaths, 'excludedPaths'),
    excludedBasenames: new Set(normalizeTerms(parsed.excludedBasenames, 'excludedBasenames')),
  };
}

export { readPolicy };
