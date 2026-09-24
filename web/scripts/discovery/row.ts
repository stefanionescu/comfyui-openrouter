import { element } from '#web/dom.ts';
import { message } from '#web/text.ts';
import type { Model } from '#web/discovery/schema.ts';
import { formatPriceSummary, type Amounts } from '#web/discovery/pricing.ts';

/**
 * Show a model, the nodes that list it, its prices, and its page on OpenRouter.
 * @param model - A validated entry from the local model list.
 * @param amounts - Optional calculator amounts for a price estimate.
 * @returns One model list item.
 */
export function buildModelRow(model: Model, amounts: Amounts | undefined): HTMLElement {
  const row = element('li');
  row.append(element('h3', model.name), element('code', model.id));
  const support =
    model.nodes.length > 0
      ? message('models.nodesAvailable', { nodes: model.nodes.join(', ') })
      : message('models.nodeUnavailable');
  row.append(element('p', support));
  for (const detail of formatPriceSummary(model, amounts)) row.append(element('p', detail));
  const link = element('a', message('models.openGuide'));
  link.href = model.documentationUrl;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  row.append(link);
  return row;
}
