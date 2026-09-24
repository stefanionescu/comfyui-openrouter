import path from 'node:path';
import { getKeys } from '@typescript-eslint/visitor-keys';
import { parse } from '@typescript-eslint/typescript-estree';
import { JSX_EXTENSIONS } from '#config/repository/extensions.js';

const jsxExtensionSet = new Set(JSX_EXTENSIONS);

function lineFor(node) {
  if (!node?.loc?.start) {
    return 1;
  }
  return node.loc.start.line ?? 1;
}

function addEntry(entries, file, language, category, kind, name, node) {
  if (!name || name === '_') {
    return;
  }

  entries.push({
    file,
    line: lineFor(node),
    language,
    category,
    kind,
    name,
  });
}

function keyName(node) {
  if (node?.type === 'Identifier' || node?.type === 'PrivateIdentifier') {
    return node.name;
  }
  if (node?.type === 'Literal' && typeof node.value === 'string') {
    return node.value;
  }
  return null;
}

function addKeyEntry(entries, file, language, category, kind, node) {
  if (node?.computed) {
    return;
  }

  addEntry(entries, file, language, category, kind, keyName(node.key), node.key ?? node);
}

function collectMember(entries, file, language, node, parent) {
  if (node.type === 'Property' && parent.type !== 'ObjectExpression') return;
  if (node.kind === 'constructor') return;
  const category = node.method || node.type.includes('Method') ? 'functions' : 'properties';
  addKeyEntry(entries, file, language, category, `${language} property`, node);
  collectParams(entries, file, language, node.value ?? node);
}

function patternChildren(node) {
  switch (node.type) {
    case 'RestElement':
      return [node.argument];
    case 'TSParameterProperty':
      return [node.parameter];
    case 'AssignmentPattern':
      return [node.left];
    case 'ArrayPattern':
      return node.elements;
    case 'ObjectPattern': {
      const children = [];
      for (const field of node.properties) {
        children.push(field.type === 'RestElement' ? field.argument : field.value);
      }
      return children;
    }
    default:
      return [];
  }
}

function collectPatternNames(entries, file, language, category, kind, node) {
  if (!node) return;
  if (node.type === 'Identifier') {
    addEntry(entries, file, language, category, kind, node.name, node);
    return;
  }
  for (const child of patternChildren(node)) {
    collectPatternNames(entries, file, language, category, kind, child);
  }
}

function collectParams(entries, file, language, node) {
  for (const param of node.params ?? []) {
    collectPatternNames(entries, file, language, 'parameters', `${language} parameter`, param);
  }
}

function isTreeNode(value) {
  if (!value || typeof value !== 'object') {
    return false;
  }
  return typeof value.type === 'string';
}

function walkTree(node, visit, parent = null) {
  if (!isTreeNode(node)) {
    return;
  }

  visit(node, parent);

  for (const key of getKeys(node)) {
    // eslint-disable-next-line security/detect-object-injection -- The parser supplies both the AST record and its traversal keys; this only reads child nodes.
    const child = node[key];
    if (Array.isArray(child)) {
      for (const item of child) {
        walkTree(item, visit, node);
      }
      continue;
    }
    walkTree(child, visit, node);
  }
}

function parseSource(relativePath, sourceText) {
  const extension = path.extname(relativePath).toLowerCase();
  const options = {
    comment: false,
    jsx: jsxExtensionSet.has(extension),
    loc: true,
    range: false,
    sourceType: 'module',
    filePath: relativePath,
    tokens: false,
  };

  return parse(sourceText, options);
}

function collectBinding(entries, file, language, node) {
  const category = node.type === 'TSParameterProperty' ? 'properties' : 'variables';
  const kind = node.type === 'TSParameterProperty' ? 'parameter property' : `${language} variable`;
  const binding = node.id ?? node.param ?? node.parameter;
  collectPatternNames(entries, file, language, category, kind, binding);
}

function collectNode(entries, file, language, node, parent) {
  if (['TSParameterProperty', 'VariableDeclarator', 'CatchClause'].includes(node.type)) {
    collectBinding(entries, file, language, node);
    return;
  }
  switch (node.type) {
    case 'ClassDeclaration':
    case 'TSInterfaceDeclaration':
    case 'TSTypeAliasDeclaration':
    case 'TSEnumDeclaration':
      addEntry(
        entries,
        file,
        language,
        'classes',
        `${language} class`,
        node.id?.name,
        node.id ?? node,
      );
      break;
    case 'TSDeclareFunction':
    case 'FunctionDeclaration':
    case 'FunctionExpression':
      addEntry(
        entries,
        file,
        language,
        'functions',
        `${language} function`,
        node.id?.name,
        node.id ?? node,
      );
      collectParams(entries, file, language, node);
      break;
    case 'TSFunctionType':
    case 'TSCallSignatureDeclaration':
    case 'TSConstructSignatureDeclaration':
    case 'ArrowFunctionExpression':
      collectParams(entries, file, language, node);
      break;
    case 'TSMethodSignature':
    case 'MethodDefinition':
    case 'Property':
    case 'TSAbstractPropertyDefinition':
    case 'TSPropertySignature':
    case 'PropertyDefinition':
      collectMember(entries, file, language, node, parent);
      break;
    case 'TSTypeParameter': {
      const name = node.name?.name ?? node.name;
      addEntry(entries, file, language, 'classes', 'type parameter', name, node);
      break;
    }
    case 'TSEnumMember':
      addEntry(entries, file, language, 'properties', 'enum member', keyName(node.id), node);
      break;
    default:
      break;
  }
}

/**
 * Parse JavaScript or TypeScript and collect its declared names.
 * @param relativePath - File path relative to the repository root.
 * @param sourceText - Complete source text for the file.
 * @param language - Language profile used to classify identifiers.
 * @returns Declared-name records with their locations and categories.
 */
function collectJavaScriptNames(relativePath, sourceText, language) {
  const entries = [];
  let astRoot;

  try {
    astRoot = parseSource(relativePath, sourceText);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`failed to parse ${relativePath}: ${message}`, { cause: error });
  }

  walkTree(astRoot, collectNode.bind(null, entries, relativePath, language));
  return entries;
}

export { collectJavaScriptNames };
