/** Local ComfyUI routes used by the browser interface. */
export const browserRoutes = {
  settings: {
    status: '/openrouter/v1/status',
    values: '/openrouter/v1/settings',
    credential: '/openrouter/v1/credential',
  },
  models: {
    read: '/openrouter/v1/models',
    refresh: '/openrouter/v1/models/refresh',
    rollback: '/openrouter/v1/models/rollback',
  },
} as const;
