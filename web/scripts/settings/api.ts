import type { Fetcher } from '#web/http.ts';
import { browserRoutes } from '#web/routes.ts';
import { browserLimits } from '#web/browser.ts';
import { parsePublicError } from '#web/schema.ts';
import { message, type MessageKey } from '#web/text.ts';
import { parseConfiguration, type Configuration } from '#web/settings/schema.ts';

/**
 * Read or change settings through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The settings dialog's request lifetime.
 * @param route - The local settings route.
 * @param method - The HTTP method.
 * @param body - The settings change, if any.
 * @returns The validated settings after the request.
 */
export async function requestConfiguration(
  fetcher: Fetcher,
  signal: AbortSignal,
  route: string = browserRoutes.settings.status,
  method: string = 'GET',
  body?: unknown,
): Promise<Configuration> {
  const options: RequestInit = {
    method,
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.requestTimeoutMilliseconds),
    ]),
    headers: { 'Content-Type': 'application/json', 'X-OpenRouter-Comfy': '1' },
  };
  if (body !== undefined) options.body = JSON.stringify(body);
  let response: Response;
  try {
    response = await fetcher(route, options);
  } catch {
    throw new Error(message('settings.unreachable'));
  }
  let document: unknown;
  try {
    document = await response.json();
  } catch {
    throw new Error(message('settings.unreadableResponse'));
  }
  if (!response.ok) {
    const failures = new Map<string, MessageKey>([
      ['GET', 'settings.readFailed'],
      ['DELETE', 'settings.removeFailed'],
    ]);
    throw new Error(
      parsePublicError(document) ?? message(failures.get(method) ?? 'settings.saveFailed'),
    );
  }
  return parseConfiguration(document);
}
