import { app } from '../../scripts/app.js';

/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
  close: 'Close',
  settings: {
    moreLimits: 'Advanced limits',
    clearKey: 'Clear Saved Key',
    close: 'Close OpenRouter settings',
    credentialLabel: 'OpenRouter API key',
    credentials: 'Credentials',
    environmentKey: "The server's OPENROUTER_API_KEY environment variable is active.",
    invalidDefinition: 'ComfyUI returned an invalid OpenRouter setting definition.',
    invalidLimit: 'ComfyUI returned an invalid OpenRouter limit.',
    invalidResponse: 'ComfyUI returned an invalid OpenRouter settings response.',
    keyCleared: 'Saved key cleared. Any environment key remains active.',
    keyNotice:
      'The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked here.',
    keySaved: 'Key saved on this server. OpenRouter checks it on the next request.',
    limits: 'Request limits',
    limitsSaved: 'Limits saved. They apply to new requests.',
    reread: 'Local settings loaded.',
    reading: 'Loading local settings...',
    missingKey: 'No OpenRouter key is configured.',
    noLimitChanges: 'No limit changes to save.',
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: 'Reload Settings',
    saveFailed: 'ComfyUI could not save OpenRouter settings.',
    saveKey: 'Save Key',
    saveLimits: 'Save Limits',
    savedKey: 'A saved key is configured on this server.',
    timeNotice:
      'The request timeout applies to each request. The maximum video wait applies to a whole video job.',
    title: 'OpenRouter Settings',
    unreachable: 'Cannot reach OpenRouter settings. Check ComfyUI and try again.',
    unreadableResponse: 'ComfyUI returned an unreadable OpenRouter settings response.',
    updateFailed: 'OpenRouter settings could not be saved.',
    readFailed: 'ComfyUI could not read OpenRouter settings.',
    removeFailed: 'ComfyUI could not clear the saved OpenRouter key.',
    menu: 'OpenRouter settings',
  },
  working: 'Working...',
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
  ['max_download_megabytes', 'maximum download size (MiB)'],
  ['max_upload_megabytes', 'maximum upload size (MiB)'],
  ['parallel_requests', 'parallel requests'],
  ['request_timeout_seconds', 'request timeout (seconds)'],
  ['video_check_interval_seconds', 'video check interval (seconds)'],
  ['video_retry_delay_minutes', 'video retry delay (minutes)'],
  ['video_wait_minutes', 'maximum video wait (minutes)'],
]);

type MessagePaths<Messages> = {
  [Key in keyof Messages & string]: Messages[Key] extends string
    ? Key
    : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;

/**
 * Read one message.
 * @param key - A dotted path into the extension's text.
 * @returns The message.
 */
export function message(key: MessageKey): string {
  let value: unknown = TEXT;
  for (const part of key.split('.')) {
    // eslint-disable-next-line security/detect-object-injection -- The key is a literal path checked by its type.
    value = (value as Record<string, unknown>)[part];
  }
  return String(value);
}

/**
 * Replace an element's text.
 * @param target - The element whose text the extension owns.
 * @param content - The new text.
 */
export function setText(target: HTMLElement, content: string): void {
  // reason: The content becomes a Text node, never parsed HTML.
  // bearer:disable javascript_lang_dangerous_insert_html
  target.replaceChildren(document.createTextNode(content));
}

/**
 * Read the language ComfyUI shows, which the server's messages follow.
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
  const value = app.extensionManager.setting.get('Comfy.Locale');
  try {
    return (
      Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ??
      'en'
    );
  } catch {
    return 'en';
  }
}
