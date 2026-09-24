import type { Fetcher } from '#web/http.ts';
import { browserRoutes } from '#web/routes.ts';
import { browserLimits } from '#web/browser.ts';
import { parsePublicError } from '#web/schema.ts';
import { message, formatDate } from '#web/text.ts';
import { parseModelList, type ModelList } from '#web/discovery/schema.ts';

type ModelAction = 'read' | 'refresh' | 'rollback';

function modelRoute(action: ModelAction): string {
  if (action === 'read') return browserRoutes.models.read;
  if (action === 'refresh') return browserRoutes.models.refresh;
  return browserRoutes.models.rollback;
}

/**
 * Describe where the model list in use came from.
 * @param list - The validated local model list.
 * @returns A readable date, or the action needed to load current models and prices.
 */
export function metadataStatus(list: ModelList): string {
  if (list.isDamaged) return message('models.damaged');
  if (list.isBundled || list.retrievedAt === null) return message('models.installedList');
  return message('models.lastRefresh', { date: formatDate(list.retrievedAt) });
}

/**
 * Read or update the model list through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The dialog's request lifetime.
 * @param action - Read, refresh public sources, or restore the previous list.
 * @param revision - The currently displayed revision required for rollback.
 * @returns The validated model list.
 */
export async function requestModels(
  fetcher: Fetcher,
  signal: AbortSignal,
  action: ModelAction,
  revision?: string,
): Promise<ModelList> {
  const options: RequestInit = {
    method: action === 'read' ? 'GET' : 'POST',
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.discoveryTimeoutMilliseconds),
    ]),
    headers: { 'Content-Type': 'application/json', 'X-OpenRouter-Comfy': '1' },
  };
  if (action === 'rollback') options.body = JSON.stringify({ revision });
  let response: Response;
  try {
    response = await fetcher(modelRoute(action), options);
  } catch {
    throw new Error(message('models.unreachable'));
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new Error(message('models.invalidResponse'));
  }
  if (!response.ok) {
    throw new Error(parsePublicError(body) ?? message('models.requestFailed'));
  }
  return parseModelList(body);
}
