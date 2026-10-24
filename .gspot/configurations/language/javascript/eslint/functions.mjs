import picomatch from 'picomatch';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { sep, relative } from 'node:path';
export const root = fileURLToPath(new URL('../../../../..', import.meta.url)).replace(/[\\/]$/u, '');
const componentParserOptions = { tsconfigRootDir: root, ecmaVersion: 'latest', sourceType: 'module' };
const runtimeGlobalNames = new WeakMap();
const runtimeMatcherGroups = new WeakMap();
/**
 * Remove host runtime globals and keep framework compiler and test names. Runtime APIs get their globals from blocks with
 * their own file selectors.
 *
 * @param block the framework ESLint configuration block.
 * @param globalsByRuntime the globals tables of the globals package, keyed by runtime name.
 * @returns a copy of the block without the runtime names in its globals, or the block itself when it declares no globals.
 */
export function stripRuntimeGlobals(block, globalsByRuntime) {
    const blockGlobals = block.languageOptions?.globals;
    if (blockGlobals === undefined)
        return block;
    let runtimeNames = runtimeGlobalNames.get(globalsByRuntime);
    if (runtimeNames === undefined) {
        runtimeNames = new Set(Object.keys({
            ...globalsByRuntime['node'],
            ...globalsByRuntime['browser'],
            ...globalsByRuntime['worker'],
            ...globalsByRuntime['serviceworker'],
            ...globalsByRuntime['react-native'],
        }));
        runtimeGlobalNames.set(globalsByRuntime, runtimeNames);
    }
    const names = runtimeNames;
    return {
        ...block,
        languageOptions: {
            ...block.languageOptions,
            globals: Object.fromEntries(Object.entries(blockGlobals).filter(([name]) => !names.has(name))),
        },
    };
}
/**
 * Select the files that one runtime declaration covers: a later declaration that covers a file wins.
 *
 * @param index the position of the runtime declaration that this matcher stands for.
 * @param runtimes the runtime declarations, in order.
 * @returns whether a file belongs to this declaration after later ones apply.
 */
export function runtimeMatches(index, runtimes) {
    let matchers = runtimeMatcherGroups.get(runtimes);
    if (matchers === undefined) {
        matchers = runtimes.map(({ scope, includes, excludes }) => {
            const included = includes.map((glob) => picomatch(glob, { dot: true, flags: 's' }));
            const excluded = excludes.map((glob) => picomatch(glob, { dot: true, flags: 's' }));
            return (path) => (scope === '' || path.startsWith(`${scope}/`)) &&
                included.some((pattern) => pattern(path)) &&
                !excluded.some((pattern) => pattern(path));
        });
        runtimeMatcherGroups.set(runtimes, matchers);
    }
    const ordered = matchers;
    return (file) => ordered.findLastIndex((matches) => matches(relative(root, file).split(sep).join('/'))) === index;
}
/**
 * Select the Vue or Svelte files whose script element asks for TypeScript. The final parser reports syntax errors, so a
 * file that does not parse counts as untyped.
 *
 * @param parser vue-eslint-parser or svelte-eslint-parser.
 * @param typescriptParser the parser of TypeScript script elements, which svelte-eslint-parser takes.
 * @returns whether a file has a TypeScript script element.
 */
export function componentMatches(parser, typescriptParser) {
    const scriptParser = typescriptParser === undefined ? false : { ts: typescriptParser, typescript: typescriptParser };
    return (file) => {
        try {
            const parsed = parser.parseForESLint(readFileSync(file, 'utf8'), {
                ...componentParserOptions,
                filePath: file,
                parser: scriptParser,
            });
            const vueComponent = parsed.services?.getDocumentFragment?.();
            const languages = vueComponent === undefined
                ? parsed.ast.body
                    .filter((node) => node.type === 'SvelteScriptElement')
                    .flatMap((script) => script.startTag.attributes)
                    .filter((attribute) => attribute.key?.name === 'lang')
                    .map((attribute) => attribute.value[0]?.value)
                : vueComponent.children
                    .filter((node) => node.type === 'VElement' && node.name === 'script')
                    .flatMap((script) => script.startTag.attributes)
                    .filter((attribute) => attribute.key?.name === 'lang')
                    .map((attribute) => attribute.value?.value);
            return languages.some((language) => language === 'ts' || language === 'typescript');
        }
        catch (error) {
            if (error instanceof SyntaxError || (error instanceof Error && error.name === 'TSError'))
                return false;
            throw error;
        }
    };
}
