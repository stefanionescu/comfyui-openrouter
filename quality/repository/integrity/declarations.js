#!/usr/bin/env bun

import fs from 'node:fs';
import path from 'node:path';
import { parse } from '@typescript-eslint/typescript-estree';
import { visitorKeys } from '@typescript-eslint/visitor-keys';
import { JAVASCRIPT_EXTENSIONS } from '#config/repository/extensions.js';
import { DISALLOWED_RUNTIME_FOLDERS } from '#config/repository/directories.js';

import {
  CONFIG_NODE_RULES,
  CONFIG_IO_MODULES,
  CONFIG_COMMAND_NAMES,
  CONFIG_PROCESS_PATHS,
  SHELL_CONFIG_GUARDS,
} from '#config/repository/declarations.js';

const repoRoot = process.cwd();
const qualityRoot = path.join(repoRoot, 'quality');
const configRoots = [path.join(repoRoot, 'src', 'config'), path.join(qualityRoot, 'config')];
const javascriptExtensionSet = new Set(JAVASCRIPT_EXTENSIONS);
const shellConfigExtensions = new Set(['.sh']);
const disallowedRuntimeFolderNames = new Set(DISALLOWED_RUNTIME_FOLDERS);
const errors = [];
const traversalKeys = new Map(Object.entries(visitorKeys));

function listFiles(rootPath, results = []) {
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Scan the fixed configuration directory and directory entries beneath it; links are not traversed.
  for (const entry of fs.readdirSync(rootPath, { withFileTypes: true })) {
    // reason: Directory entries come from readdir under the fixed policy directory; symbolic links are not followed.
    // bearer:disable javascript_lang_path_traversal
    const entryPath = path.join(rootPath, entry.name);
    if (entry.isDirectory()) {
      listFiles(entryPath, results);
      continue;
    }
    if (entry.isFile()) {
      results.push(entryPath);
    }
  }

  return results;
}

function checkConfigImport(imported, relativePath) {
  if (CONFIG_IO_MODULES.includes(imported)) {
    errors.push(
      `${relativePath}: Config files must not import filesystem or process execution modules.`,
    );
  }
  if (
    ['process', 'node:process'].includes(imported) &&
    !CONFIG_PROCESS_PATHS.includes(relativePath)
  ) {
    errors.push(`${relativePath}: Config files must not read process state.`);
  }
}

function checkConfigCall(node, relativePath) {
  if (node.callee.name === 'require') {
    checkConfigImport(node.arguments[0]?.value, relativePath);
  }
  const calledName = node.callee.name ?? node.callee.property?.name;
  if (CONFIG_COMMAND_NAMES.includes(calledName)) {
    errors.push(`${relativePath}: Config files must not execute commands.`);
  }
  if (calledName === 'fileURLToPath') {
    errors.push(`${relativePath}: Config files must not derive runtime paths.`);
  }
}

function checkNodeRestrictions(node, relativePath) {
  for (const rule of CONFIG_NODE_RULES) {
    if (rule.types.includes(node.type)) {
      errors.push(`${relativePath}:${node.loc.start.line}: ${rule.message}`);
    }
  }
}

function checkConfigNode(node, relativePath) {
  checkNodeRestrictions(node, relativePath);
  switch (node.type) {
    case 'ImportDeclaration':
      checkConfigImport(node.source.value, relativePath);
      break;
    case 'CallExpression':
      checkConfigCall(node, relativePath);
      break;
    case 'MemberExpression':
      if (node.object.name === 'process' && !CONFIG_PROCESS_PATHS.includes(relativePath)) {
        errors.push(`${relativePath}: Config files must not read process state.`);
      }
      break;
    case 'MetaProperty':
      if (node.meta.name === 'import') {
        errors.push(`${relativePath}: Config files must not derive runtime paths.`);
      }
      break;
    default:
      break;
  }
}

function checkJavaScriptConfig(source, relativePath) {
  if (source.startsWith('#!')) {
    errors.push(`${relativePath}: Config files must not be executable entrypoints.`);
  }
  let parsed;
  try {
    parsed = parse(source, { loc: true, filePath: relativePath });
  } catch (error) {
    errors.push(`${relativePath}: ${error.message}`);
    return;
  }
  const pending = [parsed];
  while (pending.length > 0) {
    const node = pending.pop();
    checkConfigNode(node, relativePath);
    pending.push(...childNodes(node));
  }
}

function childNodes(node) {
  const children = [];
  for (const key of traversalKeys.get(node.type)) {
    // eslint-disable-next-line security/detect-object-injection -- The parser supplies the AST record and its traversal keys; this reads child nodes without executing source.
    const value = node[key];
    if (Array.isArray(value)) children.push(...value.filter(Boolean));
    else if (value) children.push(value);
  }
  return children;
}

function checkConfigFile(filePath) {
  const relativePath = path.relative(repoRoot, filePath).replaceAll(path.sep, '/');
  const extension = path.extname(filePath);
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- listFiles supplies regular files from the fixed configuration directory.
  const source = fs.readFileSync(filePath, 'utf8');
  if (javascriptExtensionSet.has(extension)) {
    checkJavaScriptConfig(source, relativePath);
  } else if (shellConfigExtensions.has(extension)) {
    for (const { pattern, message } of SHELL_CONFIG_GUARDS) {
      if (pattern.test(source)) {
        errors.push(`${relativePath}: ${message}`);
      }
    }
  }
}

function checkRuntimeBucketFolders(directory = qualityRoot) {
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Scan only the quality directory and its real child directories; links are not traversed.
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }

    // reason: Directory entries come from readdir under the fixed quality directory; symbolic links are not followed.
    // bearer:disable javascript_lang_path_traversal
    const entryPath = path.join(directory, entry.name);
    if (disallowedRuntimeFolderNames.has(entry.name)) {
      errors.push(
        `${path.relative(repoRoot, entryPath).replaceAll(path.sep, '/')}/: split quality code by owner or behavior, not by runtime folder`,
      );
    }
    checkRuntimeBucketFolders(entryPath);
  }
}

for (const configRoot of configRoots) {
  for (const filePath of listFiles(configRoot)) checkConfigFile(filePath);
}
checkRuntimeBucketFolders();

if (errors.length > 0) {
  console.error('quality config policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('quality config policy passed.');
