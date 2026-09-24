import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import { browserLimits } from '#web/browser.ts';
import { buildModelRow } from '#web/discovery/row.ts';
import type { Amounts } from '#web/discovery/pricing.ts';
import type { ModelList } from '#web/discovery/schema.ts';
import { formatDate, message, setText } from '#web/text.ts';
import { requestModels, metadataStatus } from '#web/discovery/api.ts';

let current: ModelDialog | undefined;

/**
 * Explain the most recent automatic model check.
 * @param check - The scheduler's report, if available.
 * @returns A status message for the model sources section.
 */
function automaticStatus(check: ModelList['automaticCheck']): string {
  if (!check) return '';
  if (!check.enabled) return message('models.checksOff');
  if (check.running) return message('models.checkRunning');
  if (check.error) return check.error;
  if (check.updateAvailable === true) return message('models.listChanged');
  if (check.checkedAt)
    return message('models.checkSchedule', {
      date: formatDate(check.checkedAt),
      hours: check.intervalHours,
    });
  return message('models.checkDue');
}

/** Browse the saved model list, its prices, and the nodes that list each model. */
class ModelDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly search = element('input');

  private readonly inputTokens = element('input');

  private readonly outputTokens = element('input');

  private readonly videoSeconds = element('input');

  private readonly refresh = button(message('models.refresh'));

  private readonly rollback = button(message('models.restore'));

  private readonly status = element('p', message('models.readingLocal'));

  private readonly checked = element('p');

  private readonly automatic = element('p');

  private readonly count = element('p');

  private readonly list = element('ul');

  private modelList: ModelList | undefined;

  /**
   * Build the searchable model browser.
   * @param fetcher - ComfyUI's local API client.
   * @param reloadNodes - Reads ComfyUI's node definitions again, so the dropdowns show a changed list.
   */
  constructor(
    private readonly fetcher: Fetcher,
    private readonly reloadNodes: () => void,
  ) {
    this.dialog.className = 'openrouter-dialog openrouter-models';
    this.dialog.setAttribute('aria-labelledby', 'openrouter-models-title');
    const heading = element('h2', message('models.title'));
    heading.id = 'openrouter-models-title';
    const close = button(message('close'));
    close.setAttribute('aria-label', message('models.close'));
    close.addEventListener('click', this.dialog.close.bind(this.dialog, undefined));
    const header = element('header');
    header.append(heading, close);
    const searchLabel = element('label', message('models.search'));
    this.search.type = 'search';
    this.search.setAttribute('placeholder', message('models.searchPlaceholder'));
    searchLabel.append(this.search);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.list.setAttribute('aria-label', message('models.title'));
    const sources = element('details');
    sources.append(
      element('summary', message('models.sources')),
      this.checked,
      this.automatic,
      element('p', message('models.refreshNotice')),
    );
    this.dialog.append(
      header,
      this.actions(),
      this.status,
      searchLabel,
      this.count,
      this.calculation(),
      sources,
      this.list,
    );
    for (const input of [this.search, this.inputTokens, this.outputTokens, this.videoSeconds]) {
      input.addEventListener('input', this.updateView.bind(this));
    }
    this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
  }

  /**
   * Build actions to refresh or restore the model list.
   * @returns The model browser actions.
   */
  private actions(): HTMLElement {
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener('click', this.updateModels.bind(this, 'refresh'));
    this.rollback.addEventListener('click', this.updateModels.bind(this, 'rollback'));
    const actions = element('div');
    actions.className = 'openrouter-actions';
    actions.append(this.refresh, this.rollback);
    return actions;
  }

  /**
   * Build the optional price calculation: input tokens, output tokens, and video seconds.
   * @returns The collapsed calculation controls.
   */
  private calculation(): HTMLElement {
    const calculation = element('details');
    calculation.append(element('summary', message('pricing.calculate')));
    for (const [input, text, maximum, step] of [
      [this.inputTokens, message('pricing.inputTokens'), browserLimits.maxCalculatorTokens, '1'],
      [this.outputTokens, message('pricing.outputTokens'), browserLimits.maxCalculatorTokens, '1'],
      [
        this.videoSeconds,
        message('pricing.videoSeconds'),
        browserLimits.maxCalculatorSeconds,
        'any',
      ],
    ] as const) {
      const label = element('label', text);
      input.type = 'number';
      input.min = '0';
      input.max = String(maximum);
      input.step = step;
      label.append(input);
      calculation.append(label);
    }
    calculation.append(element('p', message('pricing.totalTimeNotice')));
    return calculation;
  }

  /**
   * Read the calculator's amounts; nothing to estimate until a box holds a valid number.
   * @returns The entered amounts, with empty boxes as zero, or nothing when none is entered.
   */
  private readAmounts(): Amounts | undefined {
    const boxes = [this.inputTokens, this.outputTokens, this.videoSeconds];
    if (boxes.every((box) => box.value === '') || boxes.some((box) => !box.validity.valid))
      return undefined;
    const [inputTokens, outputTokens, videoSeconds] = boxes.map((box) =>
      box.value === '' ? 0 : box.valueAsNumber,
    );
    return {
      inputTokens: inputTokens ?? 0,
      outputTokens: outputTokens ?? 0,
      videoSeconds: videoSeconds ?? 0,
    };
  }

  /** Update matching models and calculations from the current controls. */
  private updateView(): void {
    const query = this.search.value.trim().toLowerCase();
    const amounts = this.readAmounts();
    const rows = document.createDocumentFragment();
    for (const model of this.modelList?.models ?? []) {
      const label = `${model.id} ${model.name} ${model.nodes.join(' ')}`;
      if (label.toLowerCase().includes(query)) rows.appendChild(buildModelRow(model, amounts));
    }
    const visible = rows.childElementCount;
    this.list.replaceChildren();
    this.list.appendChild(rows);
    setText(
      this.count,
      message('models.count', {
        visible,
        total: this.modelList?.models.length ?? 0,
      }),
    );
  }

  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   */
  private updateModels(action: 'read' | 'refresh' | 'rollback'): void {
    this.refresh.disabled = this.rollback.disabled = true;
    setText(
      this.status,
      action === 'refresh' ? message('models.checking') : message('models.reading'),
    );
    void this.requestModels(action);
  }

  /**
   * Apply a model-list response while the dialog is open.
   * @param action - The requested list operation.
   * @returns When the request and action cleanup finish.
   */
  private async requestModels(action: 'read' | 'refresh' | 'rollback'): Promise<void> {
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action,
        this.modelList?.revision,
      );
      if (this.controller.signal.aborted) return;
      this.displayModels(next, action);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(this.status, error instanceof Error ? error.message : message('models.readFailed'));
    } finally {
      this.restoreActions();
    }
  }

  /**
   * Display a model list and the outcome of its requested operation.
   * @param next - The validated local model list.
   * @param action - The completed list operation.
   */
  private displayModels(next: ModelList, action: 'read' | 'refresh' | 'rollback'): void {
    this.modelList = next;
    setText(this.checked, metadataStatus(next));
    setText(this.automatic, automaticStatus(next.automaticCheck));
    let status = message('models.reread');
    if (action === 'refresh') status = message('models.refreshed');
    if (action === 'rollback') status = message('models.restored');
    // Every model dropdown is built from this list, so the node definitions are read again.
    if (action !== 'read') {
      this.reloadNodes();
      status = `${status} ${message('models.reloadNodes')}`;
    }
    setText(this.status, status);
    this.updateView();
  }

  /** Re-enable allowed list changes after the current request finishes. */
  private restoreActions(): void {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.modelList?.mutationAllowed;
    this.rollback.disabled = !this.modelList?.mutationAllowed || !this.modelList.canRollback;
  }

  /** Show the dialog and read the local model list. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateModels('read');
  }

  /** Stop pending requests and return focus to the caller. */
  private dispose(): void {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one model browser at a time.
 * @param fetcher - ComfyUI's local API client.
 * @param reloadNodes - Reads ComfyUI's node definitions again after the list changes.
 */
export function openModels(fetcher: Fetcher, reloadNodes: () => void): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, reloadNodes);
  current.show();
}
