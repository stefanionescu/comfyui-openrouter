import eslint from '@eslint/js';
import eslintComments from '@eslint-community/eslint-plugin-eslint-comments';

export default [
  eslint.configs.recommended,
  {
    linterOptions: { reportUnusedDisableDirectives: 'error' },
    plugins: { '@eslint-community/eslint-comments': eslintComments },
    rules: {
      '@eslint-community/eslint-comments/require-description': 'error',
      'no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    },
  },
];
