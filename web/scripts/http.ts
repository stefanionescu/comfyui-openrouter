import { api } from '../../scripts/api.js';
import { selectedLocale } from '#web/text.ts';

export type Fetcher = (route: string, options: RequestInit) => Promise<Response>;

/**
 * Send the selected ComfyUI language with local connector requests.
 * @param route - The local connector endpoint.
 * @param options - The request's existing method, headers, and body.
 * @returns The local ComfyUI response.
 */
export function requestLocal(route: string, options: RequestInit): Promise<Response> {
  const headers = new Headers(options.headers);
  headers.set('Accept-Language', selectedLocale());
  return api.fetchApi(route, { ...options, headers });
}
