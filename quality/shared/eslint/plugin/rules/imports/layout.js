import { isImportLike } from '#shared/eslint/plugin/imports.js';

const blankLinePattern = /\n\s*\n/u;
const whitespaceOnlyPattern = /^\s*$/u;

/**
 * Returns the source offset where the import's leading attached comments begin.
 * @param sourceCode - ESLint source text, comments, and token locations.
 * @param node - Syntax-tree node to inspect.
 * @returns Offset of the earliest attached leading comment, or the node start.
 */
const getLeadingSegmentStart = (sourceCode, node) => {
  const fullText = sourceCode.getText();
  const commentsBefore = sourceCode.getCommentsBefore(node);
  let start = node.range[0];

  for (let index = commentsBefore.length - 1; index >= 0; index -= 1) {
    const comment = commentsBefore.at(index);
    if (comment.type === 'Shebang') break;
    const betweenCommentNode = fullText.slice(comment.range[1], start);
    if (!whitespaceOnlyPattern.test(betweenCommentNode)) {
      break;
    }

    const previousLineBreak = fullText.lastIndexOf('\n', comment.range[0] - 1);
    const linePrefix = fullText.slice(previousLineBreak + 1, comment.range[0]);
    if (!whitespaceOnlyPattern.test(linePrefix)) {
      break;
    }

    start = comment.range[0];
  }

  return start;
};

/**
 * Returns the source offset after the node including any same-line trailing comments.
 * @param sourceCode - ESLint source text, comments, and token locations.
 * @param node - Syntax-tree node to inspect.
 * @returns Offset after the node and its same-line trailing comments.
 */
const getImportEndComments = (sourceCode, node) => {
  const fullText = sourceCode.getText();
  let end = node.range[1];

  for (const comment of sourceCode.getCommentsAfter(node)) {
    const between = fullText.slice(end, comment.range[0]);
    if (!whitespaceOnlyPattern.test(between) || comment.loc.start.line !== node.loc.end.line) {
      break;
    }
    end = comment.range[1];
  }

  return end;
};

/** Collapses whitespace for stable import statement sort comparison. */
const importSortWhitespacePattern = /\s+/gu;

/**
 * Builds entry objects for each import in a contiguous import-like block.
 * @param importNodes - Consecutive import statements in source order.
 * @param segmentStarts - Source offsets of each import and its attached comments.
 * @param blockEnd - Source offset after the last import and its trailing comments.
 * @param sourceCode - ESLint source text, comments, and token locations.
 * @returns Import records with text, ranges, and sort keys.
 */
const buildEntries = (importNodes, segmentStarts, blockEnd, sourceCode) => {
  const entries = [];
  for (const [index, importNode] of importNodes.entries()) {
    const start = segmentStarts.at(index);
    const end = index < importNodes.length - 1 ? segmentStarts.at(index + 1) : blockEnd;
    const text = sourceCode.getText().slice(start, end).trim();
    const importText = sourceCode.getText(importNode);
    const sortText = importText.replaceAll(importSortWhitespacePattern, ' ').trim();

    entries.push({
      importNode,
      start,
      end,
      text,
      importText,
      sortText,
      sortLength: sortText.length,
      lineSpan: importNode.loc.end.line - importNode.loc.start.line + 1,
      isMultiLine: importText.includes('\n'),
      originalIndex: index,
    });
  }
  return entries;
};

/**
 * Compare two values of the same type in ascending order.
 * @param leftValue - First value to compare.
 * @param rightValue - Second value to compare.
 * @returns A negative, zero, or positive ordering result.
 */
const compareTextValues = (leftValue, rightValue) => {
  if (leftValue === rightValue) {
    return 0;
  }
  return leftValue < rightValue ? -1 : 1;
};

/**
 * Compares one-line entries by normalized length, then normalized statement text.
 * @param leftEntry - First import entry to compare.
 * @param rightEntry - Second import entry to compare.
 * @returns Ordering by normalized length, text, then original position.
 */
const compareSingleLineEntries = (leftEntry, rightEntry) => {
  const lengthComparison = compareTextValues(leftEntry.sortLength, rightEntry.sortLength);
  if (lengthComparison !== 0) {
    return lengthComparison;
  }

  const textComparison = compareTextValues(leftEntry.sortText, rightEntry.sortText);
  if (textComparison !== 0) {
    return textComparison;
  }

  return leftEntry.originalIndex - rightEntry.originalIndex;
};

