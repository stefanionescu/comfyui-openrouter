/** Request deadlines and response size limits for the interface. */
export const browserLimits = {
  requestTimeoutMilliseconds: 10_000,
  discoveryTimeoutMilliseconds: 60_000,
  maxCalculatorSeconds: 3_600,
  maxCalculatorTokens: 100_000_000,
  maxTextCharacters: 200,
  maxErrorCharacters: 1_024,
  maxRetrievalTimeCharacters: 40,
  maxModelNodeIds: 100,
  maxModels: 4_096,
} as const;

/** Formats accepted from the local ComfyUI API. */
export const browserPatterns = {
  revision: /^[a-f0-9]{64}$/,
  documentation: /^https:\/\/openrouter\.ai\/~?[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._:-]*$/,
  settingName: /^[a-z][a-z_]+$/,
} as const;
