import { app } from '../../scripts/app.js';

/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
    close: 'Close',
    settings: {
        clearKey: 'Clear Saved Key',
        close: 'Close OpenRouter Settings',
        credentialLabel: 'OpenRouter API key',
        credentials: 'Credentials',
        environmentKey: 'Set by OPENROUTER_API_KEY',
        invalidDefinition: 'ComfyUI returned an invalid OpenRouter setting definition.',
        invalidLimit: 'ComfyUI returned an invalid OpenRouter limit.',
        invalidResponse: 'ComfyUI returned an invalid OpenRouter settings response.',
        keyCleared: 'Saved key cleared.',
        keyNotice:
            'Add an OpenRouter API key to use the extension. Your key stays on your ComfyUI server and is sent only to OpenRouter.',
        keySaved: 'Key saved.',
        limits: 'Request limits',
        limitsSaved: 'Limits saved.',
        reread: 'Settings loaded.',
        reading: 'Loading settings...',
        noLimitChanges: 'No limit changes to save.',
        readOnly: "Changes are disabled in this host's multi-user mode.",
        reload: 'Reload Settings',
        saveFailed: 'ComfyUI could not save OpenRouter settings.',
        saveKey: 'Save Key',
        saveLimits: 'Save Limits',
        savedKey: 'Saved key',
        title: 'OpenRouter Settings',
        unreachable: 'Cannot reach OpenRouter settings. Check ComfyUI and try again.',
        unreadableResponse: 'ComfyUI returned an unreadable OpenRouter settings response.',
        updateFailed: 'OpenRouter settings could not be saved.',
        readFailed: 'ComfyUI could not read OpenRouter settings.',
        removeFailed: 'ComfyUI could not clear the saved OpenRouter API key.',
        menu: 'OpenRouter Settings',
    },
    working: 'Working...',
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
    ['max_download_megabytes', 'Maximum download size (MiB)'],
    ['max_upload_megabytes', 'Maximum upload size (MiB)'],
    ['request_timeout_seconds', 'Request timeout (seconds)'],
]);

type MessagePaths<Messages> = {
    [Key in keyof Messages & string]: Messages[Key] extends string ? Key : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;

/**
 * Read one message.
 *
 * @param key - A dotted path into the extension's text.
 * @returns The text at that path.
 */
export function message(key: MessageKey): string {
    let value: unknown = TEXT;
    for (const part of key.split('.')) {
        value = (value as Record<string, unknown>)[part];
    }
    return String(value);
}

/**
 * Read the language ComfyUI shows, which the server's messages follow.
 *
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
    const value = app.extensionManager.setting.get('Comfy.Locale');
    try {
        return Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ?? 'en';
    } catch {
        return 'en';
    }
}
