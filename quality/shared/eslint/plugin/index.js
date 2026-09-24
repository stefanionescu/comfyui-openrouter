import { importLayout } from '#shared/eslint/plugin/rules/imports/layout.js';
import { importPathStyle } from '#shared/eslint/plugin/rules/imports/path-style.js';
import { noCallThrough } from '#shared/eslint/plugin/rules/structure/call-through.js';
import { noExportOnlyFiles } from '#shared/eslint/plugin/rules/exports/only-reexports.js';
import { newlineAfterImports } from '#shared/eslint/plugin/rules/imports/newline-after.js';
import { noCrossFolderImports } from '#shared/eslint/plugin/rules/imports/cross-folder.js';
import { maxBarrelReexports } from '#shared/eslint/plugin/rules/exports/barrel-reexports.js';
import { noReexportsOutsideIndex } from '#shared/eslint/plugin/rules/exports/outside-index.js';
import { noPrefixCollisions } from '#shared/eslint/plugin/rules/structure/prefix-collisions.js';
import { noExportedAliasConstants } from '#shared/eslint/plugin/rules/exports/alias-constants.js';
import { noDuplicateBarrelExports } from '#shared/eslint/plugin/rules/exports/duplicate-barrel.js';
import { noImportsAfterStatements } from '#shared/eslint/plugin/rules/imports/after-statements.js';
import { noSingleFileFolders } from '#shared/eslint/plugin/rules/structure/single-file-folders.js';
import { headerCommentsBeforeImports } from '#shared/eslint/plugin/rules/imports/header-comments.js';

export const rules = {
  'header-comments-before-imports': headerCommentsBeforeImports,
  'import-layout': importLayout,
  'import-path-style': importPathStyle,
  'max-barrel-reexports': maxBarrelReexports,
  'newline-after-imports': newlineAfterImports,
  'no-call-through': noCallThrough,
  'no-cross-folder-imports': noCrossFolderImports,
  'no-duplicate-barrel-exports': noDuplicateBarrelExports,
  'no-export-only-files': noExportOnlyFiles,
  'no-exported-alias-constants': noExportedAliasConstants,
  'no-imports-after-statements': noImportsAfterStatements,
  'no-prefix-collisions': noPrefixCollisions,
  'no-reexports-outside-index': noReexportsOutsideIndex,
  'no-single-file-folders': noSingleFileFolders,
};
