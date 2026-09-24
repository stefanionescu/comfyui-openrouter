// web/scripts/text.ts
import { app } from "../../scripts/app.js";
var TEXT = {
  close: "Close",
  settings: {
    moreLimits: "Advanced limits",
    clearKey: "Clear Saved Key",
    close: "Close OpenRouter settings",
    credentialLabel: "OpenRouter API key",
    credentials: "Credentials",
    environmentKey: "The server's OPENROUTER_API_KEY environment variable is active.",
    invalidDefinition: "ComfyUI returned an invalid OpenRouter setting definition.",
    invalidLimit: "ComfyUI returned an invalid OpenRouter limit.",
    invalidResponse: "ComfyUI returned an invalid OpenRouter settings response.",
    keyCleared: "Saved key cleared. Any environment key remains active.",
    keyNotice: "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked here.",
    keySaved: "Key saved on this server. OpenRouter checks it on the next request.",
    limits: "Request limits",
    limitsSaved: "Limits saved. They apply to new requests.",
    reread: "Local settings loaded.",
    reading: "Loading local settings...",
    missingKey: "No OpenRouter key is configured.",
    noLimitChanges: "No limit changes to save.",
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: "Reload Settings",
    saveFailed: "ComfyUI could not save OpenRouter settings.",
    saveKey: "Save Key",
    saveLimits: "Save Limits",
    savedKey: "A saved key is configured on this server.",
    timeNotice: "The request timeout applies to each request. The maximum video wait applies to a whole video job.",
    title: "OpenRouter Settings",
    unreachable: "Cannot reach OpenRouter settings. Check ComfyUI and try again.",
    unreadableResponse: "ComfyUI returned an unreadable OpenRouter settings response.",
    updateFailed: "OpenRouter settings could not be saved.",
    readFailed: "ComfyUI could not read OpenRouter settings.",
    removeFailed: "ComfyUI could not clear the saved OpenRouter key.",
    menu: "OpenRouter settings"
  },
  working: "Working..."
};
var LIMIT_LABELS = /* @__PURE__ */ new Map([
  ["max_download_megabytes", "maximum download size (MiB)"],
  ["max_upload_megabytes", "maximum upload size (MiB)"],
  ["parallel_requests", "parallel requests"],
  ["request_timeout_seconds", "request timeout (seconds)"],
  ["video_check_interval_seconds", "video check interval (seconds)"],
  ["video_retry_delay_minutes", "video retry delay (minutes)"],
  ["video_wait_minutes", "maximum video wait (minutes)"]
]);
function message(key) {
  let value = TEXT;
  for (const part of key.split(".")) {
    value = value[part];
  }
  return String(value);
}
function setText(target, content) {
  target.replaceChildren(document.createTextNode(content));
}
function selectedLocale() {
  const value = app.extensionManager.setting.get("Comfy.Locale");
  try {
    return Intl.getCanonicalLocales(typeof value === "string" ? value.replaceAll("_", "-") : "en")[0] ?? "en";
  } catch {
    return "en";
  }
}

// web/scripts/extension.ts
import { app as app2 } from "../../scripts/app.js";

// web/scripts/http.ts
import { api } from "../../scripts/api.js";
function requestLocal(route, options) {
  const headers = new Headers(options.headers);
  headers.set("Accept-Language", selectedLocale());
  return api.fetchApi(route, { ...options, headers });
}

// web/scripts/nodes.ts
var dynamicControlInputs = /* @__PURE__ */ new Map([
  ["OpenRouterDecisionAddQuestion", ["answer_type"]]
]);

// web/scripts/dom.ts
function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== void 0) node.appendChild(document.createTextNode(text));
  return node;
}
function button(text, type = "button") {
  const node = element("button", text);
  node.type = type;
  return node;
}

// web/scripts/routes.ts
var browserRoutes = {
  settings: {
    status: "/openrouter/v1/status",
    values: "/openrouter/v1/settings",
    credential: "/openrouter/v1/credential"
  }
};

// web/scripts/browser.ts
var browserLimits = {
  requestTimeoutMilliseconds: 1e4,
  maxErrorCharacters: 1024
};
var browserPatterns = {
  revision: /^[a-f0-9]{64}$/,
  settingName: /^[a-z][a-z_]+$/
};

