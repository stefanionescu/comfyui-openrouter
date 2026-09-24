const wordPattern = /[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|[0-9]+/g;

/**
 * Split an identifier at word, digit, and punctuation boundaries.
 * @param value - Identifier to split into words and numeric parts.
 * @returns Lowercase word and numeric parts in source order.
 */
function splitIdentifierParts(value) {
  const parts = [];
  for (const segment of String(value).split(/[^A-Za-z0-9]+/u)) {
    for (const part of segment.match(wordPattern) ?? []) {
      parts.push(part.toLowerCase());
    }
  }
  return parts;
}

/**
 * Find the first repeated word in an identifier.
 * @param parts - Lowercase identifier parts in their original order.
 * @returns First repeated part, or null when all parts are distinct.
 */
function firstDuplicatePart(parts) {
  const seen = new Set();

  for (const part of parts) {
    if (seen.has(part)) {
      return part;
    }
    seen.add(part);
  }

  return null;
}

/**
 * Normalize banned terms and split each into words.
 * @param terms - Banned terms from the naming policy.
 * @returns Nonempty normalized terms and their word sequences.
 */
function buildTermEntries(terms) {
  const entries = [];
  for (const value of terms) {
    const term = String(value).trim().toLowerCase();
    if (!term) {
      continue;
    }
    const entry = {
      term,
      parts: splitIdentifierParts(term),
    };
    if (entry.parts.length > 0) {
      entries.push(entry);
    }
  }
  return entries;
}

/**
 * Find a banned word or consecutive phrase in an identifier.
 * @param parts - Lowercase identifier parts in their original order.
 * @param termEntries - Normalized banned terms and their word sequences.
 * @returns First matching banned term, or null when none matches.
 */
function findBannedTerm(parts, termEntries) {
  for (const entry of termEntries) {
    const lastStart = parts.length - entry.parts.length;
    for (let index = 0; index <= lastStart; index += 1) {
      if (matchesPhrase(parts, entry.parts, index)) return entry.term;
    }
  }

  return null;
}

function matchesPhrase(parts, phrase, start) {
  for (const [offset, part] of phrase.entries()) {
    if (parts.at(start + offset) !== part) return false;
  }
  return true;
}

export { buildTermEntries, findBannedTerm, firstDuplicatePart, splitIdentifierParts };
