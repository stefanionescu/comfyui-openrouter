export const CONFIG_NODE_RULES = [
  {
    types: [
      'FunctionDeclaration',
      'FunctionExpression',
      'ArrowFunctionExpression',
      'ClassDeclaration',
      'ClassExpression',
    ],
    message: 'Config files must not define executable logic.',
  },
  {
    types: [
      'IfStatement',
      'ForStatement',
      'ForInStatement',
      'ForOfStatement',
      'WhileStatement',
      'DoWhileStatement',
      'SwitchStatement',
      'TryStatement',
    ],
    message: 'Config files must not contain control flow.',
  },
];
export const CONFIG_IO_MODULES = [
  'fs',
  'node:fs',
  'fs/promises',
  'node:fs/promises',
  'child_process',
  'node:child_process',
];
export const CONFIG_COMMAND_NAMES = [
  'exec',
  'execFile',
  'execSync',
  'execFileSync',
  'spawn',
  'spawnSync',
];
// These tool loaders need absolute paths for the selected repository.
export const CONFIG_PROCESS_PATHS = [
  'quality/config/eslint/index.js',
  'quality/config/imports/madge.cjs',
];

export const SHELL_CONFIG_GUARDS = [
  {
    pattern: /^\s*(?:source|\.)\s+/mu,
    message: 'shell config files must not source other scripts',
  },
  {
    pattern: /^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\)\s*\{/mu,
    message: 'shell config files must not define functions',
  },
  {
    pattern: /^\s*(?:if|for|while|case)\b/mu,
    message: 'shell config files must not contain control flow',
  },
  {
    pattern: /^\s*funct\x69on\s+/mu,
    message: 'shell config files must not define functions',
  },
  { pattern: /\$\(/u, message: 'shell config files must not run command substitutions' },
];
