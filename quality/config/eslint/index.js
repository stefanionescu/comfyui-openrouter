import jsdoc from 'eslint-plugin-jsdoc';
import nodePlugin from 'eslint-plugin-n';
import sonarjs from 'eslint-plugin-sonarjs';
import unicorn from 'eslint-plugin-unicorn';
import security from 'eslint-plugin-security';
import tsParser from '@typescript-eslint/parser';
import sharedPolicy from '#config/eslint/base.mjs';
import prettierConfig from 'eslint-config-prettier';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import { NODE_API_VERSION } from '#config/eslint/runtime.js';
import { rules as localRules } from '#shared/eslint/plugin/index.js';
import eslintComments from '@eslint-community/eslint-plugin-eslint-comments';
import { SINGLE_FILE_FOLDER_PATTERNS } from '#config/repository/directories.js';

import {
  ESLINT_BROWSER_GLOBALS,
  ESLINT_COMMONJS_GLOBALS,
  ESLINT_NODE_GLOBALS,
} from '#config/eslint/options.js';
import {
  sourceRules,
  nodeSourceRules,
  eslintSpacingRules,
  unusedVarsRule,
} from '#config/eslint/rules.js';

const ignores = [
  '**/node_modules/**',
  '.artifacts/**',
  'dist/**',
  'web/extension.js',
  '**/.venv/**',
  '**/.git/**',
];

const nodeScriptFiles = ['scripts/**/*.mjs'];
const browserFiles = ['web/scripts/**/*.ts'];
const qualityModuleFiles = ['quality/**/*.mjs', 'quality/**/*.js'];
const qualityCommonjsFiles = ['quality/**/*.cjs'];

const plugins = {
  '@eslint-community/eslint-comments': eslintComments,
  jsdoc,
  local: { rules: localRules },
  n: nodePlugin,
  security,
  sonarjs,
  unicorn,
};

const eslintNodeSettings = {
  node: {
    version: NODE_API_VERSION,
  },
};
const boundaryOverrides = [
  {
    files: browserFiles,
    rules: {
      'no-alert': 'error',
      'no-restricted-properties': [
        'error',
        {
          property: 'getCanvasMenuOptions',
          message: 'Use the ComfyUI getCanvasMenuItems extension hook.',
        },
        {
          property: 'getExtraMenuOptions',
          message: 'Use the ComfyUI getNodeMenuItems extension hook.',
        },
      ],
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['node:*', '#shared/**', '#repository/**', '**/quality/**'],
              message: 'ComfyUI browser code must not import build or quality tools.',
            },
          ],
        },
      ],
    },
  },
];

const qualityToolingOverrides = {
  files: [...qualityModuleFiles, ...qualityCommonjsFiles],
  rules: {
    'n/no-process-exit': 'off',
  },
};

export default [
  { ignores },
  {
    settings: eslintNodeSettings,
  },
  ...sharedPolicy,
  {
    files: [...nodeScriptFiles, ...qualityModuleFiles],
    plugins,
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: ESLINT_NODE_GLOBALS,
    },
    rules: nodeSourceRules,
  },
  {
    files: browserFiles,
    plugins: { ...plugins, '@typescript-eslint': tsPlugin },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: process.cwd(),
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: ESLINT_BROWSER_GLOBALS,
    },
    rules: {
      ...sourceRules,
      ...tsPlugin.configs['eslint-recommended'].overrides[0].rules,
      ...tsPlugin.configs['strict-type-checked'].rules,
      '@typescript-eslint/no-confusing-void-expression': ['error', { ignoreArrowShorthand: true }],
      '@typescript-eslint/restrict-template-expressions': ['error', { allowNumber: true }],
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': unusedVarsRule,
      'local/import-path-style': ['error', { style: 'ts' }],
    },
  },
  {
    files: qualityCommonjsFiles,
    plugins,
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'commonjs',
      globals: ESLINT_COMMONJS_GLOBALS,
    },
    rules: nodeSourceRules,
  },
  qualityToolingOverrides,
  ...boundaryOverrides,
  {
    files: ['web/scripts/extension.ts', 'web/scripts/text.ts', 'web/scripts/http.ts'],
    rules: {
      // ComfyUI serves these modules outside the connector's bundled directory.
      'local/import-path-style': [
        'error',
        {
          style: 'ts',
          externalSources: ['../../scripts/app.js', '../../scripts/api.js'],
        },
      ],
      'local/no-cross-folder-imports': [
        'error',
        {
          externalSources: ['../../scripts/app.js', '../../scripts/api.js'],
        },
      ],
    },
  },
  ...(SINGLE_FILE_FOLDER_PATTERNS.length > 0
    ? [{ files: SINGLE_FILE_FOLDER_PATTERNS, rules: { 'local/no-single-file-folders': 'off' } }]
    : []),
  prettierConfig,
  { rules: eslintSpacingRules },
];
