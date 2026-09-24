/** Request deadlines and response size limits for the interface. */
export const browserLimits = {
  requestTimeoutMilliseconds: 10_000,
  maxErrorCharacters: 1_024,
} as const;

/** Formats accepted from the local ComfyUI API. */
export const browserPatterns = {
  revision: /^[a-f0-9]{64}$/,
  settingName: /^[a-z][a-z_]+$/,
} as const;
