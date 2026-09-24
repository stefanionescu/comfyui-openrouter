/** Local ComfyUI routes used by the browser interface. */
export const browserRoutes = {
  settings: {
    status: '/openrouter/v1/status',
    values: '/openrouter/v1/settings',
    credential: '/openrouter/v1/credential',
  },
} as const;
