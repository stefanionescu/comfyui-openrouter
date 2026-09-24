import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { normalizeFilename } from '#shared/eslint/plugin/path-policy/normalization.js';

const ignoredTypes = new Set(['ImportDeclaration', 'TSImportEqualsDeclaration', 'EmptyStatement']);
const declarationTypes = new Set(['ExportDefaultDeclaration']);

/**
 * Classifies a top-level statement as 'skip' (imports), 'reexport', or 'declaration'.
 * @param statement - Top-level syntax-tree statement to inspect.
 * @returns The statement category: skip, reexport, or declaration.
 */
const classifyStatement = (statement) => {
  if (ignoredTypes.has(statement.type)) {
    return 'skip';
  }

  if (declarationTypes.has(statement.type)) {
    return 'declaration';
  }

  if (statement.type === 'ExportAllDeclaration') {
    return 'reexport';
  }

  if (statement.type === 'ExportNamedDeclaration') {
    return statement.declaration ? 'declaration' : 'reexport';
  }

  return 'declaration';
};

/**
 * Analyzes a program's statements to determine if the file contains only re-exports with no real declarations.
 * @param body - Top-level statements in source order.
 * @returns Declaration flags and the first re-export node to report.
 */
const analyzeStatements = (body) => {
  let hasReexport = false;
  let hasNonExportStatement = false;
  let reportNode = null;

  for (const statement of body) {
    const kind = classifyStatement(statement);
    if (kind === 'skip') {
      continue;
    }

    if (kind === 'reexport') {
      hasReexport = true;
      reportNode ??= statement;
    } else {
      hasNonExportStatement = true;
    }
  }

  return { hasReexport, hasNonExportStatement, reportNode };
};

export const noExportOnlyFiles = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow non-index files that only re-export symbols.',
    },
    schema: [],
  },
  create(context) {
    const filename = context.filename ?? '';
    const normalized = normalizeFilename(filename);

    if (!normalized || normalized === '<input>' || isIndexFile(normalized)) {
      return {};
    }

    return {
      Program(node) {
        const { hasReexport, hasNonExportStatement, reportNode } = analyzeStatements(node.body);

        if (hasReexport && !hasNonExportStatement) {
          context.report({
            node: reportNode ?? node,
            message: 'Non-index files must include real declarations, not just re-exports.',
          });
        }
      },
    };
  },
};
