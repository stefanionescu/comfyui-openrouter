import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import { browserRoutes } from '#web/routes.ts';
import { requestConfiguration } from '#web/settings/api.ts';
import type { Configuration } from '#web/settings/schema.ts';
import { LIMIT_LABELS, message, setText } from '#web/text.ts';

let current: SettingsDialog | undefined;

/** Edit server settings and cancel pending requests when the dialog closes. */
class SettingsDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly status = element('p', message('settings.reading'));

  private readonly source = element('p');

  private readonly reload = button(message('settings.reload'));

  private readonly key = element('input');

  private readonly keyFields = element('fieldset');

  private readonly limitFields = element('fieldset');

  private readonly inputs = new Map<string, HTMLInputElement>();

  private configuration: Configuration | undefined;

  /**
   * Build settings forms without contacting OpenRouter.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(private readonly fetcher: Fetcher) {
    this.dialog.className = 'openrouter-dialog';
    this.dialog.setAttribute('aria-labelledby', 'openrouter-settings-title');
    const heading = element('h2', message('settings.title'));
    heading.id = 'openrouter-settings-title';
    const close = button(message('close'));
    close.setAttribute('aria-label', message('settings.close'));
    close.addEventListener('click', this.dialog.close.bind(this.dialog, undefined));
    const header = element('header');
    header.append(heading, close);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.reload.addEventListener('click', () => this.updateSettings(message('settings.reread')));
    const footer = element('footer');
    footer.append(this.status, this.reload);
    this.dialog.append(
      header,
      this.credentials(),
      element('p', message('settings.keyNotice')),
      this.limits(),
      element('p', message('settings.timeNotice')),
      footer,
    );
    this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
  }

  /**
   * Build the private key form.
   * @returns The form for saving or clearing the server's key.
   */
  private credentials(): HTMLFormElement {
    const form = element('form');
    this.keyFields.disabled = true;
    const label = element('label', message('settings.credentialLabel'));
    this.key.type = 'password';
    this.key.autocomplete = 'off';
    this.key.spellcheck = false;
    this.key.required = true;
    label.append(this.key);
    const clear = button(message('settings.clearKey'));

    clear.addEventListener('click', () =>
      this.updateSettings(
        message('settings.keyCleared'),
        browserRoutes.settings.credential,
        'DELETE',
      ),
    );
    const actions = element('div');
    actions.className = 'openrouter-actions';
    actions.append(button(message('settings.saveKey'), 'submit'), clear);
    this.keyFields.append(
      element('legend', message('settings.credentials')),
      this.source,
      label,
      actions,
    );
    form.append(this.keyFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.updateSettings(message('settings.keySaved'), browserRoutes.settings.credential, 'PUT', {
        api_key: value,
      });
    });
    return form;
  }

  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  private limits(): HTMLFormElement {
    const form = element('form');
    this.limitFields.disabled = true;
    this.limitFields.append(element('legend', message('settings.limits')));
    this.limitFields.append(button(message('settings.saveLimits'), 'submit'));
    form.append(this.limitFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }

  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits.
   */
  private populateLimits(configuration: Configuration): void {
    this.limitFields.replaceChildren(element('legend', message('settings.limits')));
    const additionalLimits = element('details');
    additionalLimits.append(element('summary', message('settings.moreLimits')));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const label = element('label', LIMIT_LABELS.get(name) ?? name);
      const input = element('input');
      input.type = 'number';
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = '1';
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      const primary = name === 'request_timeout_seconds' || name === 'video_wait_minutes';
      (primary ? this.limitFields : additionalLimits).append(label);
    }
    this.limitFields.append(additionalLimits, button(message('settings.saveLimits'), 'submit'));
  }

  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  private saveLimits(configuration: Configuration): void {
    const changes = new Map<string, number>();
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== settings.get(name)) changes.set(name, input.valueAsNumber);
    }
    if (changes.size === 0) {
      setText(this.status, message('settings.noLimitChanges'));
      return;
    }
    this.updateSettings(message('settings.limitsSaved'), browserRoutes.settings.values, 'PATCH', {
      revision: configuration.revision,
      settings: Object.fromEntries(changes),
    });
  }

  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  private display(configuration: Configuration): void {
    this.configuration = configuration;
    if (this.inputs.size === 0) this.populateLimits(configuration);
    this.key.maxLength = configuration.credentialLimit;
    setText(
      this.source,
      {
        missing: message('settings.missingKey'),
        saved: message('settings.savedKey'),
        environment: message('settings.environmentKey'),
      }[configuration.credentialSource],
    );
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(settings.get(name));
    }
    if (!configuration.mutationAllowed) setText(this.status, message('settings.readOnly'));
  }

  /**
   * Keep settings requests serial and show the server's response.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   */
  private updateSettings(success: string, route?: string, method?: string, body?: unknown): void {
    if (route === browserRoutes.settings.credential) this.key.value = '';
    this.keyFields.disabled = this.limitFields.disabled = true;
    this.reload.disabled = true;
    setText(this.status, message('working'));
    void this.requestSettings(success, route, method, body);
  }

  /**
   * Apply the server response and restore editing after a settings request.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  private async requestSettings(
    success: string,
    route?: string,
    method?: string,
    body?: unknown,
  ): Promise<void> {
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body,
      );
      if (this.controller.signal.aborted) return;
      setText(this.status, success);
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message('settings.updateFailed'),
        );
    } finally {
      if (!this.controller.signal.aborted) {
        this.keyFields.disabled = this.limitFields.disabled = !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }

  /** Show the dialog and read local settings. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateSettings(message('settings.reread'));
  }

  /** Clear the key input, stop requests, and return focus to the caller. */
  private dispose(): void {
    this.key.value = '';
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one settings dialog at a time.
 * @param fetcher - ComfyUI's local API client.
 */
export function openSettings(fetcher: Fetcher): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new SettingsDialog(fetcher);
  current.show();
}
