import fs from 'node:fs';

/**
 * Reads a JSON file.
 *
 * @param {string} filePath File path.
 * @param {string} description Source description.
 * @returns {unknown} Parsed JSON.
 */
export function readJsonFile(filePath, description) {
  try {
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Repository commands supply local paths; this reader accepts no network requests.
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`${description} could not be read: ${message}`, { cause: error });
  }
}

/**
 * Requires an array value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {unknown[]} The array value.
 */
export function requireArray(value, name) {
  if (!Array.isArray(value)) {
    throw new Error(`${name} must be an array`);
  }
  return value;
}

/**
 * Requires a plain item value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {Record<string, unknown>} The item value.
 */
export function requireDictionary(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${name} must be an item`);
  }
  return value;
}

/**
 * Requires a non-empty string value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {string} The string value.
 */
export function requireString(value, name) {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`${name} must be a non-empty string`);
  }
  return value;
}

/**
 * Reject missing and unknown configuration fields.
 * @param value - Configuration object to inspect.
 * @param required - Required field names.
 * @param optional - Optional field names.
 * @param context - Location of the configuration object.
 */
export function requireKeys(value, required, optional, context) {
  const allowed = new Set([...required, ...optional]);
  const missing = [];
  const unknown = [];
  for (const key of required) {
    if (!Object.hasOwn(value, key)) missing.push(key);
  }
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) unknown.push(key);
  }
  if (missing.length > 0 || unknown.length > 0) {
    throw new Error(
      `${context}: missing fields [${missing.join(', ')}]; unknown fields [${unknown.join(', ')}].`,
    );
  }
}
