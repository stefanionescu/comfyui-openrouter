import { isImportLike } from '#shared/eslint/plugin/imports.js';

/**
 * Returns true if the statement belongs to a directive prologue such as `'use strict';`.
 * @param statement - Top-level syntax-tree statement to inspect.
 * @returns Whether the statement is a directive such as use strict.
 */
const isDirectiveStatement = (statement) => {
  if (statement.type !== 'ExpressionStatement') {
    return false;
  }
  return typeof statement.directive === 'string';
};

export const noImportsAfterStatements = {
  meta: {
    type: 'layout',
    docs: {
      description:
        'Disallow static import declarations or supported require statements after top-level statements.',
    },
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
      importAfterStatement: 'Static import declarations must appear before top-level statements.',
      importOrRequireAfterStatement:
        'Static import/require declarations must appear before top-level statements.',
    },
  },
  create(context) {
    const supportRequire = context.options?.[0]?.supportRequire === true;
    const checkProgram = (node) => {
      let hasTopLevelStatement = false;

      for (const statement of node.body) {
        if (!hasTopLevelStatement && isDirectiveStatement(statement)) {
          continue;
        }

        if (isImportLike(supportRequire, statement)) {
          reportLateImport(context, statement, hasTopLevelStatement, supportRequire);
          continue;
        }

        hasTopLevelStatement = true;
      }
    };
    return { Program: checkProgram };
  },
};

function reportLateImport(context, statement, hasTopLevelStatement, supportRequire) {
  if (!hasTopLevelStatement) return;
  context.report({
    node: statement,
    messageId: supportRequire ? 'importOrRequireAfterStatement' : 'importAfterStatement',
  });
}
