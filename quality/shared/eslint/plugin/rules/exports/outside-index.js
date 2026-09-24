import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { normalizeFilename } from '#shared/eslint/plugin/path-policy/normalization.js';

export const noReexportsOutsideIndex = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow re-exports outside index barrel files.',
    },
    schema: [],
  },
  create(context) {
    const filename = context.filename ?? '';
    const normalized = normalizeFilename(filename);

    if (!normalized || normalized === '<input>' || isIndexFile(normalized)) {
      return {};
    }

    function reportReexport(node) {
      if (node.source) {
        context.report({
          node,
          message: 'Re-exports are only allowed from index barrel files.',
        });
      }
    }

    return {
      ExportAllDeclaration: reportReexport,
      ExportNamedDeclaration: reportReexport,
    };
  },
};
