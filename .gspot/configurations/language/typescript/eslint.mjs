import { root, stripRuntimeGlobals } from "../javascript/eslint/functions.mjs";
import globals from "globals";
import { join } from "node:path";
import tseslint from "typescript-eslint";
import { createTypeScriptImportResolver } from "eslint-import-resolver-typescript";
export default [
    // typescript: tseslint["configs"]["strictTypeChecked"][0].rules
    stripRuntimeGlobals({
        ...tseslint["configs"]["strictTypeChecked"][0],
        "ignores": [],
        rules: {
            ...tseslint["configs"]["strictTypeChecked"][0].rules
        },
        files: [
            [
                "**/*.{ts,mts,cts,tsx}",
                "**/*"
            ]
        ]
    }, globals),
    // typescript: tseslint["configs"]["strictTypeChecked"][1].rules
    stripRuntimeGlobals({
        ...tseslint["configs"]["strictTypeChecked"][1],
        "ignores": [],
        rules: {
            ...tseslint["configs"]["strictTypeChecked"][1].rules
        },
        files: [
            [
                "**/*.{ts,mts,cts,tsx}",
                "**/*"
            ]
        ]
    }, globals),
    // typescript: tseslint["configs"]["strictTypeChecked"][2].rules
    stripRuntimeGlobals({
        ...tseslint["configs"]["strictTypeChecked"][2],
        "ignores": [],
        rules: {
            ...tseslint["configs"]["strictTypeChecked"][2].rules
        },
        files: [
            [
                "**/*.{ts,mts,cts,tsx}",
                "**/*"
            ]
        ]
    }, globals),
    // typescript
    stripRuntimeGlobals({
        plugins: {
            '@typescript-eslint': tseslint.plugin
        },
        languageOptions: {
            parserOptions: {
                projectService: true,
                tsconfigRootDir: root
            }
        },
        settings: {
            'import-x/parsers': {
                '@typescript-eslint/parser': [
                    ".ts",
                    ".tsx",
                    ".mts",
                    ".cts"
                ]
            },
            'import-x/resolver-next': [
                createTypeScriptImportResolver({
                    project: [
                        join(root, "tsconfig.json")
                    ]
                })
            ]
        },
        "ignores": [],
        rules: {
            "@typescript-eslint/no-misused-spread": [
                "error",
                {
                    "allow": [
                        "string"
                    ]
                }
            ],
            "sonarjs/deprecation": "off",
            "jsdoc/require-param-type": "off",
            "jsdoc/require-returns-type": "off",
            "jsdoc/check-types": "off",
            "jsdoc/no-undefined-types": "off",
            "jsdoc/valid-types": "off",
            "jsdoc/no-types": "error",
            "jsdoc/check-tag-names": [
                "error",
                {
                    "typed": true
                }
            ],
            "@typescript-eslint/consistent-type-definitions": [
                "error",
                "type"
            ],
            "@typescript-eslint/consistent-type-imports": [
                "error",
                {
                    "prefer": "type-imports",
                    "fixStyle": "separate-type-imports"
                }
            ],
            "import-x/no-duplicates": [
                "error",
                {
                    "prefer-inline": true
                }
            ],
            "@typescript-eslint/consistent-type-exports": [
                "error",
                {
                    "fixMixedExportsWithInlineTypeSpecifier": false
                }
            ],
            "@typescript-eslint/switch-exhaustiveness-check": [
                "error",
                {
                    "considerDefaultExhaustiveForUnions": true
                }
            ],
            "@typescript-eslint/prefer-readonly": "error",
            "@typescript-eslint/require-array-sort-compare": [
                "error",
                {
                    "ignoreStringArrays": true
                }
            ],
            "@typescript-eslint/no-floating-promises": [
                "error",
                {
                    "ignoreVoid": false
                }
            ],
            "@typescript-eslint/no-unused-vars": [
                "error",
                {
                    "args": "all",
                    "argsIgnorePattern": "^_",
                    "varsIgnorePattern": "^_",
                    "destructuredArrayIgnorePattern": "^_",
                    "ignoreUsingDeclarations": true
                }
            ],
            "@typescript-eslint/no-require-imports": "off",
            "@typescript-eslint/strict-boolean-expressions": "error",
            "@typescript-eslint/explicit-module-boundary-types": "error",
            "@typescript-eslint/prefer-optional-chain": "error",
            "gspot/no-magic-numbers": [
                "error",
                {
                    "ignoreEnums": true,
                    "ignoreArrayIndexes": true,
                    "ignoreReadonlyClassProperties": true,
                    "ignoreTypeIndexes": true,
                    "ignore": [
                        -1, 0, 1
                    ]
                }
            ],
            "@typescript-eslint/ban-ts-comment": [
                "error",
                {
                    "ts-expect-error": false,
                    "ts-ignore": true,
                    "ts-nocheck": true
                }
            ],
            "sonarjs/no-duplicate-in-composite": "error",
            "sonarjs/redundant-type-aliases": "error",
            "no-unused-vars": "off"
        },
        files: [
            [
                "**/*.{ts,mts,cts,tsx}",
                "**/*"
            ]
        ]
    }, globals),
    // typescript
    stripRuntimeGlobals({
        "ignores": [],
        rules: {
            "gspot/no-magic-numbers": "off",
            "@typescript-eslint/no-non-null-assertion": "off"
        },
        files: [
            [
                "**/test/**",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/tests/**",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/__tests__/**",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/*.test.*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/*.spec.*",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/test_*.py",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/*_test.py",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/conftest.py",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/Tests/**",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ],
            [
                "**/*Tests.swift",
                "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}",
                "**/*"
            ]
        ]
    }, globals),
];
