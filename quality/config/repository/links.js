export const LINK_ALIASES = [['web/', 'extensions/comfyui-openrouter']];
export const LINK_TEMPLATES = [];

export const LINK_MODES = ['--local', '--external'];
export const LINK_USAGE = 'Usage: bun quality/repository/links.mjs [--local|--external]';
export const LINK_OPTIONS = {
  markdown: true,
  recurse: false,
  checkCss: true,
  checkFragments: true,
  timeout: 15000,
  concurrency: 10,
  redirects: 'allow',
  requireHttps: 'error',
};

export const LINK_EXCLUDED_PREFIXES = ['.artifacts/'];
export const LINK_EXCLUDED_FILES = ['PLAN.md', 'plan.md', 'TODOS.md', '.mise.local.toml'];
