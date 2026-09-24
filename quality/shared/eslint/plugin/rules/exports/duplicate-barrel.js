import fs from 'node:fs';
import path from 'node:path';
import { visibleFiles } from '#shared/files.js';
import { parse } from '@typescript-eslint/typescript-estree';
import { EXPORT_FILE_EXTENSIONS } from '#config/repository/extensions.js';
import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';

import {
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

const exportNameCache = new Map();
let publicModuleFiles;

/**
 * Resolves a relative import source to an absolute file path, trying direct matches and index files.
 * @param importerFile - Absolute path of the importing file.
 * @param source - Module path written in the import.
 * @returns The resolved file path, or null when the module cannot be found.
 */
const findModulePath = (importerFile, source) => {
  if (!source.startsWith('.')) {
    return null;
  }

  publicModuleFiles ??= readPublicModules();
  const importerDir = path.dirname(importerFile);
  // reason: Candidates are read only after membership in the Git-visible regular-file set is checked.
  // bearer:disable javascript_lang_path_traversal
  const sourcePath = path.resolve(importerDir, source);

  const candidates = [sourcePath];
  for (const extension of EXPORT_FILE_EXTENSIONS) {
    candidates.push(`${sourcePath}${extension}`);
  }
  for (const extension of EXPORT_FILE_EXTENSIONS) {
    // reason: Candidates are read only after membership in the Git-visible regular-file set is checked.
    // bearer:disable javascript_lang_path_traversal
    candidates.push(path.join(sourcePath, `index${extension}`));
  }
  for (const candidate of candidates) {
    if (publicModuleFiles.has(candidate)) return candidate;
  }

  return null;
};

/**
 * Recursively collects all exported names from a file, following `export *` re-exports.
 * @param filePath - Absolute path of the module whose exports are needed.
 * @param visited - Module paths already followed in this branch.
 * @returns Set of named exports, including reachable wildcard exports.
 */
const getExportForFile = (filePath, visited = new Set()) => {
  const normalizedFile = normalizePath(filePath);
  if (visited.has(normalizedFile)) {
    return new Set();
  }
  visited.add(normalizedFile);

  const cacheKey = `${normalizedFile}::${Array.from(visited).sort().join('|')}`;
  const cached = exportNameCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  // eslint-disable-next-line security/detect-non-literal-fs-filename -- The resolver selects this path from Git-visible regular files; read errors must fail the check.
  const content = fs.readFileSync(filePath, 'utf8');

  const statements = parse(content, { jsx: /\.[jt]sx$/u.test(filePath) }).body;
  const names = new Set(statements.flatMap(exportedNames));
  expandStarExports(filePath, statements, visited, names);

  exportNameCache.set(cacheKey, names);
  return names;
};

function readPublicModules() {
  const files = new Set();
  for (const file of visibleFiles(process.cwd())) {
    files.add(path.resolve(process.cwd(), file));
  }
  return files;
}

function expandStarExports(filePath, statements, visited, names) {
  for (const statement of statements) {
    if (statement.type !== 'ExportAllDeclaration') continue;
    const resolved = findModulePath(filePath, statement.source.value);
    if (!resolved) continue;
    const childNames = getExportForFile(resolved, new Set(visited));
    for (const name of childNames) {
      names.add(name);
    }
  }
}

function exportedNames(statement) {
  if (statement.type !== 'ExportNamedDeclaration') return [];
  const names = collectDeclarationNames(statement.declaration);
  for (const { exported } of statement.specifiers) {
    names.push(exported.type === 'Identifier' ? exported.name : exported.value);
  }
  return names;
}

/**
 * Records an export name, or reports a lint error if the name was already exported.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param node - Syntax-tree node to report.
 * @param name - Exported symbol name.
 */
const addNameReport = (context, seen, node, name) => {
  if (!name) {
    return;
  }
  const previous = seen.get(name);
  if (previous) {
    context.report({
      node,
      message: `Duplicate barrel export "${name}" detected. Use explicit aliases or remove conflicting re-exports.`,
    });
    return;
  }
  seen.set(name, node);
};

/**
 * Extracts declared names from an AST declaration node (function, class, variable, type, etc.).
 * @param declaration - Declaration node that may introduce exported names.
 * @returns Names introduced by the declaration, or an empty array.
 */
const collectDeclarationNames = (declaration) => {
  if (!declaration) {
    return [];
  }

  if (
    declaration.type === 'FunctionDeclaration' ||
    declaration.type === 'ClassDeclaration' ||
    declaration.type === 'TSTypeAliasDeclaration' ||
    declaration.type === 'TSInterfaceDeclaration' ||
    declaration.type === 'TSEnumDeclaration'
  ) {
    return declaration.id?.name ? [declaration.id.name] : [];
  }

  if (declaration.type !== 'VariableDeclaration') {
    return [];
  }

  const names = [];
  for (const item of declaration.declarations) {
    if (item.id.type === 'Identifier') names.push(item.id.name);
  }
  return names;
};

/**
 * Processes an ExportNamedDeclaration, tracking each exported name and reporting duplicates.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param statement - Export declaration to inspect.
 */
const processNamedDeclaration = (context, seen, statement) => {
  for (const name of collectDeclarationNames(statement.declaration)) {
    addNameReport(context, seen, statement, name);
  }

  for (const specifier of statement.specifiers) {
    if (specifier.type !== 'ExportSpecifier') {
      continue;
    }
    const exportedName =
      specifier.exported.type === 'Identifier' ? specifier.exported.name : specifier.exported.value;
    addNameReport(context, seen, statement, exportedName);
  }
};

/**
 * Processes an ExportAllDeclaration by resolving the source module and checking for duplicate names.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param statement - Export declaration to inspect.
 * @param normalized - Absolute source path with forward slashes.
 */
const processAllDeclaration = (context, seen, statement, normalized) => {
  if (!statement.source || typeof statement.source.value !== 'string') {
    return;
  }

  const resolved = findModulePath(normalized, statement.source.value);
  if (!resolved) {
    return;
  }
  const names = getExportForFile(resolved);
  for (const name of names) {
    addNameReport(context, seen, statement, name);
  }
};

export const noDuplicateBarrelExports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow duplicate exported names within barrel index files.',
    },
    schema: [],
  },
  create(context) {
    const filename = normalizeFilename(context.filename ?? '');
    if (!filename || filename === '<input>' || !isIndexFile(filename)) {
      return {};
    }

    const normalized = normalizePath(filename);

    return {
      Program(node) {
        const seen = new Map();

        for (const statement of node.body) {
          if (statement.type === 'ExportNamedDeclaration') {
            processNamedDeclaration(context, seen, statement);
          } else if (statement.type === 'ExportAllDeclaration') {
            processAllDeclaration(context, seen, statement, normalized);
          }
        }
      },
    };
  },
};
