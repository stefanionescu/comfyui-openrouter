import { isImportLike } from '#shared/eslint/plugin/imports.js';

const directiveCommentPattern =
  /^(?:eslint(?:\s|$|-)|global\s|globals\s|exported\s|jshint\s|jslint\s|istanbul\s|c8\s|@?ts-(?:ignore|expect-error|nocheck|check)\b)/u;
const blankLinePattern = /\n\s*\n/u;
const whitespaceOnlyPattern = /^\s*$/u;

/**
 * Returns true if the comment's range falls entirely within the node's range.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the entire comment lies within the node.
 */
const isCommentInsideNode = (comment, node) => {
  const startsInside = comment.range[0] >= node.range[0];
  const endsInside = comment.range[1] <= node.range[1];
  return startsInside && endsInside;
};

/**
 * Returns true if the comment sits on the same line after the node with only whitespace between them.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the comment follows the node on the same line.
 */
const isTrailingCommentNode = (sourceText, comment, node) => {
  if (comment.loc.start.line !== node.loc.end.line) {
    return false;
  }
  if (comment.range[0] < node.range[1]) {
    return false;
  }

  return whitespaceOnlyPattern.test(sourceText.slice(node.range[1], comment.range[0]));
};

/**
 * Returns true if the comment appears directly before the node with only whitespace (and optionally one blank line) between them.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @param root0 - Comment attachment options.
 * @param root0.allowSingleBlankLine - Whether one blank line may separate a comment from the node.
 * @returns Whether the comment is attached before the node.
 */
const isLeadingCommentNode = (sourceText, comment, node, { allowSingleBlankLine = false } = {}) => {
  if (comment.range[1] > node.range[0]) {
    return false;
  }

  const between = sourceText.slice(comment.range[1], node.range[0]);
  if (!whitespaceOnlyPattern.test(between)) {
    return false;
  }

  const lineDistance = node.loc.start.line - comment.loc.end.line;
  if (allowSingleBlankLine) {
    if (lineDistance > 2) {
      return false;
    }
  } else if (lineDistance > 1) {
    return false;
  }

  if (!allowSingleBlankLine && blankLinePattern.test(between)) {
    return false;
  }

  const lineStart = sourceText.lastIndexOf('\n', comment.range[0] - 1) + 1;
  return whitespaceOnlyPattern.test(sourceText.slice(lineStart, comment.range[0]));
};

/**
 * Returns true if the comment is inside, trailing, or leading-attached to the given node.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param options - Comment attachment options.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the comment belongs to the node.
 */
const isAttachedToNode = (sourceText, comment, options, node) => {
  if (isCommentInsideNode(comment, node)) {
    return true;
  }
  if (isTrailingCommentNode(sourceText, comment, node)) {
    return true;
  }
  return isLeadingCommentNode(sourceText, comment, node, options);
};

export const headerCommentsBeforeImports = {
  meta: {
    type: 'layout',
    docs: {
      description: 'Require file-level comments/docs to appear before the import/require section.',
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
      headerFirst: 'Top-level comments/docs must be placed before import/require statements.',
    },
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const sourceText = sourceCode.getText();
    const options = context.options?.[0] ?? {};
    const supportRequire = options.supportRequire === true;

    return {
      Program(node) {
        const firstImportIndex = node.body.findIndex(isImportLike.bind(null, supportRequire));
        if (firstImportIndex === -1) {
          return;
        }

        const firstNonImportRun = node.body.findIndex(
          isAfterImportRun.bind(null, firstImportIndex, supportRequire),
        );
        if (firstNonImportRun === -1) {
          return;
        }

        const firstImportNode = node.body.at(firstImportIndex);
        const importRun = node.body.slice(firstImportIndex, firstNonImportRun);
        const firstNonImportNode = node.body.at(firstNonImportRun);
        const violatingComment = sourceCode
          .getAllComments()
          .find(isHeaderComment.bind(null, sourceText, importRun, firstNonImportNode));

        if (!violatingComment) {
          return;
        }

        context.report({
          node: violatingComment,
          fix: (fixer) => {
            const lineStart = sourceText.lastIndexOf('\n', violatingComment.range[0] - 1) + 1;
            let segmentEnd = violatingComment.range[1];
            while (segmentEnd < sourceText.length && /[\t\n\r ]/u.test(sourceText.at(segmentEnd))) {
              segmentEnd += 1;
            }
            const commentText = sourceText.slice(lineStart, violatingComment.range[1]).trimEnd();

            return [
              fixer.insertTextBeforeRange(
                [firstImportNode.range[0], firstImportNode.range[0]],
                `${commentText}\n\n`,
              ),
              fixer.removeRange([lineStart, segmentEnd]),
            ];
          },
          messageId: 'headerFirst',
        });
      },
    };
  },
};

function isAfterImportRun(firstIndex, supportRequire, statement, index) {
  if (index <= firstIndex) return false;
  return !isImportLike(supportRequire, statement);
}

function isHeaderComment(sourceText, importRun, nextNode, comment) {
  const normalizedComment = comment.value.replace(/^\s*\*?/u, '').trim();
  const isAttachedImport = isAttachedToNode.bind(null, sourceText, comment, undefined);
  return (
    comment.range[0] >= importRun[0].range[0] &&
    comment.range[1] <= nextNode.range[0] &&
    !directiveCommentPattern.test(normalizedComment) &&
    !importRun.some(isAttachedImport) &&
    !isAttachedToNode(sourceText, comment, { allowSingleBlankLine: true }, nextNode)
  );
}
