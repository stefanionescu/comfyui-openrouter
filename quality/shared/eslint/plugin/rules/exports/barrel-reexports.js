import { BARREL_REEXPORTS_MAX } from '#config/eslint/limits.js';
import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { normalizeFilename } from '#shared/eslint/plugin/path-policy/normalization.js';

export const maxBarrelReexports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Limit the number of re-exports in barrel (index) files.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          max: { type: 'integer', minimum: 1 },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const filename = context.filename ?? '';
    const normalized = normalizeFilename(filename);

    if (!normalized || normalized === '<input>' || !isIndexFile(normalized)) {
      return {};
    }

    const max = context.options[0]?.max ?? BARREL_REEXPORTS_MAX;
    const reexportNodes = [];

    return {
      ExportAllDeclaration: reexportNodes.push.bind(reexportNodes),
      ExportNamedDeclaration(node) {
        if (node.source) {
          reexportNodes.push(node);
        }
      },
      'Program:exit'() {
        if (reexportNodes.length > max) {
          for (const node of reexportNodes) {
            context.report({
              node,
              message: `Barrel file has ${reexportNodes.length} re-exports, exceeding the maximum of ${max}. Export a single map/item instead.`,
            });
          }
        }
      },
    };
  },
};
