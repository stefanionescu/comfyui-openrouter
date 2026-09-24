#!/usr/bin/env bun

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { check } from 'linkinator';
import { visibleFiles } from '#shared/files.js';

import {
  LINK_OPTIONS,
  LINK_MODES,
  LINK_USAGE,
  LINK_ALIASES,
  LINK_TEMPLATES,
  LINK_EXCLUDED_PREFIXES,
  LINK_EXCLUDED_FILES,
} from '#config/repository/links.js';

const root = process.cwd();
const mode = process.argv[2] ?? '--local';

function copyPublicFiles(destination) {
  const pages = [];
  for (const relative of visibleFiles(root)) {
    if (
      LINK_EXCLUDED_FILES.includes(relative) ||
      LINK_EXCLUDED_PREFIXES.some(relative.startsWith.bind(relative))
    )
      continue;
    // reason: Only Git-listed regular files are copied into this private temporary directory.
    // bearer:disable javascript_lang_path_traversal
    const target = path.join(destination, relative);
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- visibleFiles rejects symbolic links; copy only those Git-visible files into the owned temporary directory.
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(root, relative), target);
    if (/\.(?:md|html)$/u.test(relative) && !LINK_TEMPLATES.includes(relative))
      pages.push(relative);
    pages.push(...copyAliases(destination, relative, target));
  }
  return pages;
}

function copyAliases(destination, relative, target) {
  const pages = [];
  for (const [source, alias] of LINK_ALIASES) {
    if (!relative.startsWith(source)) continue;
    // reason: Configured aliases copy only Git-listed assets into the private scan directory.
    // bearer:disable javascript_lang_path_traversal
    const installed = path.join(destination, alias, relative.slice(source.length));
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Both paths belong to the temporary scan directory and the alias comes from static configuration.
    fs.mkdirSync(path.dirname(installed), { recursive: true });
    fs.copyFileSync(target, installed);
    if (/\.(?:md|html)$/u.test(relative)) pages.push(path.relative(destination, installed));
  }
  return pages;
}

async function main() {
  if (process.argv.length > 3 || !LINK_MODES.includes(mode)) {
    throw new Error(LINK_USAGE);
  }
  // Serve only Git-visible files. The repository's private configuration stays outside the scan.
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'comfyui-openrouter-links-'));
  try {
    const pages = copyPublicFiles(directory);
    const results = await check({
      ...LINK_OPTIONS,
      path: pages,
      serverRoot: directory,
      linksToSkip: async (link) => {
        const url = new URL(link);
        if (!['http:', 'https:'].includes(url.protocol)) return true;
        return mode === '--local' && url.hostname !== 'localhost';
      },
    });
    for (const link of results.links) {
      if (link.state !== 'BROKEN') continue;
      console.error(`Broken link (${link.status ?? 'unreachable'}): ${link.url}`);
      if (link.parent) console.error(`  From: ${link.parent}`);
    }
    if (!results.passed) process.exitCode = 1;
    console.log(`Checked ${pages.length} documentation files.`);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

await main();
