import * as v from 'valibot';
import { message } from '#web/text.ts';
import { browserLimits, browserPatterns } from '#web/browser.ts';

const shortTextSchema = v.pipe(
  v.string(),
  v.minLength(1),
  v.maxLength(browserLimits.maxTextCharacters),
);

const retrievalTimeSchema = v.nullable(
  v.pipe(
    v.string(),
    v.minLength(1),
    v.maxLength(browserLimits.maxRetrievalTimeCharacters),
    v.check((value) => Number.isFinite(Date.parse(value))),
  ),
);

const priceSchema = v.pipe(
  v.object({
    label: shortTextSchema,
    usd: v.pipe(
      v.string(),
      v.maxLength(browserLimits.maxTextCharacters),
      v.check((value) => Number.isFinite(Number(value)) && Number(value) >= 0),
    ),
    unit: v.nullable(shortTextSchema),
  }),
  v.transform((price) => {
    return { label: price.label, dollars: Number(price.usd), unit: price.unit };
  }),
);

const modelSchema = v.pipe(
  v.object({
    id: shortTextSchema,
    name: shortTextSchema,
    nodes: v.pipe(v.array(shortTextSchema), v.maxLength(browserLimits.maxModelNodeIds)),
    observed: v.boolean(),
    documentation_url: v.pipe(v.string(), v.regex(browserPatterns.documentation)),
    prices: v.pipe(v.array(priceSchema), v.maxLength(browserLimits.maxModelNodeIds)),
  }),
  v.transform((model) => {
    return {
      id: model.id,
      name: model.name,
      nodes: model.nodes,
      observed: model.observed,
      documentationUrl: model.documentation_url,
      prices: model.prices,
    };
  }),
);

const automaticCheckSchema = v.pipe(
  v.object({
    enabled: v.boolean(),
    running: v.boolean(),
    interval_hours: v.pipe(v.number(), v.safeInteger(), v.minValue(1)),
    checked_at: retrievalTimeSchema,
    update_available: v.nullable(v.boolean()),
    error: v.nullable(
      v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters)),
    ),
  }),
  v.transform((check) => {
    return {
      intervalHours: check.interval_hours,
      checkedAt: check.checked_at,
      updateAvailable: check.update_available,
      error: check.error,
      enabled: check.enabled,
      running: check.running,
    };
  }),
);

const modelListSchema = v.pipe(
  v.object({
    revision: v.pipe(v.string(), v.regex(browserPatterns.revision)),
    retrieved_at: retrievalTimeSchema,
    is_bundled: v.boolean(),
    is_damaged: v.boolean(),
    models: v.pipe(v.array(modelSchema), v.minLength(1), v.maxLength(browserLimits.maxModels)),
    can_rollback: v.boolean(),
    mutation_allowed: v.boolean(),
    automatic_check: v.optional(automaticCheckSchema),
  }),
  v.check((document) => {
    const keys = new Set<string>();
    for (const model of document.models) {
      if (keys.has(model.id)) return false;
      keys.add(model.id);
    }
    return true;
  }),
  v.transform((document) => {
    return {
      revision: document.revision,
      retrievedAt: document.retrieved_at,
      isBundled: document.is_bundled,
      isDamaged: document.is_damaged,
      canRollback: document.can_rollback,
      mutationAllowed: document.mutation_allowed,
      models: document.models,
      ...(document.automatic_check === undefined
        ? {}
        : { automaticCheck: document.automatic_check }),
    };
  }),
);

export type Model = v.InferOutput<typeof modelSchema>;
export type ModelList = v.InferOutput<typeof modelListSchema>;

/**
 * Validate and transform a model list returned by the local server.
 * @param value - The untrusted JSON response.
 * @returns The browser model list.
 */
export function parseModelList(value: unknown): ModelList {
  const result = v.safeParse(modelListSchema, value);
  if (!result.success) throw new Error(message('models.invalidResponse'));
  return result.output;
}
