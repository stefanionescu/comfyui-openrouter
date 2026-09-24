import * as v from 'valibot';
import { message } from '#web/text.ts';
import { browserPatterns } from '#web/browser.ts';

type SettingDefinition = { minimum: number; maximum: number };

export type Configuration = {
  revision: string;
  credentialSource: 'missing' | 'saved' | 'environment';
  credentialLimit: number;
  mutationAllowed: boolean;
  definitions: Record<string, SettingDefinition>;
  settings: Record<string, number>;
};

const unknownRecordSchema = v.record(v.string(), v.unknown());

const settingNameSchema = v.pipe(v.string(), v.regex(browserPatterns.settingName));

const settingDefinitionSchema = v.object({
  minimum: v.pipe(v.number(), v.safeInteger()),
  maximum: v.pipe(v.number(), v.safeInteger()),
});

const configurationDocumentSchema = v.object({
  revision: v.pipe(v.string(), v.regex(browserPatterns.revision)),
  mutation_allowed: v.boolean(),
  credential: v.object({
    source: v.picklist(['missing', 'saved', 'environment']),
  }),
  setting_ranges: v.unknown(),
  settings: unknownRecordSchema,
  credential_limit: v.unknown(),
});

const credentialLimitSchema = v.pipe(v.number(), v.safeInteger(), v.minValue(1));

/**
 * Read the settings fields and ranges supplied by the backend.
 * @param value - The untrusted settings definitions.
 * @returns The validated definitions indexed by setting name.
 */
function parseDefinitions(value: unknown): Configuration['definitions'] {
  const document = v.safeParse(unknownRecordSchema, value);
  if (!document.success) throw new Error(message('settings.invalidResponse'));
  const definitions = new Map<string, SettingDefinition>();
  for (const [name, raw] of Object.entries(document.output)) {
    const validName = v.safeParse(settingNameSchema, name);
    const definition = v.safeParse(settingDefinitionSchema, raw);
    if (
      !validName.success ||
      !definition.success ||
      definition.output.minimum > definition.output.maximum
    ) {
      throw new Error(message('settings.invalidDefinition'));
    }
    definitions.set(name, definition.output);
  }
  return Object.fromEntries(definitions);
}

/**
 * Validate and transform settings returned by the local server.
 * @param value - The untrusted JSON response.
 * @returns The browser settings without a saved credential value.
 */
export function parseConfiguration(value: unknown): Configuration {
  const result = v.safeParse(configurationDocumentSchema, value);
  if (!result.success) throw new Error(message('settings.invalidResponse'));
  const document = result.output;
  const definitions = parseDefinitions(document.setting_ranges);
  const credentialLimit = v.safeParse(credentialLimitSchema, document.credential_limit);
  if (!credentialLimit.success) throw new Error(message('settings.invalidResponse'));
  const settings = new Map(Object.entries(document.settings));
  for (const [name, definition] of Object.entries(definitions)) {
    const setting = v.safeParse(
      v.pipe(
        v.number(),
        v.safeInteger(),
        v.minValue(definition.minimum),
        v.maxValue(definition.maximum),
      ),
      settings.get(name),
    );
    if (!setting.success) throw new Error(message('settings.invalidLimit'));
  }
  return {
    revision: document.revision,
    credentialSource: document.credential.source,
    credentialLimit: credentialLimit.output,
    mutationAllowed: document.mutation_allowed,
    definitions,
    settings: document.settings as Configuration['settings'],
  };
}
