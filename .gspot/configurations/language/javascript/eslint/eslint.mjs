import { root, runtimeMatches } from "./functions.mjs";
import globals from "globals";
import { join } from "node:path";
import eslint from "@eslint/js";
import sonarjs from "eslint-plugin-sonarjs";
import unicorn from "eslint-plugin-unicorn";
import packageJson from "eslint-plugin-package-json";
import prettierConfig from "eslint-config-prettier";
import gspot from "@gspothq/eslint-plugin";
import importX from "eslint-plugin-import-x";
import jsdoc from "eslint-plugin-jsdoc";
import nodePlugin from "eslint-plugin-n";
import regexp from "eslint-plugin-regexp";
import security from "eslint-plugin-security";
import perfectionist from "eslint-plugin-perfectionist";
import boundaries from "eslint-plugin-boundaries";
import typescriptBlocks from "../../typescript/eslint.mjs";
const runtimeDeclarations = [
    {
        "scope": "",
        "runtime": "node",
        "includes": [
            "**/*"
        ],
        "excludes": []
    },
    {
        "scope": "",
        "runtime": "commonjs",
        "includes": [
            "**/*.{cjs,cts}"
        ],
        "excludes": []
    },
    {
        "scope": "",
        "runtime": "browser",
        "includes": [
            "web/scripts/**"
        ],
        "excludes": []
    }
];
export default [
    // Files that ESLint skips.
    {
        "ignores": [
            "**/build/**",
            "plans/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/*.py[cod]",
            "**/.ruff_cache/**",
            "dist/**",
            ".cache/**",
            "**/.artifacts/**",
            "**/.import_linter_cache/**",
            "**/node.zip",
            "**/.env",
            "**/.env.*",
            "**/.mise.local.toml",
            "**/*.log",
            "**/.DS_Store",
            ".gspot/**",
            ".stylelintrc.json",
            "eslint.config.mjs",
            ".markdownlint.jsonc",
            "ruff.toml",
            "pyrightconfig.json",
            ".editorconfig",
            "prettier.config.mjs",
            ".prettierignore",
            "web/extension.js",
            "web/extension.css",
            "example_workflows/*.json",
            "subgraphs/*.json",
            "**/requirements.txt",
            "**/bower_components/**",
            "**/venv/**",
            "**/.dev.vars",
            "**/.dev.vars.*",
            "**/bun.lock",
            "**/uv.lock",
            "**/.env*"
        ]
    },
    // javascript: eslint["configs"]["recommended"].rules
    {
        ...eslint["configs"]["recommended"],
        rules: {
            ...eslint["configs"]["recommended"].rules
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    // javascript: sonarjs["configs"]["recommended"].rules
    {
        ...sonarjs["configs"]["recommended"],
        rules: {
            ...sonarjs["configs"]["recommended"].rules
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    // javascript: unicorn["configs"]["recommended"].rules
    {
        ...unicorn["configs"]["recommended"],
        rules: {
            ...unicorn["configs"]["recommended"].rules
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    // javascript: gspot.configs.all.rules
    {
        plugins: {
            "gspot": gspot,
            "import-x": importX,
            "jsdoc": jsdoc,
            "n": nodePlugin,
            "regexp": regexp,
            "security": security,
            "perfectionist": perfectionist,
            "boundaries": boundaries
        },
        linterOptions: {
            reportUnusedDisableDirectives: 'error'
        },
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            globals: globals.es2024
        },
        settings: {
            gspot: {
                root
            },
            'import-x/ignore': [
                "[\\\\/]build[\\\\/]",
                "[\\\\/]plans[\\\\/]",
                "[\\\\/]\\.venv[\\\\/]",
                "[\\\\/]node_modules[\\\\/]",
                "[\\\\/]__pycache__[\\\\/]",
                "[\\\\/]\\.ruff_cache[\\\\/]",
                "[\\\\/]dist[\\\\/]",
                "[\\\\/]\\.cache[\\\\/]",
                "[\\\\/]\\.artifacts[\\\\/]",
                "[\\\\/]\\.import_linter_cache[\\\\/]",
                "[\\\\/]\\.gspot[\\\\/]",
                "[\\\\/]bower_components[\\\\/]",
                "[\\\\/]venv[\\\\/]"
            ],
            'boundaries/root-path': root
        },
        rules: {
            ...gspot.configs.all.rules,
            "no-empty-character-class": "off",
            "no-useless-constructor": "error",
            "no-useless-return": "error",
            "no-useless-call": "error",
            "no-useless-rename": "error",
            "no-duplicate-imports": "off",
            "eqeqeq": [
                "error",
                "always"
            ],
            "prefer-const": "error",
            "no-empty": [
                "error",
                {
                    "allowEmptyCatch": false
                }
            ],
            "no-param-reassign": "error",
            "perfectionist/sort-imports": [
                "error",
                {
                    "type": "line-length",
                    "order": "asc",
                    "ignoreCase": false,
                    "groups": [
                        "singleline-import",
                        "multiline-import"
                    ],
                    "fallbackSort": {
                        "type": "alphabetical",
                        "order": "asc"
                    },
                    "newlinesBetween": 1,
                    "newlinesInside": 0,
                    "sortSideEffects": false,
                    "useExperimentalDependencyDetection": false
                }
            ],
            "perfectionist/sort-named-imports": [
                "error",
                {
                    "type": "line-length",
                    "ignoreCase": false
                }
            ],
            "perfectionist/sort-exports": [
                "error",
                {
                    "type": "line-length",
                    "groups": [
                        "singleline-export",
                        "multiline-export"
                    ],
                    "newlinesBetween": 1,
                    "ignoreCase": false
                }
            ],
            "perfectionist/sort-named-exports": [
                "error",
                {
                    "type": "line-length",
                    "ignoreCase": false
                }
            ],
            "sonarjs/assertions-in-tests": "off",
            "sonarjs/async-test-assertions": "off",
            "sonarjs/slow-regex": "off",
            "sonarjs/no-unused-vars": "off",
            "sonarjs/unused-import": "off",
            "sonarjs/no-empty-character-class": "off",
            "sonarjs/no-control-regex": "off",
            "sonarjs/no-useless-catch": "off",
            "sonarjs/no-parameter-reassignment": "off",
            "sonarjs/for-loop-increment-sign": "off",
            "sonarjs/no-hardcoded-passwords": "off",
            "sonarjs/no-hardcoded-secrets": "off",
            "sonarjs/no-empty-test-file": "off",
            "sonarjs/no-collapsible-if": "error",
            "sonarjs/no-nested-switch": "error",
            "sonarjs/prefer-object-literal": "error",
            "sonarjs/no-commented-code": "error",
            "sonarjs/prefer-immediate-return": "error",
            "unicorn/no-lonely-if": "off",
            "unicorn/prevent-abbreviations": "off",
            "unicorn/filename-case": "off",
            "unicorn/no-null": "off",
            "unicorn/no-useless-undefined": "off",
            "unicorn/import-style": "off",
            "unicorn/prefer-export-from": "off",
            "unicorn/prefer-ternary": [
                "error",
                "only-single-line"
            ],
            "unicorn/expiring-todo-comments": [
                "error",
                {
                    "allowWarningComments": false
                }
            ],
            "security/detect-disable-mustache-escape": "error",
            "security/detect-eval-with-expression": "off",
            "security/detect-new-buffer": "off",
            "security/detect-non-literal-regexp": "off",
            "security/detect-non-literal-require": "error",
            "security/detect-pseudoRandomBytes": "error",
            "security/detect-unsafe-regex": "off",
            "security/detect-object-injection": "off",
            "security/detect-non-literal-fs-filename": "off",
            "security/detect-child-process": "error",
            "security/detect-possible-timing-attacks": "error",
            "jsdoc/require-param-name": "error",
            "jsdoc/check-param-names": "error",
            "jsdoc/check-tag-names": "error",
            "jsdoc/no-types": "off",
            "jsdoc/require-jsdoc": [
                "error",
                {
                    "enableFixer": false,
                    "publicOnly": true,
                    "require": {
                        "FunctionDeclaration": true,
                        "ArrowFunctionExpression": true,
                        "FunctionExpression": true,
                        "MethodDefinition": true
                    }
                }
            ],
            "jsdoc/require-description": "error",
            "jsdoc/require-param": [
                "error",
                {
                    "enableFixer": false
                }
            ],
            "jsdoc/match-name": [
                "error",
                {
                    "match": [
                        {
                            "tags": [
                                "param"
                            ],
                            "disallowName": "/^root\\d+$/",
                            "message": "Name the parameter for its role, such as options."
                        }
                    ]
                }
            ],
            "jsdoc/informative-docs": "error",
            "jsdoc/require-param-description": "error",
            "jsdoc/tag-lines": [
                "error",
                "any",
                {
                    "startLines": 1
                }
            ],
            "regexp/no-super-linear-backtracking": "error",
            "regexp/no-empty-alternative": "error",
            "regexp/no-empty-capturing-group": "error",
            "regexp/no-empty-character-class": "error",
            "regexp/no-empty-group": "error",
            "regexp/no-empty-lookarounds-assertion": "error",
            "regexp/no-useless-assertions": "error",
            "regexp/no-useless-backreference": "error",
            "regexp/no-useless-character-class": "error",
            "regexp/no-useless-dollar-replacements": "error",
            "regexp/no-useless-lazy": "error",
            "regexp/no-useless-quantifier": "error",
            "regexp/no-useless-range": "error",
            "regexp/no-lazy-ends": "error",
            "regexp/no-optional-assertion": "error",
            "regexp/no-invalid-regexp": "error",
            "regexp/no-misleading-capturing-group": "error",
            "regexp/no-contradiction-with-assertion": "error",
            "regexp/strict": "error",
            "import-x/export": "error",
            "import-x/no-cycle": [
                "error",
                {
                    "ignoreExternal": false
                }
            ],
            "import-x/no-self-import": "error",
            "import-x/no-useless-path-segments": "error",
            "import-x/no-empty-named-blocks": "error",
            "import-x/no-duplicates": "error",
            "no-restricted-syntax": [
                "error",
                {
                    "selector": ":matches(Program, BlockStatement, StaticBlock) > BlockStatement",
                    "message": "A block that stands alone hides a step. Name the step as a function, or remove the braces."
                },
                {
                    "selector": "TSEnumDeclaration",
                    "message": "Use a literal union or an as-const object instead of an enum."
                },
                {
                    "selector": "TSAsExpression[expression.type=\"TSAsExpression\"]",
                    "message": "Do not assert twice. Narrow the value, fix its type, or check it at run time."
                },
                {
                    "selector": "TSTypeAssertion[expression.type=\"TSTypeAssertion\"]",
                    "message": "Do not assert twice. Narrow the value, fix its type, or check it at run time."
                },
                {
                    "selector": "TSAsExpression > TSAnyKeyword",
                    "message": "Do not assert to any. Give the value a real type, or check it at run time."
                },
                {
                    "selector": "TSTypeAssertion > TSAnyKeyword",
                    "message": "Do not assert to any. Give the value a real type, or check it at run time."
                },
                {
                    "selector": "TSAsExpression > TSNeverKeyword",
                    "message": "Do not assert to never to silence the type system."
                },
                {
                    "selector": "TSTypeAssertion > TSNeverKeyword",
                    "message": "Do not assert to never to silence the type system."
                },
                {
                    "selector": "LogicalExpression[operator=\"||\"][right.type=\"ObjectExpression\"][right.properties.length=0]",
                    "message": "An empty-object fallback hides a missing value. Handle the missing case."
                },
                {
                    "selector": "LogicalExpression[operator=\"??\"][right.type=\"ObjectExpression\"][right.properties.length=0]",
                    "message": "An empty-object fallback hides a missing value. Handle the missing case."
                },
                {
                    "selector": "NewExpression[callee.name=/Error$/]:matches([arguments.length=1], [arguments.1.type=\"ObjectExpression\"]) > Literal.arguments:first-child[value=/^[a-z]/]",
                    "message": "Start an error message with a capital letter."
                },
                {
                    "selector": "NewExpression[callee.name=/Error$/]:matches([arguments.length=1], [arguments.1.type=\"ObjectExpression\"]) > TemplateLiteral.arguments:first-child[quasis.0.value.raw=/^[a-z]/]",
                    "message": "Start an error message with a capital letter."
                },
                {
                    "selector": "CallExpression:matches([callee.property.name=/^(debug|info|warn|error|fatal|trace)$/], [callee.property.name=\"log\"][callee.object.name!=\"console\"]) > TemplateLiteral.arguments:first-child[expressions.length>0]",
                    "message": "Log a stable message and pass the values as fields."
                }
            ],
            "max-lines": [
                "error",
                {
                    "max": 300,
                    "skipBlankLines": true,
                    "skipComments": true
                }
            ],
            "max-lines-per-function": [
                "error",
                {
                    "max": 60,
                    "skipBlankLines": true,
                    "skipComments": true,
                    "IIFEs": true
                }
            ],
            "max-params": [
                "error",
                {
                    "max": 7,
                    "countVoidThis": false
                }
            ],
            "max-depth": [
                "error",
                3
            ],
            "max-statements": [
                "error",
                30
            ],
            "max-nested-callbacks": [
                "error",
                3
            ],
            "complexity": [
                "error",
                8
            ],
            "sonarjs/cognitive-complexity": [
                "error",
                8
            ],
            "sonarjs/no-identical-functions": [
                "error",
                8
            ],
            "gspot/import-boundaries": [
                gspot.configs.all.rules["gspot/import-boundaries"] ?? 'off',
                {
                    "folders": [
                        "*/*"
                    ],
                    "aliases": {
                        "#web/*": "web/scripts/*"
                    }
                }
            ],
            "import-x/first": "error",
            "import-x/newline-after-import": [
                "error",
                {
                    "count": 1,
                    "considerComments": true
                }
            ]
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    // javascript
    {
        rules: {
            "no-unused-vars": [
                "error",
                {
                    "args": "all",
                    "argsIgnorePattern": "^_",
                    "varsIgnorePattern": "^_",
                    "destructuredArrayIgnorePattern": "^_"
                }
            ],
            "jsdoc/require-param-type": "error",
            "jsdoc/require-returns-type": "error",
            "jsdoc/check-types": "error",
            "jsdoc/no-undefined-types": "error",
            "jsdoc/valid-types": "error"
        },
        files: [
            "**/*.{js,mjs,cjs,jsx}"
        ]
    },
    // javascript
    {
        settings: {
            "n": {
                "tryExtensions": [
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".mjs",
                    ".mts",
                    ".cjs",
                    ".cts",
                    ".json",
                    ".node"
                ],
                "typescriptExtensionMap": []
            }
        },
        "ignores": [],
        rules: {
            "n/file-extension-in-import": [
                "error",
                "always"
            ]
        },
        files: [
            [
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ]
        ]
    },
    // javascript
    {
        settings: {
            "n": {
                "tryExtensions": [
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".mjs",
                    ".mts",
                    ".cjs",
                    ".cts",
                    ".json",
                    ".node"
                ],
                "typescriptExtensionMap": []
            }
        },
        "ignores": [],
        rules: {
            "n/file-extension-in-import": [
                "error",
                "always"
            ],
            "gspot/import-boundaries": [
                gspot.configs.all.rules["gspot/import-boundaries"] ?? 'off',
                {
                    "folders": [
                        "*/*"
                    ],
                    "aliases": {
                        "#web/*": "web/scripts/*"
                    }
                }
            ]
        },
        files: [
            "**/*.mjs",
            "**/*.cjs"
        ]
    },
    // javascript
    {
        settings: {
            ...{
                "boundaries/files": [
                    {
                        "category": "tests",
                        "pattern": [
                            "**/test/**",
                            "**/tests/**",
                            "**/__tests__/**",
                            "**/*.test.*",
                            "**/*.spec.*",
                            "**/test_*.py",
                            "**/*_test.py",
                            "**/conftest.py",
                            "**/Tests/**",
                            "**/*Tests.swift"
                        ],
                        "stopMatching": true
                    },
                    {
                        "category": "import-rule:page",
                        "pattern": [
                            "web/scripts/browser.ts",
                            "web/scripts/contracts.ts",
                            "web/scripts/dom.ts",
                            "web/scripts/host.d.ts",
                            "web/scripts/http.ts",
                            "web/scripts/nodes.ts",
                            "web/scripts/routes.ts",
                            "web/scripts/schema.ts",
                            "web/scripts/text.ts"
                        ]
                    },
                    {
                        "category": "import-rule:settings-dialog",
                        "pattern": [
                            "web/scripts/settings/**"
                        ]
                    },
                    {
                        "category": "import-rule:extension",
                        "pattern": [
                            "web/scripts/extension.ts"
                        ]
                    },
                    {
                        "category": "import-rule:config",
                        "pattern": [
                            "src/config/**"
                        ]
                    },
                    {
                        "category": "import-rule:state",
                        "pattern": [
                            "src/state/**"
                        ]
                    },
                    {
                        "category": "import-rule:storage",
                        "pattern": [
                            "src/storage/**"
                        ]
                    },
                    {
                        "category": "import-rule:openrouter",
                        "pattern": [
                            "src/openrouter/**"
                        ]
                    },
                    {
                        "category": "import-rule:settings",
                        "pattern": [
                            "src/settings/**"
                        ]
                    },
                    {
                        "category": "import-rule:comfy",
                        "pattern": [
                            "src/comfy/**"
                        ]
                    },
                    {
                        "category": "import-rule:nodes",
                        "pattern": [
                            "src/nodes/**"
                        ]
                    },
                    {
                        "category": "import-rule:entry",
                        "pattern": [
                            "__init__.py",
                            "src/__init__.py"
                        ]
                    },
                    {
                        "category": "import-rule:scripts",
                        "pattern": [
                            "scripts/**"
                        ]
                    },
                    {
                        "category": "other",
                        "pattern": [
                            "**/*"
                        ]
                    }
                ],
                "boundaries/ignore": [],
                "boundaries/elements": [
                    {
                        "type": "other",
                        "pattern": "**",
                        "partialMatch": false
                    }
                ],
                "boundaries/dependency-nodes": [
                    "require",
                    "dynamic-import"
                ],
                "boundaries/additional-dependency-nodes": [
                    {
                        "selector": "ImportDeclaration:not([importKind=type]):matches([specifiers.length=0], :has(ImportSpecifier:not([importKind=type]), ImportDefaultSpecifier, ImportNamespaceSpecifier)) > Literal",
                        "kind": "value",
                        "name": "import"
                    },
                    {
                        "selector": "ImportDeclaration:matches([importKind=type], [specifiers.length>0]:not(:has(ImportSpecifier:not([importKind=type]), ImportDefaultSpecifier, ImportNamespaceSpecifier))) > Literal",
                        "kind": "type",
                        "name": "import"
                    },
                    {
                        "selector": ":matches(ExportAllDeclaration:not([exportKind=type]), ExportNamedDeclaration:not([exportKind=type]):matches([specifiers.length=0], :has(ExportSpecifier:not([exportKind=type])))) > Literal",
                        "kind": "value",
                        "name": "export"
                    },
                    {
                        "selector": ":matches(ExportAllDeclaration[exportKind=type], ExportNamedDeclaration:matches([exportKind=type], [specifiers.length>0]:not(:has(ExportSpecifier:not([exportKind=type]))))) > Literal",
                        "kind": "type",
                        "name": "export"
                    }
                ]
            },
            'import/resolver': {
                typescript: {
                    project: [
                        join(root, "tsconfig.json")
                    ]
                }
            }
        },
        rules: {
            "boundaries/dependencies": [
                "error",
                {
                    "default": "disallow",
                    "policies": [
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:page"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"page\" may import only its own files, not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:page"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:page"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:settings-dialog"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"settings-dialog\" may import its own files and \"page\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:settings-dialog"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:settings-dialog",
                                                "import-rule:page"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:extension"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"extension\" may import its own files and \"page\", \"settings-dialog\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:extension"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:extension",
                                                "import-rule:page",
                                                "import-rule:settings-dialog"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:config"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"config\" may import only its own files, not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:config"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:config"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:state"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"state\" may import its own files and \"config\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:state"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:state",
                                                "import-rule:config"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:storage"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"storage\" may import its own files and \"config\", \"state\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:storage"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:storage",
                                                "import-rule:config",
                                                "import-rule:state"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:openrouter"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"openrouter\" may import its own files and \"config\", \"state\", \"storage\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:openrouter"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:openrouter",
                                                "import-rule:config",
                                                "import-rule:state",
                                                "import-rule:storage"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:settings"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"settings\" may import its own files and \"config\", \"state\", \"storage\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:settings"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:settings",
                                                "import-rule:config",
                                                "import-rule:state",
                                                "import-rule:storage"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:comfy"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"comfy\" may import its own files and \"config\", \"state\", \"storage\", \"openrouter\", \"settings\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:comfy"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:comfy",
                                                "import-rule:config",
                                                "import-rule:state",
                                                "import-rule:storage",
                                                "import-rule:openrouter",
                                                "import-rule:settings"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:nodes"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"nodes\" may import its own files and \"config\", \"state\", \"openrouter\", \"settings\", \"comfy\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:nodes"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:nodes",
                                                "import-rule:config",
                                                "import-rule:state",
                                                "import-rule:openrouter",
                                                "import-rule:settings",
                                                "import-rule:comfy"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:entry"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"entry\" may import its own files and \"comfy\", \"nodes\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:entry"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:entry",
                                                "import-rule:comfy",
                                                "import-rule:nodes"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:scripts"
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            },
                            "message": "Import rule \"scripts\" may import its own files and \"config\", \"comfy\", \"nodes\", not {{dependency.source}} from {{to.file.categories.[0]}}. Move the code, move that rule above this one, or list the rules it may import in can_import."
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": "import-rule:scripts"
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "anyOf": [
                                                "import-rule:scripts",
                                                "import-rule:config",
                                                "import-rule:comfy",
                                                "import-rule:nodes"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "isUnknown": true
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            }
                        },
                        {
                            "allow": {
                                "to": {
                                    "file": {
                                        "isUnknown": true
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "path": [
                                        "**/test/**",
                                        "**/tests/**",
                                        "**/__tests__/**",
                                        "**/*.test.*",
                                        "**/*.spec.*",
                                        "**/test_*.py",
                                        "**/*_test.py",
                                        "**/conftest.py",
                                        "**/Tests/**",
                                        "**/*Tests.swift"
                                    ]
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            }
                        },
                        {
                            "allow": {
                                "to": {
                                    "file": {
                                        "path": [
                                            "**/test/**",
                                            "**/tests/**",
                                            "**/__tests__/**",
                                            "**/*.test.*",
                                            "**/*.spec.*",
                                            "**/test_*.py",
                                            "**/*_test.py",
                                            "**/conftest.py",
                                            "**/Tests/**",
                                            "**/*Tests.swift"
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": {
                                        "noneOf": [
                                            "import-rule:page",
                                            "import-rule:settings-dialog",
                                            "import-rule:extension",
                                            "import-rule:config",
                                            "import-rule:state",
                                            "import-rule:storage",
                                            "import-rule:openrouter",
                                            "import-rule:settings",
                                            "import-rule:comfy",
                                            "import-rule:nodes",
                                            "import-rule:entry",
                                            "import-rule:scripts"
                                        ]
                                    }
                                }
                            },
                            "allow": {
                                "to": {
                                    "file": {
                                        "path": "**/*"
                                    }
                                }
                            }
                        },
                        {
                            "allow": {
                                "to": {
                                    "file": {
                                        "categories": {
                                            "noneOf": [
                                                "import-rule:page",
                                                "import-rule:settings-dialog",
                                                "import-rule:extension",
                                                "import-rule:config",
                                                "import-rule:state",
                                                "import-rule:storage",
                                                "import-rule:openrouter",
                                                "import-rule:settings",
                                                "import-rule:comfy",
                                                "import-rule:nodes",
                                                "import-rule:entry",
                                                "import-rule:scripts"
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "from": {
                                "file": {
                                    "categories": {
                                        "noneOf": [
                                            "tests"
                                        ]
                                    }
                                }
                            },
                            "disallow": {
                                "to": {
                                    "file": {
                                        "categories": "tests"
                                    }
                                }
                            }
                        }
                    ],
                    "checkInternals": true
                }
            ]
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    ...typescriptBlocks,
    // javascript
    {
        languageOptions: {
            sourceType: "module",
            globals: globals["nodeBuiltin"]
        },
        rules: {
            "n/no-unsupported-features/node-builtins": [
                "error",
                {
                    "allowExperimental": true
                }
            ],
            "n/no-unsupported-features/es-builtins": "error",
            "n/no-deprecated-api": "error",
            "unicorn/no-process-exit": "off",
            "n/no-unsupported-features/es-syntax": "off",
            "n/no-sync": "off",
            "n/no-callback-literal": "error",
            "n/no-new-require": "error",
            "n/no-path-concat": "error",
            "n/no-missing-import": "off",
            "n/no-missing-require": "off",
            "n/no-unpublished-import": [
                "error",
                {
                    "ignoreTypeImport": true
                }
            ],
            "n/no-unpublished-require": "error",
            "n/no-extraneous-import": "error",
            "n/no-extraneous-require": "error",
            "n/prefer-global/url-search-params": [
                "error",
                "always"
            ],
            "n/prefer-global/url": [
                "error",
                "always"
            ],
            "n/prefer-global/process": [
                "error",
                "always"
            ],
            "n/prefer-global/console": [
                "error",
                "always"
            ],
            "n/prefer-global/buffer": [
                "error",
                "always"
            ],
            "n/no-process-exit": "error",
            "n/prefer-promises/dns": "error",
            "n/prefer-promises/fs": "error"
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                runtimeMatches(0, runtimeDeclarations)
            ]
        ]
    },
    // javascript
    {
        languageOptions: {
            sourceType: "commonjs",
            globals: globals["node"]
        },
        rules: {
            "n/no-unsupported-features/node-builtins": [
                "error",
                {
                    "allowExperimental": true
                }
            ],
            "n/no-unsupported-features/es-builtins": "error",
            "n/no-deprecated-api": "error",
            "unicorn/no-process-exit": "off",
            "n/no-unsupported-features/es-syntax": "off",
            "n/no-sync": "off",
            "n/no-callback-literal": "error",
            "n/no-new-require": "error",
            "n/no-path-concat": "error",
            "n/no-missing-import": "off",
            "n/no-missing-require": "off",
            "n/no-unpublished-import": [
                "error",
                {
                    "ignoreTypeImport": true
                }
            ],
            "n/no-unpublished-require": "error",
            "n/no-extraneous-import": "error",
            "n/no-extraneous-require": "error",
            "n/prefer-global/url-search-params": [
                "error",
                "always"
            ],
            "n/prefer-global/url": [
                "error",
                "always"
            ],
            "n/prefer-global/process": [
                "error",
                "always"
            ],
            "n/prefer-global/console": [
                "error",
                "always"
            ],
            "n/prefer-global/buffer": [
                "error",
                "always"
            ],
            "n/no-process-exit": "error",
            "n/prefer-promises/dns": "error",
            "n/prefer-promises/fs": "error",
            "unicorn/prefer-module": "off"
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                runtimeMatches(1, runtimeDeclarations)
            ]
        ]
    },
    // javascript
    {
        languageOptions: {
            sourceType: "module",
            globals: globals["browser"]
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                runtimeMatches(2, runtimeDeclarations)
            ]
        ]
    },
    // javascript
    {
        "ignores": [],
        rules: {
            "no-restricted-syntax": [
                "error",
                {
                    "selector": ":matches(Program, BlockStatement, StaticBlock) > BlockStatement",
                    "message": "A block that stands alone hides a step. Name the step as a function, or remove the braces."
                },
                {
                    "selector": "TSEnumDeclaration",
                    "message": "Use a literal union or an as-const object instead of an enum."
                },
                {
                    "selector": "TSAsExpression[expression.type=\"TSAsExpression\"]",
                    "message": "Do not assert twice. Narrow the value, fix its type, or check it at run time."
                },
                {
                    "selector": "TSTypeAssertion[expression.type=\"TSTypeAssertion\"]",
                    "message": "Do not assert twice. Narrow the value, fix its type, or check it at run time."
                },
                {
                    "selector": "TSAsExpression > TSAnyKeyword",
                    "message": "Do not assert to any. Give the value a real type, or check it at run time."
                },
                {
                    "selector": "TSTypeAssertion > TSAnyKeyword",
                    "message": "Do not assert to any. Give the value a real type, or check it at run time."
                },
                {
                    "selector": "TSAsExpression > TSNeverKeyword",
                    "message": "Do not assert to never to silence the type system."
                },
                {
                    "selector": "TSTypeAssertion > TSNeverKeyword",
                    "message": "Do not assert to never to silence the type system."
                },
                {
                    "selector": "LogicalExpression[operator=\"||\"][right.type=\"ObjectExpression\"][right.properties.length=0]",
                    "message": "An empty-object fallback hides a missing value. Handle the missing case."
                },
                {
                    "selector": "LogicalExpression[operator=\"??\"][right.type=\"ObjectExpression\"][right.properties.length=0]",
                    "message": "An empty-object fallback hides a missing value. Handle the missing case."
                },
                {
                    "selector": "NewExpression[callee.name=/Error$/]:matches([arguments.length=1], [arguments.1.type=\"ObjectExpression\"]) > Literal.arguments:first-child[value=/^[a-z]/]",
                    "message": "Start an error message with a capital letter."
                },
                {
                    "selector": "NewExpression[callee.name=/Error$/]:matches([arguments.length=1], [arguments.1.type=\"ObjectExpression\"]) > TemplateLiteral.arguments:first-child[quasis.0.value.raw=/^[a-z]/]",
                    "message": "Start an error message with a capital letter."
                },
                {
                    "selector": "CallExpression:matches([callee.property.name=/^(debug|info|warn|error|fatal|trace)$/], [callee.property.name=\"log\"][callee.object.name!=\"console\"]) > TemplateLiteral.arguments:first-child[expressions.length>0]",
                    "message": "Log a stable message and pass the values as fields."
                },
                {
                    "selector": "ExportAllDeclaration",
                    "message": "Export values at their declaration instead of re-exporting them."
                },
                {
                    "selector": "ExportNamedDeclaration[source!=null]",
                    "message": "Export values at their declaration instead of re-exporting them."
                },
                {
                    "selector": ":matches(ImportDeclaration, ExportAllDeclaration, ExportNamedDeclaration, ImportExpression)[source.value=/^(#[^/]+\\/|@\\/)/][source.value!=/\\.[^/?.]+$/]:not([source.value=/\\?/]):not(:has(ImportAttribute:matches([key.name='type'],[key.value='type'])[value.value='json']))",
                    "message": "Give an alias import its file extension."
                }
            ]
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "**/*"
            ]
        ]
    },
    // javascript
    {
        "ignores": [
            "**/test/**",
            "**/tests/**",
            "**/__tests__/**",
            "**/*.test.*",
            "**/*.spec.*",
            "**/test_*.py",
            "**/*_test.py",
            "**/conftest.py",
            "**/Tests/**",
            "**/*Tests.swift",
            "scripts/**",
            "**/*.config.{js,mjs,cjs,ts}",
            ".mise/tasks/**"
        ],
        rules: {
            "no-console": "error"
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "**/*"
            ]
        ]
    },
    // javascript
    {
        rules: {
            "n/no-process-exit": "off",
            "unicorn/no-process-exit": "off"
        },
        files: [
            [
                "scripts/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/*.config.{js,mjs,cjs,ts}",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                ".mise/tasks/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ]
        ]
    },
    // javascript
    {
        rules: {
            "jsdoc/require-jsdoc": "off",
            "jsdoc/require-param": "off",
            "jsdoc/require-description": "off",
            "jsdoc/require-param-description": "off",
            "n/no-unpublished-import": "off",
            "n/no-unpublished-require": "off"
        },
        files: [
            [
                "**/test/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/tests/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/__tests__/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/*.test.*",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/*.spec.*",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/test_*.py",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/*_test.py",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/conftest.py",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/Tests/**",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ],
            [
                "**/*Tests.swift",
                "**/*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
            ]
        ]
    },
    // javascript: packageJson["configs"]["recommended"].rules
    {
        ...packageJson["configs"]["recommended"],
        rules: {
            ...packageJson["configs"]["recommended"].rules
        },
        files: [
            "**/package.json"
        ]
    },
    // javascript: prettierConfig.rules
    {
        ...prettierConfig,
        rules: {
            ...prettierConfig.rules
        },
        files: [
            "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
        ]
    },
    // javascript
    {
        rules: {
            "package-json/restrict-dependency-ranges": [
                "error",
                {
                    "rangeType": "pin"
                }
            ]
        },
        files: [
            "**/package.json"
        ]
    },
    // javascript
    {
        rules: {
            "package-json/require-packageManager": "error"
        },
        files: [
            "package.json"
        ]
    },
    // javascript
    {
        rules: {
            "max-lines": [
                "error",
                {
                    "max": 300,
                    "skipBlankLines": true,
                    "skipComments": true
                }
            ],
            "max-lines-per-function": [
                "error",
                {
                    "max": 60,
                    "skipBlankLines": true,
                    "skipComments": true,
                    "IIFEs": true
                }
            ],
            "max-params": [
                "error",
                {
                    "max": 7,
                    "countVoidThis": false
                }
            ],
            "max-depth": [
                "error",
                3
            ],
            "max-statements": [
                "error",
                30
            ],
            "max-nested-callbacks": [
                "error",
                3
            ],
            "complexity": [
                "error",
                8
            ],
            "sonarjs/cognitive-complexity": [
                "error",
                8
            ]
        },
        files: [
            "**/*.{js,mjs,cjs,jsx}"
        ]
    },
    // javascript
    {
        "ignores": [],
        rules: {
            "gspot/no-trivial-files": [
                gspot.configs.all.rules["gspot/no-trivial-files"] ?? 'off',
                {
                    "allowIndex": false
                }
            ],
            "gspot/no-trivial-functions": [
                gspot.configs.all.rules["gspot/no-trivial-functions"] ?? 'off',
                {
                    "trivialFunctionStatements": 2
                }
            ]
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "**/*.{js,mjs,cjs,jsx}"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "**/*.{ts,mts,cts,tsx,vue,svelte,astro}"
            ]
        ]
    },
    // javascript
    {
        "ignores": [],
        rules: {
            "gspot/import-boundaries": "off"
        },
        files: [
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/extension.ts"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/extension.ts/**"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/http.ts"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/http.ts/**"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/text.ts"
            ],
            [
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*",
                "web/scripts/text.ts/**"
            ]
        ]
    },
];
