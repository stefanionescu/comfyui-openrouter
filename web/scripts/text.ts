import { app } from '../../scripts/app.js';

/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
  close: 'Close',
  models: {
    checkDue: 'An automatic model check is due. Checks do not change this list.',
    checkRunning: 'An automatic model check is running. Reopen this list to see its result.',
    checkSchedule: 'Automatic check: {date}. Checks run every {hours} hours.',
    checking: "Checking OpenRouter's public model lists...",
    checksOff: 'Automatic model checks are off. Change this in OpenRouter settings.',
    close: 'Close OpenRouter models',
    count: '{visible} of {total} models',
    damaged:
      'The saved model list could not be read, so the nodes show the list that came with this version. Refresh Models to replace it.',
    installedList:
      'Showing the model list that came with this version. Refresh Models to load current models and prices.',
    invalidResponse: 'ComfyUI returned an invalid OpenRouter model list.',
    lastRefresh: 'Models and prices checked {date}.',
    listChanged: 'The model list has changed. Select Refresh Models to update your list.',
    readFailed: 'Cannot load models.',
    reread: 'Local model list loaded.',
    reading: 'Loading model list...',
    readingLocal: 'Loading the local model list...',
    nodeUnavailable: 'No node lists this model. Choose other model ID in a node and type its ID.',
    nodesAvailable: 'Used by: {nodes}.',
    openGuide: 'Model page on OpenRouter (opens in a new tab)',
    refresh: 'Refresh Models',
    refreshNotice: 'Refresh updates models and prices. The node dropdowns show the refreshed list.',
    refreshed: 'Model list refreshed.',
    reloadNodes: 'The node dropdowns now show this list.',
    requestFailed: 'The model list request failed.',
    restore: 'Restore Previous List',
    restored: 'Previous model list restored.',
    search: 'Search models',
    searchPlaceholder: 'Model name, ID, or node',
    sources: 'Model sources and automatic checks',
    title: 'OpenRouter Models',
    unreachable: 'Cannot reach the OpenRouter model list. Check ComfyUI and try again.',
    menu: 'OpenRouter models',
  },
  pricing: {
    calculate: 'Calculate a price',
    calculation: 'Estimate: {amount}.',
    inputTokens: 'input tokens',
    outputTokens: 'output tokens',
    videoSeconds: 'video seconds',
    perMillionInput: 'per 1M input tokens',
    perMillionOutput: 'per 1M output tokens',
    perMillionCharacters: 'per 1M characters',
    perRequest: 'per request',
    perVideoSecond: 'per video second',
    range: '{lowest} to {highest}, by sound and resolution',
    rate: '{price} {unit}',
    rateOutdated:
      'This model was not in the latest list. Refresh OpenRouter models before relying on its price.',
    rateUnavailable: 'OpenRouter lists no price for this model.',
    totalTimeNotice: 'The estimate is not a quote; OpenRouter decides each charge.',
  },
  settings: {
    moreLimits: 'Advanced limits',
    automaticChecks: 'Check for model updates automatically',
    checkInterval: 'check interval (hours)',
    checkNotice:
      "Checks read OpenRouter's public model lists. Open OpenRouter models to see changes and refresh your list.",
    checksSaved: 'Model check settings saved. Changes take effect within one minute.',
    clearKey: 'Clear Saved Key',
    close: 'Close OpenRouter settings',
    credentialLabel: 'OpenRouter API key',
    credentials: 'Credentials',
    environmentKey: "The server's OPENROUTER_API_KEY environment variable is active.",
    incompleteResponse: 'ComfyUI returned incomplete OpenRouter settings.',
    invalidChecks: 'ComfyUI returned invalid model check settings.',
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
    modelUpdates: 'Model updates',
    noCheckChanges: 'No model check changes to save.',
    noLimitChanges: 'No limit changes to save.',
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: 'Reload Settings',
    saveChecks: 'Save Model Check Settings',
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
  ['model_interval_hours', 'check interval (hours)'],
  ['parallel_requests', 'parallel requests'],
  ['request_timeout_seconds', 'request timeout (seconds)'],
  ['resubmit_hold_minutes', 'resubmit hold (minutes)'],
  ['video_poll_seconds', 'video check interval (seconds)'],
  ['video_wait_minutes', 'maximum video wait (minutes)'],
]);

type MessagePaths<Messages> = {
  [Key in keyof Messages & string]: Messages[Key] extends string
    ? Key
    : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;
type MessageValues = Record<string, string | number>;

/**
 * Read one message and insert its named values as plain text.
 * @param key - A dotted path into the extension's text.
 * @param values - Named values inserted for `{name}` placeholders.
 * @returns The rendered message.
 */
export function message(key: MessageKey, values: MessageValues = {}): string {
  let value: unknown = TEXT;
  for (const part of key.split('.')) {
    // eslint-disable-next-line security/detect-object-injection -- The key is a literal path checked by its type.
    value = (value as Record<string, unknown>)[part];
  }
  return String(value).replaceAll(/\{(\w+)\}/g, (placeholder, name: string) => {
    if (!Object.hasOwn(values, name)) return placeholder;
    // eslint-disable-next-line security/detect-object-injection -- Interpolation reads an own property of the caller's display values and inserts it as plain text.
    const inserted = values[name];
    return typeof inserted === 'number' ? formatNumber(inserted) : String(inserted);
  });
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
 * Read the active locale for number and date display.
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

/**
 * Format display numbers without changing serialized values.
 * @param value - The number to display.
 * @param options - Precision and other display options.
 * @returns The number in the selected ComfyUI locale.
 */
function formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat(selectedLocale(), options).format(value);
}

/**
 * Format a server timestamp for the selected ComfyUI locale.
 * @param value - A validated timestamp.
 * @returns The local date and time.
 */
export function formatDate(value: string): string {
  return new Date(value).toLocaleString(selectedLocale());
}

/**
 * Format a price in US dollars for the selected ComfyUI locale.
 * @param value - The amount in US dollars.
 * @returns The amount with its currency, to four significant digits.
 */
export function formatMoney(value: number): string {
  return formatNumber(value, { style: 'currency', currency: 'USD', maximumSignificantDigits: 4 });
}
