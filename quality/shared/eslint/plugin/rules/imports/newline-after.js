import { isImportLike } from '#shared/eslint/plugin/imports.js';

const blankLinePattern = /\n\s*\n/u;
const whitespaceOnlyPattern = /^\s*$/u;

/**
 * Returns the source offset after the node including any same-line trailing comments.
 * @param sourceCode - ESLint source text, comments, and token locations.
 * @param node - Syntax-tree node to inspect.
 * @returns Offset after the statement and same-line trailing comments.
 */
const getStatementEndComments = (sourceCode, node) => {
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

/**
 * Returns the first non-whitespace offset in a text range.
 * @param text - Source text within the selected range.
 * @param rangeStart - Absolute source offset at the start of the range.
 * @param fallbackOffset - Offset to return when the range contains only whitespace.
 * @returns First non-whitespace offset, or the supplied fallback.
 */
const getFirstContentOffset = (text, rangeStart, fallbackOffset) => {
  const contentOffset = text.search(/\S/u);
  if (contentOffset === -1) {
    return fallbackOffset;
  }
  return rangeStart + contentOffset;
};

export const newlineAfterImports = {
  meta: {
    type: 'layout',
    docs: {
      description: 'Require a blank line after the import/require section.',
    },
    fixable: 'whitespace',
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
      newlineAfterImport: 'Import statements must be followed by a blank line.',
      newlineAfterImportOrRequire: 'Import/require statements must be followed by a blank line.',
    },
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const sourceText = sourceCode.getText();
    const supportRequire = context.options?.[0]?.supportRequire === true;

    return {
      Program(node) {
        const firstImportIndex = node.body.findIndex(isImportLike.bind(null, supportRequire));
        if (firstImportIndex === -1) {
          return;
        }

        let lastImportIndex = firstImportIndex;
        for (let index = firstImportIndex + 1; index < node.body.length; index += 1) {
          if (!isImportLike(supportRequire, node.body.at(index))) {
            break;
          }
          lastImportIndex = index;
        }

        const firstNonImportNode = node.body.at(lastImportIndex + 1);
        if (!firstNonImportNode) {
          return;
        }

        const lastImportNode = node.body.at(lastImportIndex);
        const importEnd = getStatementEndComments(sourceCode, lastImportNode);
        const boundaryText = sourceText.slice(importEnd, firstNonImportNode.range[0]);
        const leadingWhitespace = boundaryText.match(/^\s*/u)[0];

        if (blankLinePattern.test(leadingWhitespace)) {
          return;
        }

        context.report({
          node: firstNonImportNode,
          messageId: supportRequire ? 'newlineAfterImportOrRequire' : 'newlineAfterImport',
          fix(fixer) {
            const contentStart = getFirstContentOffset(
              boundaryText,
              importEnd,
              firstNonImportNode.range[0],
            );
            const range = [importEnd, contentStart];
            return fixer.replaceTextRange(range, '\n\n');
          },
        });
      },
    };
  },
};
