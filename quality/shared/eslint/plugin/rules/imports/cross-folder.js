import path from 'node:path';
import { ALIAS_ROOTS, DEFAULT_SCOPE } from '#config/imports/aliases.js';

import {
  isInScope,
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

/**
 * Converts an absolute target path to its project alias form if it matches a known alias root.
 * @param absoluteTargetPath - Resolved module path with forward slashes.
 * @param aliasRoots - Directory segments and their package import aliases.
 * @returns The matching package import alias, or null when no alias applies.
 */
const findAliasPath = (absoluteTargetPath, aliasRoots) => {
  for (const { segment, aliasPrefix } of aliasRoots) {
    const marker = `/${segment}/`;
    const markerIndex = absoluteTargetPath.indexOf(marker);
    if (markerIndex < 0) {
      continue;
    }
    const remainder = absoluteTargetPath.slice(markerIndex + marker.length);
    return `${aliasPrefix}${remainder}`;
  }
  return null;
};

/**
 * Returns the quote character (single or double) used by an import source node.
 * @param sourceNode - String-literal node containing the module path.
 * @returns The original quote character, defaulting to a single quote.
 */
const getQuote = (sourceNode) => {
  const raw = typeof sourceNode.raw === 'string' ? sourceNode.raw : '';
  if (raw.startsWith('"')) {
    return '"';
  }
  return "'";
};

export const noCrossFolderImports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow cross-folder relative imports. Use package imports instead.',
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          scope: {
            type: 'array',
            items: { type: 'string' },
          },
          externalSources: {
            type: 'array',
            items: { type: 'string' },
            uniqueItems: true,
          },
          aliasRoots: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                segment: { type: 'string' },
                aliasPrefix: { type: 'string' },
              },
              required: ['segment', 'aliasPrefix'],
              additionalProperties: false,
            },
          },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const normalizedFilename = normalizePath(normalizeFilename(context.filename ?? ''));
    if (!normalizedFilename || normalizedFilename === '<input>') {
      return {};
    }

    const options = context.options?.[0] ?? {};
    const scope = options.scope?.length ? options.scope : DEFAULT_SCOPE;
    const aliasRoots = options.aliasRoots?.length ? options.aliasRoots : ALIAS_ROOTS;

    if (!isInScope(normalizedFilename, scope)) {
      return {};
    }

    const importerDir = path.posix.dirname(normalizedFilename);

    const checkSource = (sourceNode) => {
      const source = sourceNode?.value;
      if (
        typeof source !== 'string' ||
        !source.startsWith('../') ||
        options.externalSources?.includes(source)
      ) {
        return;
      }

      const absoluteTargetPath = normalizePath(
        path.posix.normalize(path.posix.join(importerDir, source)),
      );
      const aliasPath = findAliasPath(absoluteTargetPath, aliasRoots);

      context.report({
        node: sourceNode,
        message: aliasPath
          ? `Cross-folder relative imports are not allowed. Use "${aliasPath}" instead.`
          : 'Cross-folder relative imports are not allowed. Use project aliases instead.',
        fix: aliasPath ? replaceSource.bind(null, sourceNode, aliasPath) : null,
      });
    };

    const checkModuleSource = (node) => {
      if (node.source) checkSource(node.source);
    };

    return {
      CallExpression(node) {
        if (node.callee?.type === 'Identifier' && node.callee.name === 'require') {
          checkSource(node.arguments?.[0]);
        }
      },
      ImportDeclaration: checkModuleSource,
      ImportExpression: checkModuleSource,
      ExportAllDeclaration: checkModuleSource,
      ExportNamedDeclaration: checkModuleSource,
    };
  },
};

function replaceSource(sourceNode, aliasPath, fixer) {
  const quote = getQuote(sourceNode);
  const replacement = `${quote}${aliasPath}${quote}`;
  return fixer.replaceText(sourceNode, replacement);
}