// node_modules/valibot/dist/index.mjs
var store$4;
var DEFAULT_CONFIG = {
  lang: void 0,
  message: void 0,
  abortEarly: void 0,
  abortPipeEarly: void 0
};
// @__NO_SIDE_EFFECTS__
function getGlobalConfig(config$1) {
  if (!config$1 && !store$4) return DEFAULT_CONFIG;
  return {
    lang: config$1?.lang ?? store$4?.lang,
    message: config$1?.message,
    abortEarly: config$1?.abortEarly ?? store$4?.abortEarly,
    abortPipeEarly: config$1?.abortPipeEarly ?? store$4?.abortPipeEarly
  };
}
var store$3;
// @__NO_SIDE_EFFECTS__
function getGlobalMessage(lang) {
  return store$3?.get(lang);
}
var store$2;
// @__NO_SIDE_EFFECTS__
function getSchemaMessage(lang) {
  return store$2?.get(lang);
}
var store$1;
// @__NO_SIDE_EFFECTS__
function getSpecificMessage(reference, lang) {
  return store$1?.get(reference)?.get(lang);
}
// @__NO_SIDE_EFFECTS__
function _stringify(input) {
  const type = typeof input;
  if (type === "string") return `"${input}"`;
  if (type === "number" || type === "bigint" || type === "boolean") return `${input}`;
  if (type === "object" || type === "function") return (input && Object.getPrototypeOf(input)?.constructor?.name) ?? "null";
  return type;
}
function _addIssue(context, label, dataset, config$1, other) {
  const input = other && "input" in other ? other.input : dataset.value;
  const expected = other?.expected ?? context.expects ?? null;
  const received = other?.received ?? /* @__PURE__ */ _stringify(input);
  const issue = {
    kind: context.kind,
    type: context.type,
    input,
    expected,
    received,
    message: `Invalid ${label}: ${expected ? `Expected ${expected} but r` : "R"}eceived ${received}`,
    requirement: context.requirement,
    path: other?.path,
    issues: other?.issues,
    lang: config$1.lang,
    abortEarly: config$1.abortEarly,
    abortPipeEarly: config$1.abortPipeEarly
  };
  const isSchema = context.kind === "schema";
  const message$1 = other?.message ?? context.message ?? /* @__PURE__ */ getSpecificMessage(context.reference, issue.lang) ?? (isSchema ? /* @__PURE__ */ getSchemaMessage(issue.lang) : null) ?? config$1.message ?? /* @__PURE__ */ getGlobalMessage(issue.lang);
  if (message$1 !== void 0) issue.message = typeof message$1 === "function" ? message$1(issue) : message$1;
  if (isSchema) dataset.typed = false;
  if (dataset.issues) dataset.issues.push(issue);
  else dataset.issues = [issue];
}
// @__NO_SIDE_EFFECTS__
function _isValidObjectKey(object$1, key) {
  return Object.prototype.hasOwnProperty.call(object$1, key) && key !== "__proto__" && key !== "prototype" && key !== "constructor";
}
// @__NO_SIDE_EFFECTS__
function _joinExpects(values$1, separator) {
  const list = [...new Set(values$1)];
  if (list.length > 1) return `(${list.join(` ${separator} `)})`;
  return list[0] ?? "never";
}
function _standardSchema(schema) {
  schema["~standard"] = {
    version: 1,
    vendor: "valibot",
    validate: (value$1) => schema["~run"]({ value: value$1 }, /* @__PURE__ */ getGlobalConfig())
  };
  return schema;
}
// @__NO_SIDE_EFFECTS__
function maxLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_length",
    reference: maxLength,
    async: false,
    expects: `<=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length > this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function maxValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_value",
    reference: maxValue,
    async: false,
    expects: `<=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value <= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_length",
    reference: minLength,
    async: false,
    expects: `>=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length < this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_value",
    reference: minValue,
    async: false,
    expects: `>=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value >= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function regex(requirement, message$1) {
  return {
    kind: "validation",
    type: "regex",
    reference: regex,
    async: false,
    expects: `${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement.test(dataset.value)) _addIssue(this, "format", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function safeInteger(message$1) {
  return {
    kind: "validation",
    type: "safe_integer",
    reference: safeInteger,
    async: false,
    expects: null,
    requirement: Number.isSafeInteger,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "safe integer", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function getFallback(schema, dataset, config$1) {
  return typeof schema.fallback === "function" ? schema.fallback(dataset, config$1) : schema.fallback;
}
// @__NO_SIDE_EFFECTS__
function getDefault(schema, dataset, config$1) {
  return typeof schema.default === "function" ? schema.default(dataset, config$1) : schema.default;
}
// @__NO_SIDE_EFFECTS__
function boolean(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "boolean",
    reference: boolean,
    expects: "boolean",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "boolean") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function number(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "number",
    reference: number,
    expects: "number",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "number" && !isNaN(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function object(entries$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "object",
    reference: object,
    expects: "Object",
    async: false,
    entries: entries$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const key in this.entries) {
          const valueSchema = this.entries[key];
          if (key in input || (valueSchema.type === "exact_optional" || valueSchema.type === "optional" || valueSchema.type === "nullish") && valueSchema.default !== void 0) {
            const value$1 = key in input ? input[key] : /* @__PURE__ */ getDefault(valueSchema);
            const valueDataset = valueSchema["~run"]({ value: value$1 }, config$1);
            if (valueDataset.issues) {
              const pathItem = {
                type: "object",
                origin: "value",
                input,
                key,
                value: value$1
              };
              for (const issue of valueDataset.issues) {
                if (issue.path) issue.path.unshift(pathItem);
                else issue.path = [pathItem];
                dataset.issues?.push(issue);
              }
              if (!dataset.issues) dataset.issues = valueDataset.issues;
              if (config$1.abortEarly) {
                dataset.typed = false;
                break;
              }
            }
            if (!valueDataset.typed) dataset.typed = false;
            dataset.value[key] = valueDataset.value;
          } else if (valueSchema.fallback !== void 0) dataset.value[key] = /* @__PURE__ */ getFallback(valueSchema);
          else if (valueSchema.type !== "exact_optional" && valueSchema.type !== "optional" && valueSchema.type !== "nullish") {
            _addIssue(this, "key", dataset, config$1, {
              input: void 0,
              expected: `"${key}"`,
              path: [{
                type: "object",
                origin: "key",
                input,
                key,
                value: input[key]
              }]
            });
            if (config$1.abortEarly) break;
          }
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function optional(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "optional",
    reference: optional,
    expects: `(${wrapped.expects} | undefined)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === void 0) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === void 0) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
    }
  });
}
// @__NO_SIDE_EFFECTS__
function picklist(options, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "picklist",
    reference: picklist,
    expects: /* @__PURE__ */ _joinExpects(options.map(_stringify), "|"),
    async: false,
    options,
    message: message$1,
    "~run"(dataset, config$1) {
      if (this.options.includes(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function record(key, value$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "record",
    reference: record,
    expects: "Object",
    async: false,
    key,
    value: value$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const entryKey in input) if (/* @__PURE__ */ _isValidObjectKey(input, entryKey)) {
          const entryValue = input[entryKey];
          const keyDataset = this.key["~run"]({ value: entryKey }, config$1);
          if (keyDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "key",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of keyDataset.issues) {
              issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = keyDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          const valueDataset = this.value["~run"]({ value: entryValue }, config$1);
          if (valueDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "value",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of valueDataset.issues) {
              if (issue.path) issue.path.unshift(pathItem);
              else issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = valueDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          if (!keyDataset.typed || !valueDataset.typed) dataset.typed = false;
          if (keyDataset.typed) dataset.value[keyDataset.value] = valueDataset.value;
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function string(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "string",
    reference: string,
    expects: "string",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "string") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function unknown() {
  return _standardSchema({
    kind: "schema",
    type: "unknown",
    reference: unknown,
    expects: "unknown",
    async: false,
    "~run"(dataset) {
      dataset.typed = true;
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function pipe(...pipe$1) {
  return _standardSchema({
    ...pipe$1[0],
    pipe: pipe$1,
    "~run"(dataset, config$1) {
      for (const item of pipe$1) if (item.kind !== "metadata") {
        if (dataset.issues && (item.kind === "schema" || item.kind === "transformation")) {
          dataset.typed = false;
          break;
        }
        if (!dataset.issues || !config$1.abortEarly && !config$1.abortPipeEarly) dataset = item["~run"](dataset, config$1);
      }
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function safeParse(schema, input, config$1) {
  const dataset = schema["~run"]({ value: input }, /* @__PURE__ */ getGlobalConfig(config$1));
  return {
    typed: dataset.typed,
    success: !dataset.issues,
    output: dataset.value,
    issues: dataset.issues
  };
}

// web/scripts/schema.ts
var publicErrorSchema = object({
  error: optional(
    pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
  )
});
function parsePublicError(value) {
  const result = safeParse(publicErrorSchema, value);
  if (!result.success) return void 0;
  return result.output.error;
}

// web/scripts/settings/schema.ts
var unknownRecordSchema = record(string(), unknown());
var settingNameSchema = pipe(string(), regex(browserPatterns.settingName));
var settingDefinitionSchema = object({
  minimum: pipe(number(), safeInteger()),
  maximum: pipe(number(), safeInteger())
});
var configurationDocumentSchema = object({
  revision: pipe(string(), regex(browserPatterns.revision)),
  mutation_allowed: boolean(),
  credential: object({
    source: picklist(["missing", "saved", "environment"])
  }),
  setting_ranges: unknown(),
  settings: unknownRecordSchema,
  credential_limit: unknown()
});
var credentialLimitSchema = pipe(number(), safeInteger(), minValue(1));
function parseDefinitions(value) {
  const document2 = safeParse(unknownRecordSchema, value);
  if (!document2.success) throw new Error(message("settings.invalidResponse"));
  const definitions = /* @__PURE__ */ new Map();
  for (const [name, raw] of Object.entries(document2.output)) {
    const validName = safeParse(settingNameSchema, name);
    const definition = safeParse(settingDefinitionSchema, raw);
    if (!validName.success || !definition.success || definition.output.minimum > definition.output.maximum) {
      throw new Error(message("settings.invalidDefinition"));
    }
    definitions.set(name, definition.output);
  }
  return Object.fromEntries(definitions);
}
function parseConfiguration(value) {
  const result = safeParse(configurationDocumentSchema, value);
  if (!result.success) throw new Error(message("settings.invalidResponse"));
  const document2 = result.output;
  const definitions = parseDefinitions(document2.setting_ranges);
  const credentialLimit = safeParse(credentialLimitSchema, document2.credential_limit);
  if (!credentialLimit.success) throw new Error(message("settings.invalidResponse"));
  const settings = new Map(Object.entries(document2.settings));
  for (const [name, definition] of Object.entries(definitions)) {
    const setting = safeParse(
      pipe(
        number(),
        safeInteger(),
        minValue(definition.minimum),
        maxValue(definition.maximum)
      ),
      settings.get(name)
    );
    if (!setting.success) throw new Error(message("settings.invalidLimit"));
  }
  return {
    revision: document2.revision,
    credentialSource: document2.credential.source,
    credentialLimit: credentialLimit.output,
    mutationAllowed: document2.mutation_allowed,
    definitions,
    settings: document2.settings
  };
}

// web/scripts/settings/api.ts
async function requestConfiguration(fetcher, signal, route = browserRoutes.settings.status, method = "GET", body) {
  const options = {
    method,
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.requestTimeoutMilliseconds)
    ]),
    headers: { "Content-Type": "application/json", "X-OpenRouter-Comfy": "1" }
  };
  if (body !== void 0) options.body = JSON.stringify(body);
  let response;
  try {
    response = await fetcher(route, options);
  } catch {
    throw new Error(message("settings.unreachable"));
  }
  let document2;
  try {
    document2 = await response.json();
  } catch {
    throw new Error(message("settings.unreadableResponse"));
  }
  if (!response.ok) {
    const failures = /* @__PURE__ */ new Map([
      ["GET", "settings.readFailed"],
      ["DELETE", "settings.removeFailed"]
    ]);
    throw new Error(
      parsePublicError(document2) ?? message(failures.get(method) ?? "settings.saveFailed")
    );
  }
  return parseConfiguration(document2);
}

// web/scripts/settings/dialog.ts
var current;
var SettingsDialog = class {
  /**
   * Build settings forms without contacting OpenRouter.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(fetcher) {
    this.fetcher = fetcher;
    this.dialog.className = "openrouter-dialog";
    this.dialog.setAttribute("aria-labelledby", "openrouter-settings-title");
    const heading = element("h2", message("settings.title"));
    heading.id = "openrouter-settings-title";
    const close = button(message("close"));
    close.setAttribute("aria-label", message("settings.close"));
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener("click", () => this.updateSettings(message("settings.reread")));
    const footer = element("footer");
    footer.append(this.status, this.reload);
    this.dialog.append(
      header,
      this.credentials(),
      element("p", message("settings.keyNotice")),
      this.limits(),
      element("p", message("settings.timeNotice")),
      footer
    );
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
  }
  fetcher;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  status = element("p", message("settings.reading"));
  source = element("p");
  reload = button(message("settings.reload"));
  key = element("input");
  keyFields = element("fieldset");
  limitFields = element("fieldset");
  inputs = /* @__PURE__ */ new Map();
  configuration;
  /**
   * Build the private key form.
   * @returns The form for saving or clearing the server's key.
   */
  credentials() {
    const form = element("form");
    this.keyFields.disabled = true;
    const label = element("label", message("settings.credentialLabel"));
    this.key.type = "password";
    this.key.autocomplete = "off";
    this.key.spellcheck = false;
    this.key.required = true;
    label.append(this.key);
    const clear = button(message("settings.clearKey"));
    clear.addEventListener(
      "click",
      () => this.updateSettings(
        message("settings.keyCleared"),
        browserRoutes.settings.credential,
        "DELETE"
      )
    );
    const actions = element("div");
    actions.className = "openrouter-actions";
    actions.append(button(message("settings.saveKey"), "submit"), clear);
    this.keyFields.append(
      element("legend", message("settings.credentials")),
      this.source,
      label,
      actions
    );
    form.append(this.keyFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.updateSettings(message("settings.keySaved"), browserRoutes.settings.credential, "PUT", {
        api_key: value
      });
    });
    return form;
  }
  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  limits() {
    const form = element("form");
    this.limitFields.disabled = true;
    this.limitFields.append(element("legend", message("settings.limits")));
    this.limitFields.append(button(message("settings.saveLimits"), "submit"));
    form.append(this.limitFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }
  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits.
   */
  populateLimits(configuration) {
    this.limitFields.replaceChildren(element("legend", message("settings.limits")));
    const additionalLimits = element("details");
    additionalLimits.append(element("summary", message("settings.moreLimits")));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const label = element("label", LIMIT_LABELS.get(name) ?? name);
      const input = element("input");
      input.type = "number";
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = "1";
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      const primary = name === "request_timeout_seconds" || name === "video_wait_minutes";
      (primary ? this.limitFields : additionalLimits).append(label);
    }
    this.limitFields.append(additionalLimits, button(message("settings.saveLimits"), "submit"));
  }
  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  saveLimits(configuration) {
    const changes = /* @__PURE__ */ new Map();
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== settings.get(name)) changes.set(name, input.valueAsNumber);
    }
    if (changes.size === 0) {
      setText(this.status, message("settings.noLimitChanges"));
      return;
    }
    this.updateSettings(message("settings.limitsSaved"), browserRoutes.settings.values, "PATCH", {
      revision: configuration.revision,
      settings: Object.fromEntries(changes)
    });
  }
  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  display(configuration) {
    this.configuration = configuration;
    if (this.inputs.size === 0) this.populateLimits(configuration);
    this.key.maxLength = configuration.credentialLimit;
    setText(
      this.source,
      {
        missing: message("settings.missingKey"),
        saved: message("settings.savedKey"),
        environment: message("settings.environmentKey")
      }[configuration.credentialSource]
    );
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(settings.get(name));
    }
    if (!configuration.mutationAllowed) setText(this.status, message("settings.readOnly"));
  }
  /**
   * Keep settings requests serial and show the server's response.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   */
  updateSettings(success, route, method, body) {
    if (route === browserRoutes.settings.credential) this.key.value = "";
    this.keyFields.disabled = this.limitFields.disabled = true;
    this.reload.disabled = true;
    setText(this.status, message("working"));
    void this.requestSettings(success, route, method, body);
  }
  /**
   * Apply the server response and restore editing after a settings request.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  async requestSettings(success, route, method, body) {
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body
      );
      if (this.controller.signal.aborted) return;
      setText(this.status, success);
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message("settings.updateFailed")
        );
    } finally {
      if (!this.controller.signal.aborted) {
        this.keyFields.disabled = this.limitFields.disabled = !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }
  /** Show the dialog and read local settings. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateSettings(message("settings.reread"));
  }
  /** Clear the key input, stop requests, and return focus to the caller. */
  dispose() {
    this.key.value = "";
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openSettings(fetcher) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new SettingsDialog(fetcher);
  current.show();
}

// web/scripts/widgets.ts
function findWidget(canvasNode, name) {
  return canvasNode.widgets?.find((widget) => widget.name === name);
}
function chainCallback(widget, after) {
  const previous = widget.callback?.bind(widget);
  widget.callback = function(...args) {
    previous?.apply(this, args);
    after();
  };
}

// web/scripts/extension.ts
var controlRestorers = /* @__PURE__ */ new WeakMap();
var childLabels = /* @__PURE__ */ new Map();
function listOptionLabels(name, option) {
  return Object.entries(option.inputs.required ?? {}).flatMap(
    ([child, [, spec]]) => spec.display_name ? [[`${option.key}/${name}.${child}`, spec.display_name]] : []
  );
}
function readChildLabels(definitions) {
  for (const [nodeClass, definition] of Object.entries(definitions)) {
    const controls = dynamicControlInputs.get(nodeClass) ?? [];
    const labels = new Map(
      Object.entries(definition.input?.required ?? {}).filter(([name]) => controls.includes(name)).flatMap(
        ([name, [, spec]]) => (spec.options ?? []).flatMap((option) => listOptionLabels(name, option))
      )
    );
    if (labels.size) childLabels.set(nodeClass, labels);
  }
}
function addNodeControls(canvasNode) {
  const restorers = [];
  for (const name of dynamicControlInputs.get(canvasNode.comfyClass ?? "") ?? []) {
    const widget = findWidget(canvasNode, name);
    if (widget) restorers.push(watchControl(canvasNode, widget));
  }
  controlRestorers.set(canvasNode, restorers);
}
function watchControl(canvasNode, widget) {
  const restoreValues = preserveControlValues(canvasNode, widget);
  chainCallback(widget, () => {
    restoreValues(true);
    const canvas = app2.canvas;
    canvas.onSelectionChange?.(canvas.selected_nodes);
  });
  return restoreValues;
}
function preserveControlValues(canvasNode, widget) {
  const restoredWidgets = /* @__PURE__ */ new WeakSet();
  const labels = childLabels.get(canvasNode.comfyClass ?? "");
  const restoreValues = (restore = false) => {
    const selected = widget.value;
    for (const child of canvasNode.widgets ?? []) {
      if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
      restoredWidgets.add(child);
      const key = `${selected}/${child.name}`;
      const label = labels?.get(key);
      if (label) child.label = label;
      const saved = canvasNode.properties.conditionalValues;
      if (restore && saved && Object.hasOwn(saved, key))
        child.value = saved[key];
      const removed = child.onRemove;
      child.onRemove = function() {
        if (!app2.configuringGraph) {
          canvasNode.properties.conditionalValues ??= {};
          canvasNode.properties.conditionalValues[key] = child.value;
        }
        removed?.call(this);
      };
    }
  };
  restoreValues();
  return restoreValues;
}
function refreshGraph() {
  for (const canvasNode of app2.rootGraph.nodes) {
    for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
  }
}
app2.registerExtension({
  name: "openrouter",
  setup: () => {
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = new URL("./extension.css", import.meta.url).href;
    const stylesheets = /* @__PURE__ */ new Set();
    for (const link of document.querySelectorAll("link[rel=stylesheet]")) {
      stylesheets.add(link.getAttribute("href"));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
  addCustomNodeDefs: readChildLabels,
  nodeCreated: addNodeControls,
  afterConfigureGraph: refreshGraph,
  commands: [
    {
      id: "OpenRouter.OpenSettings",
      label: message("settings.menu"),
      function: openSettings.bind(null, requestLocal)
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "OpenRouter"],
      commands: ["OpenRouter.OpenSettings"]
    }
  ]
});
