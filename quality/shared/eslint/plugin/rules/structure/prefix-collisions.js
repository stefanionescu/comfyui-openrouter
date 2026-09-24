import path from 'node:path';
import { PREFIXED_FILES_SCOPE } from '#config/imports/aliases.js';
import { PREFIXED_FILES_THRESHOLD } from '#config/eslint/limits.js';
import { DIRECTORY_IGNORE_PATHS } from '#config/repository/directories.js';
import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { analyzeDirectory, getPrefix } from '#repository/integrity/directory-prefixes.js';

import {
  isInScope,
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

export const noPrefixCollisions = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow repeated filename or directory-name prefixes in the same folder; group them in a subfolder instead.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          threshold: { type: 'number', minimum: 2 },
          scope: { type: 'array', items: { type: 'string' } },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const filename = context.filename ?? '';
    const normalized = normalizePath(normalizeFilename(filename));
    if (!normalized || normalized === '<input>') {
      return {};
    }

    const options = context.options?.[0] ?? {};
    const scope =
      Array.isArray(options.scope) && options.scope.length > 0
        ? options.scope
        : PREFIXED_FILES_SCOPE;
    const threshold =
      typeof options.threshold === 'number' && options.threshold >= PREFIXED_FILES_THRESHOLD
        ? options.threshold
        : PREFIXED_FILES_THRESHOLD;

    if (!isInScope(normalized, scope)) {
      return {};
    }

    const fileName = path.posix.basename(normalized);
    if (isIndexFile(fileName)) {
      return {};
    }

    const fileStem = fileName.replace(/\.[^.]+$/, '');
    const prefix = getPrefix(fileStem);
    if (!prefix) {
      return {};
    }

    const dirPath = path.dirname(normalized);

    return {
      Program(node) {
        const { prefixMap } = analyzeDirectory(dirPath, {
          ignorePaths: DIRECTORY_IGNORE_PATHS,
          skipIndexFiles: true,
        });
        const peers = prefixMap.get(prefix) ?? [];
        if (peers.length >= threshold) {
          context.report({ node, message: collisionMessage(prefix, peers) });
        }
      },
    };
  },
};

function collisionMessage(prefix, peers) {
  const types = new Set();
  const names = [];
  for (const peer of peers) {
    types.add(peer.type);
    names.push(peer.type === 'dir' ? `${peer.name}/` : peer.name);
  }
  if (types.has('file') && types.has('dir')) {
    return `Entries in this folder share the "${prefix}" stem/prefix (${names.join(', ')}). Resolve the collision by renaming or reorganizing.`;
  }
  if (types.has('dir')) {
    return `Directories in this folder share the "${prefix}" prefix (${names.join(', ')}). Resolve the collision by renaming or reorganizing.`;
  }
  return `Files in this folder share the "${prefix}" prefix (${peers.length} files). Group them in a subfolder and rename to remove the prefix.`;
}
