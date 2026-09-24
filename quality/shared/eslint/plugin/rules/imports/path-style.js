import { INTERNAL_PREFIXES } from '#config/imports/aliases.js';

const styleMessages = new Map([
  ['js', 'Internal imports must use explicit JavaScript file extensions.'],
  ['ts', 'Internal imports must use explicit .ts extensions.'],
  ['extensionless', 'Internal imports must be extensionless (no .js/.ts suffix).'],
]);
const javascriptExtensions = ['.js', '.mjs', '.cjs'];
const typescriptExtensions = ['.ts', '.mts', '.cts'];
const skippedExtensions = ['.json'];

/**
 * Returns the file extension from an import source, if the source includes one.
 * @param source - Module path written in the import.
 * @returns The final filename suffix, or an empty string when absent.
 */
function getSourceExtension(source) {
  const fileName = source.split('/').pop() ?? '';
  const index = fileName.lastIndexOf('.');
  return index > 0 ? fileName.slice(index) : '';
}

/**
 * Returns true if the import source starts with any of the known internal prefixes.
 * @param source - Module path written in the import.
 * @param internalPrefixes - Prefixes that identify imports owned by the repository.
 * @returns Whether the module path has a configured internal prefix.
 */
function isInternalImport(source, internalPrefixes) {
  for (const prefix of internalPrefixes) {
    if (source.startsWith(prefix)) {
      return true;
    }
  }
  return false;
}

/**
 * Returns true if the import source's file extension matches the required style (js, ts, or extensionless).
 * @param source - Module path written in the import.
 * @param style - Required import extension style.
 * @returns Whether the module path follows the selected extension rule.
 */
function isCompliant(source, style) {
  const extension = getSourceExtension(source);
  const hasKnownScriptExtension =
    javascriptExtensions.includes(extension) || typescriptExtensions.includes(extension);

  if (skippedExtensions.includes(extension) || (extension && !hasKnownScriptExtension)) {
    return true;
  }

  if (style === 'js') {
    return javascriptExtensions.includes(extension);
  }

  if (style === 'ts') {
    return typescriptExtensions.includes(extension);
  }

  return !hasKnownScriptExtension;
}

/**
 * Returns the preferred source value for fixable extension-style violations.
 * @param source - Module path written in the import.
 * @param style - Required import extension style.
 * @returns Module path with the required extension added, replaced, or removed.
 */
function getPreferredSource(source, style) {
  const extension = getSourceExtension(source);

  if (style === 'extensionless') {
    return extension ? source.slice(0, -extension.length) : source;
  }

  if (extension) {
    return source.slice(0, -extension.length) + `.${style}`;
  }

  return `${source}.${style}`;
}

/**
 * Returns the quote character used by the import source node.
 * @param sourceNode - String-literal node containing the module path.
 * @returns The original quote character, defaulting to a single quote.
 */
function getQuote(sourceNode) {
  const raw = typeof sourceNode.raw === 'string' ? sourceNode.raw : '';
  if (raw.startsWith('"')) {
    return '"';
  }
  return "'";
}

export const importPathStyle = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce internal import suffix style by runtime boundary.',
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          style: {
            enum: ['js', 'ts', 'extensionless'],
          },
          internalPrefixes: {
            type: 'array',
            items: { type: 'string' },
          },
          externalSources: {
            type: 'array',
            items: { type: 'string' },
            uniqueItems: true,
          },
        },
        required: ['style'],
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const options = context.options?.[0] ?? {};
    const style = options.style;
    const internalPrefixes =
      Array.isArray(options.internalPrefixes) && options.internalPrefixes.length > 0
        ? options.internalPrefixes
        : INTERNAL_PREFIXES;

    if (!styleMessages.has(style)) {
      return {};
    }

    const checkSource = (sourceNode) => {
      const source = sourceNode?.value;
      if (typeof source !== 'string') {
        return;
      }

      if (
        options.externalSources?.includes(source) ||
        !isInternalImport(source, internalPrefixes)
      ) {
        return;
      }

      if (isCompliant(source, style)) {
        return;
      }

      context.report({
        node: sourceNode,
        message: styleMessages.get(style),
        fix(fixer) {
          const preferredSource = getPreferredSource(source, style);
          const quote = getQuote(sourceNode);
          return fixer.replaceText(sourceNode, `${quote}${preferredSource}${quote}`);
        },
      });
    };

    const checkRequireCall = (node) => {
      if (node.callee?.type !== 'Identifier' || node.callee.name !== 'require') {
        return;
      }
      checkSource(node.arguments?.[0]);
    };

    const checkModuleSource = (node) => {
      if (node.source) {
        checkSource(node.source);
      }
    };

    return {
      CallExpression: checkRequireCall,
      ImportDeclaration: checkModuleSource,
      ImportExpression: checkModuleSource,
      ExportAllDeclaration: checkModuleSource,
      ExportNamedDeclaration: checkModuleSource,
    };
  },
};
