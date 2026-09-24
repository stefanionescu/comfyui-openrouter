import type { Model } from '#web/discovery/schema.ts';
import { formatMoney, message, type MessageKey } from '#web/text.ts';

/** What the person enters in the calculator; a box left empty counts as zero. */
export type Amounts = { inputTokens: number; outputTokens: number; videoSeconds: number };

type Unit = { label: MessageKey; scale: number; amount: keyof Amounts | undefined };

/** How each documented unit is shown, how many units one listed price covers, and what it multiplies. */
const UNITS = new Map<string, Unit>([
  ['input tokens', { label: 'pricing.perMillionInput', scale: 1_000_000, amount: 'inputTokens' }],
  [
    'output tokens',
    { label: 'pricing.perMillionOutput', scale: 1_000_000, amount: 'outputTokens' },
  ],
  [
    'input characters',
    { label: 'pricing.perMillionCharacters', scale: 1_000_000, amount: undefined },
  ],
  ['request', { label: 'pricing.perRequest', scale: 1, amount: undefined }],
  ['video second', { label: 'pricing.perVideoSecond', scale: 1, amount: 'videoSeconds' }],
]);

/**
 * Describe one listed price; a price without a documented unit shows its name and value only.
 * @param price - One validated price line.
 * @returns The line for display.
 */
function describePrice(price: Model['prices'][number]): string {
  const unit = price.unit === null ? undefined : UNITS.get(price.unit);
  if (unit === undefined) return `${price.label}: ${String(price.dollars)}`;
  const rate = message('pricing.rate', {
    price: formatMoney(price.dollars * unit.scale),
    unit: message(unit.label),
  });
  return `${price.label}: ${rate}`;
}

/**
 * Estimate a charge from the prices whose unit the calculator has an amount for.
 * Token prices add up; each video price is one choice of sound and resolution, so video gives a range.
 * @param model - A validated entry from the local model list.
 * @param amounts - The calculator's tokens and video seconds.
 * @returns The lowest and highest estimate in US dollars.
 */
function estimatePrice(model: Model, amounts: Amounts): [number, number] {
  const costs = model.prices.flatMap((price) => {
    const amount = price.unit === null ? undefined : UNITS.get(price.unit)?.amount;
    // eslint-disable-next-line security/detect-object-injection -- The key comes from the fixed unit table.
    return amount === undefined ? [] : [{ amount, dollars: price.dollars * amounts[amount] }];
  });
  const tokens = costs
    .filter((cost) => cost.amount !== 'videoSeconds')
    .reduce((total, cost) => total + cost.dollars, 0);
  const videos = costs.filter((cost) => cost.amount === 'videoSeconds').map((cost) => cost.dollars);
  if (videos.length === 0) return [tokens, tokens];
  return [tokens + Math.min(...videos), tokens + Math.max(...videos)];
}

/**
 * Show an estimate as one amount, or as a range when the video choices cost different amounts.
 * @param estimate - The lowest and highest estimate in US dollars.
 * @returns The amount for display.
 */
function formatEstimate(estimate: [number, number]): string {
  const [lowest, highest] = estimate;
  if (lowest === highest) return formatMoney(lowest);
  return message('pricing.range', { lowest: formatMoney(lowest), highest: formatMoney(highest) });
}

/**
 * Describe a model's listed prices and, for a current model, estimate a charge.
 * @param model - A validated entry from the local model list.
 * @param amounts - The calculator's tokens and video seconds, if any were entered.
 * @returns Price details and an optional estimate for display.
 */
export function formatPriceSummary(model: Model, amounts: Amounts | undefined): string[] {
  if (model.prices.length === 0) return [message('pricing.rateUnavailable')];
  const summary = model.prices.map(describePrice);
  if (!model.observed) summary.push(message('pricing.rateOutdated'));
  else if (amounts !== undefined)
    summary.push(
      message('pricing.calculation', { amount: formatEstimate(estimatePrice(model, amounts)) }),
    );
  return summary;
}