/**
 * Compares multi-line entries by line span, normalized length, then normalized statement text.
 * @param leftEntry - First import entry to compare.
 * @param rightEntry - Second import entry to compare.
 * @returns Ordering by line count, then the single-line sort keys.
 */
const compareMultiLineEntries = (leftEntry, rightEntry) => {
  const lineSpanComparison = compareTextValues(leftEntry.lineSpan, rightEntry.lineSpan);
  if (lineSpanComparison !== 0) {
    return lineSpanComparison;
  }

  return compareSingleLineEntries(leftEntry, rightEntry);
};

/**
 * Returns entries in the expected import layout order.
 * @param entries - Import entries in their current source order.
 * @returns Single-line imports followed by multiline imports, each sorted.
 */
const computeExpectedEntries = (entries) => {
  const singleLineEntries = [];
  const multiLineEntries = [];
  for (const entry of entries) {
    if (entry.isMultiLine) multiLineEntries.push(entry);
    else singleLineEntries.push(entry);
  }
  return [
    ...singleLineEntries.sort(compareSingleLineEntries),
    ...multiLineEntries.sort(compareMultiLineEntries),
  ];
};

/**
 * Builds replacement text with one blank line between one-line and multi-line sections.
 * @param expectedEntries - Import entries in the required order.
 * @returns Sorted import text with one blank line between sections.
 */
const buildReplacementText = (expectedEntries) => {
  let replacementText = '';
  for (const [index, entry] of expectedEntries.entries()) {
    if (index === 0) {
      replacementText = entry.text;
      continue;
    }

    const previousEntry = expectedEntries.at(index - 1);
    const separator = !previousEntry.isMultiLine && entry.isMultiLine ? '\n\n' : '\n';
    replacementText = `${replacementText}${separator}${entry.text}`;
  }
  return replacementText;
};

/**
 * Returns consecutive import-like statement runs from the program body.
 * @param programBody - Top-level statements in source order.
 * @param supportRequire - Whether CommonJS require calls count as imports.
 * @returns Separate groups of consecutive import statements.
 */
const collectImportRuns = (programBody, supportRequire) => {
  const runs = [];
  let currentRun = [];

  for (const statement of programBody) {
    if (isImportLike(supportRequire, statement)) {
      currentRun.push(statement);
      continue;
    }
    if (currentRun.length > 0) {
      runs.push(currentRun);
      currentRun = [];
    }
  }
  if (currentRun.length > 0) {
    runs.push(currentRun);
  }

  return runs;
};

export const importLayout = {
  meta: {
    type: 'layout',
    docs: {
      description: 'Sort and group import/require statements by statement shape and length.',
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          supportRequire: { type: 'boolean' },
        },
        additionalProperties: false,
      },
    ],
    messages: {
      importLayout:
        'Import layout must place one-line imports first, multi-line imports second, and sort each section by length.',
    },
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const supportRequire = context.options?.[0]?.supportRequire === true;

    return {
      Program(node) {
        for (const importNodes of collectImportRuns(node.body, supportRequire)) {
          if (importNodes.length < 2) {
            continue;
          }

          const segmentStarts = importNodes.map(getLeadingSegmentStart.bind(null, sourceCode));
          const blockEnd = getImportEndComments(sourceCode, importNodes.at(-1));
          const entries = buildEntries(importNodes, segmentStarts, blockEnd, sourceCode);
          const expectedEntries = computeExpectedEntries(entries);
          const replacementText = buildReplacementText(expectedEntries);
          const currentText = sourceCode
            .getText()
            .slice(entries[0].start, entries.at(-1).end)
            .trim();
          const hasBlankLineMismatch =
            blankLinePattern.test(currentText) !== blankLinePattern.test(replacementText);

          if (currentText === replacementText && !hasBlankLineMismatch) {
            continue;
          }

          const firstMisorderedEntry = findMisorderedEntry(entries, expectedEntries);

          context.report({
            node: firstMisorderedEntry.importNode,
            messageId: 'importLayout',
            fix: replaceImports.bind(null, entries, replacementText),
          });
        }
      },
    };
  },
};

function replaceImports(entries, replacementText, fixer) {
  const firstOffset = entries[0].start;
  const lastOffset = entries.at(-1).end;
  return fixer.replaceTextRange([firstOffset, lastOffset], replacementText);
}

function findMisorderedEntry(entries, expectedEntries) {
  for (const [index, entry] of entries.entries()) {
    if (entry.importNode !== expectedEntries.at(index).importNode) return entry;
  }
  return entries[0];
}
