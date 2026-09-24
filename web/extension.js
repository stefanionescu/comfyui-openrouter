// web/scripts/text.ts
import { app } from "../../scripts/app.js";
var TEXT = {
  close: "Close",
  models: {
    checkDue: "An automatic model check is due. Checks do not change this list.",
    checkRunning: "An automatic model check is running. Reopen this list to see its result.",
    checkSchedule: "Automatic check: {date}. Checks run every {hours} hours.",
    checking: "Checking OpenRouter's public model lists...",
    checksOff: "Automatic model checks are off. Change this in OpenRouter settings.",
    close: "Close OpenRouter models",
    count: "{visible} of {total} models",
    damaged: "The saved model list could not be read, so the nodes show the list that came with this version. Refresh Models to replace it.",
    installedList: "Showing the model list that came with this version. Refresh Models to load current models and prices.",
    invalidResponse: "ComfyUI returned an invalid OpenRouter model list.",
    lastRefresh: "Models and prices checked {date}.",
    listChanged: "The model list has changed. Select Refresh Models to update your list.",
    readFailed: "Cannot load models.",
    reread: "Local model list loaded.",
    reading: "Loading model list...",
    readingLocal: "Loading the local model list...",
    nodeUnavailable: "No node lists this model. Choose other model ID in a node and type its ID.",
    nodesAvailable: "Used by: {nodes}.",
    openGuide: "Model page on OpenRouter (opens in a new tab)",
    refresh: "Refresh Models",
    refreshNotice: "Refresh updates models and prices. The node dropdowns show the refreshed list.",
    refreshed: "Model list refreshed.",
    reloadNodes: "The node dropdowns now show this list.",
    requestFailed: "The model list request failed.",
    restore: "Restore Previous List",
    restored: "Previous model list restored.",
    search: "Search models",
    searchPlaceholder: "Model name, ID, or node",
    sources: "Model sources and automatic checks",
    title: "OpenRouter Models",
    unreachable: "Cannot reach the OpenRouter model list. Check ComfyUI and try again.",
    menu: "OpenRouter models"
  },
  pricing: {
    calculate: "Calculate a price",
    calculation: "Estimate: {amount}.",
    inputTokens: "input tokens",
    outputTokens: "output tokens",
    videoSeconds: "video seconds",
    perMillionInput: "per 1M input tokens",
    perMillionOutput: "per 1M output tokens",
    perMillionCharacters: "per 1M characters",
    perRequest: "per request",
    perVideoSecond: "per video second",
    range: "{lowest} to {highest}, by sound and resolution",
    rate: "{price} {unit}",
    rateOutdated: "This model was not in the latest list. Refresh OpenRouter models before relying on its price.",
    rateUnavailable: "OpenRouter lists no price for this model.",
    totalTimeNotice: "The estimate is not a quote; OpenRouter decides each charge."
  },
  settings: {
    moreLimits: "Advanced limits",
    automaticChecks: "Check for model updates automatically",
    checkInterval: "check interval (hours)",
    checkNotice: "Checks read OpenRouter's public model lists. Open OpenRouter models to see changes and refresh your list.",
    checksSaved: "Model check settings saved. Changes take effect within one minute.",
    clearKey: "Clear Saved Key",
    close: "Close OpenRouter settings",
    credentialLabel: "OpenRouter API key",
    credentials: "Credentials",
    environmentKey: "The server's OPENROUTER_API_KEY environment variable is active.",
    incompleteResponse: "ComfyUI returned incomplete OpenRouter settings.",
    invalidChecks: "ComfyUI returned invalid model check settings.",
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
    modelUpdates: "Model updates",
    noCheckChanges: "No model check changes to save.",
    noLimitChanges: "No limit changes to save.",
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: "Reload Settings",
    saveChecks: "Save Model Check Settings",
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
  ["model_interval_hours", "check interval (hours)"],
  ["parallel_requests", "parallel requests"],
  ["request_timeout_seconds", "request timeout (seconds)"],
  ["resubmit_hold_minutes", "resubmit hold (minutes)"],
  ["video_poll_seconds", "video check interval (seconds)"],
  ["video_wait_minutes", "maximum video wait (minutes)"]
]);
function message(key, values = {}) {
  let value = TEXT;
  for (const part of key.split(".")) {
    value = value[part];
  }
  return String(value).replaceAll(/\{(\w+)\}/g, (placeholder, name) => {
    if (!Object.hasOwn(values, name)) return placeholder;
    const inserted = values[name];
    return typeof inserted === "number" ? formatNumber(inserted) : String(inserted);
  });
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
function formatNumber(value, options) {
  return new Intl.NumberFormat(selectedLocale(), options).format(value);
}
function formatDate(value) {
  return new Date(value).toLocaleString(selectedLocale());
}
function formatMoney(value) {
  return formatNumber(value, { style: "currency", currency: "USD", maximumSignificantDigits: 4 });
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
  ["OpenRouterChatAsk", ["model"]],
  ["OpenRouterImageGenerate", ["model"]],
  ["OpenRouterVideoGenerate", ["model"]],
  ["OpenRouterAudioSpeak", ["model"]],
  ["OpenRouterAudioTranscribe", ["model"]],
  ["OpenRouterSearchEmbed", ["model"]],
  ["OpenRouterSearchRank", ["model"]],
  ["OpenRouterDecisionAsk", ["model"]],
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

// web/scripts/browser.ts
var browserLimits = {
  requestTimeoutMilliseconds: 1e4,
  discoveryTimeoutMilliseconds: 6e4,
  minCalculatorSeconds: 0.1,
  maxCalculatorSeconds: 3600,
  maxCalculatorTokens: 1e8,
  maxTextCharacters: 200,
  maxErrorCharacters: 1024,
  maxRetrievalTimeCharacters: 40,
  maxModelNodeIds: 100,
  maxModels: 4096
};
var browserPatterns = {
  revision: /^[a-f0-9]{64}$/,
  documentation: /^https:\/\/openrouter\.ai\/~?[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._:-]*$/,
  nodeId: /^OpenRouter[A-Za-z]+$/,
  settingName: /^[a-z][a-z_]+$/
};

// web/scripts/discovery/pricing.ts
var UNITS = /* @__PURE__ */ new Map([
  ["input tokens", { label: "pricing.perMillionInput", scale: 1e6, amount: "inputTokens" }],
  [
    "output tokens",
    { label: "pricing.perMillionOutput", scale: 1e6, amount: "outputTokens" }
  ],
  [
    "input characters",
    { label: "pricing.perMillionCharacters", scale: 1e6, amount: void 0 }
  ],
  ["request", { label: "pricing.perRequest", scale: 1, amount: void 0 }],
  ["video second", { label: "pricing.perVideoSecond", scale: 1, amount: "videoSeconds" }]
]);
function describePrice(price) {
  const unit = price.unit === null ? void 0 : UNITS.get(price.unit);
  if (unit === void 0) return `${price.label}: ${String(price.dollars)}`;
  const rate = message("pricing.rate", {
    price: formatMoney(price.dollars * unit.scale),
    unit: message(unit.label)
  });
  return `${price.label}: ${rate}`;
}
function estimatePrice(model, amounts) {
  const costs = model.prices.flatMap((price) => {
    const amount = price.unit === null ? void 0 : UNITS.get(price.unit)?.amount;
    return amount === void 0 ? [] : [{ amount, dollars: price.dollars * amounts[amount] }];
  });
  const tokens = costs.filter((cost) => cost.amount !== "videoSeconds").reduce((total, cost) => total + cost.dollars, 0);
  const videos = costs.filter((cost) => cost.amount === "videoSeconds").map((cost) => cost.dollars);
  if (videos.length === 0) return [tokens, tokens];
  return [tokens + Math.min(...videos), tokens + Math.max(...videos)];
}
function formatEstimate(estimate) {
  const [lowest, highest] = estimate;
  if (lowest === highest) return formatMoney(lowest);
  return message("pricing.range", { lowest: formatMoney(lowest), highest: formatMoney(highest) });
}
function formatPriceSummary(model, amounts) {
  if (model.prices.length === 0) return [message("pricing.rateUnavailable")];
  const summary = model.prices.map(describePrice);
  if (!model.observed) summary.push(message("pricing.rateOutdated"));
  else if (amounts !== void 0)
    summary.push(
      message("pricing.calculation", { amount: formatEstimate(estimatePrice(model, amounts)) })
    );
  return summary;
}

// web/scripts/discovery/row.ts
function buildModelRow(model, amounts) {
  const row = element("li");
  row.append(element("h3", model.name), element("code", model.id));
  const support = model.nodes.length > 0 ? message("models.nodesAvailable", { nodes: model.nodes.join(", ") }) : message("models.nodeUnavailable");
  row.append(element("p", support));
  for (const detail of formatPriceSummary(model, amounts)) row.append(element("p", detail));
  const link = element("a", message("models.openGuide"));
  link.href = model.documentationUrl;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  row.append(link);
  return row;
}

// web/scripts/routes.ts
var browserRoutes = {
  settings: {
    status: "/openrouter/v1/status",
    values: "/openrouter/v1/settings",
    credential: "/openrouter/v1/credential"
  },
  models: {
    read: "/openrouter/v1/models",
    refresh: "/openrouter/v1/models/refresh",
    rollback: "/openrouter/v1/models/rollback"
  }
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
function check(requirement, message$1) {
  return {
    kind: "validation",
    type: "check",
    reference: check,
    async: false,
    expects: null,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "input", dataset, config$1);
      return dataset;
    }
  };
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
function transform(operation) {
  return {
    kind: "transformation",
    type: "transform",
    reference: transform,
    async: false,
    operation,
    "~run"(dataset) {
      dataset.value = this.operation(dataset.value);
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
function array(item, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "array",
    reference: array,
    expects: "Array",
    async: false,
    item,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (Array.isArray(input)) {
        dataset.typed = true;
        dataset.value = [];
        for (let key = 0; key < input.length; key++) {
          const value$1 = input[key];
          const itemDataset = this.item["~run"]({ value: value$1 }, config$1);
          if (itemDataset.issues) {
            const pathItem = {
              type: "array",
              origin: "value",
              input,
              key,
              value: value$1
            };
            for (const issue of itemDataset.issues) {
              if (issue.path) issue.path.unshift(pathItem);
              else issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = itemDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          if (!itemDataset.typed) dataset.typed = false;
          dataset.value.push(itemDataset.value);
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
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
function nullable(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "nullable",
    reference: nullable,
    expects: `(${wrapped.expects} | null)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === null) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === null) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
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

// web/scripts/discovery/schema.ts
var shortTextSchema = pipe(
  string(),
  minLength(1),
  maxLength(browserLimits.maxTextCharacters)
);
var retrievalTimeSchema = nullable(
  pipe(
    string(),
    minLength(1),
    maxLength(browserLimits.maxRetrievalTimeCharacters),
    check((value) => Number.isFinite(Date.parse(value)))
  )
);
var priceSchema = pipe(
  object({
    label: shortTextSchema,
    usd: pipe(
      string(),
      maxLength(browserLimits.maxTextCharacters),
      check((value) => Number.isFinite(Number(value)) && Number(value) >= 0)
    ),
    unit: nullable(shortTextSchema)
  }),
  transform((price) => {
    return { label: price.label, dollars: Number(price.usd), unit: price.unit };
  })
);
var modelSchema = pipe(
  object({
    id: shortTextSchema,
    name: shortTextSchema,
    nodes: pipe(array(shortTextSchema), maxLength(browserLimits.maxModelNodeIds)),
    observed: boolean(),
    documentation_url: pipe(string(), regex(browserPatterns.documentation)),
    prices: pipe(array(priceSchema), maxLength(browserLimits.maxModelNodeIds))
  }),
  transform((model) => {
    return {
      id: model.id,
      name: model.name,
      nodes: model.nodes,
      observed: model.observed,
      documentationUrl: model.documentation_url,
      prices: model.prices
    };
  })
);
var automaticCheckSchema = pipe(
  object({
    enabled: boolean(),
    running: boolean(),
    interval_hours: pipe(number(), safeInteger(), minValue(1)),
    checked_at: retrievalTimeSchema,
    update_available: nullable(boolean()),
    error: nullable(
      pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
    )
  }),
  transform((check2) => {
    return {
      intervalHours: check2.interval_hours,
      checkedAt: check2.checked_at,
      updateAvailable: check2.update_available,
      error: check2.error,
      enabled: check2.enabled,
      running: check2.running
    };
  })
);
var modelListSchema = pipe(
  object({
    revision: pipe(string(), regex(browserPatterns.revision)),
    retrieved_at: retrievalTimeSchema,
    is_bundled: boolean(),
    is_damaged: boolean(),
    models: pipe(array(modelSchema), minLength(1), maxLength(browserLimits.maxModels)),
    can_rollback: boolean(),
    mutation_allowed: boolean(),
    automatic_check: optional(automaticCheckSchema)
  }),
  check((document2) => {
    const keys = /* @__PURE__ */ new Set();
    for (const model of document2.models) {
      if (keys.has(model.id)) return false;
      keys.add(model.id);
    }
    return true;
  }),
  transform((document2) => {
    return {
      revision: document2.revision,
      retrievedAt: document2.retrieved_at,
      isBundled: document2.is_bundled,
      isDamaged: document2.is_damaged,
      canRollback: document2.can_rollback,
      mutationAllowed: document2.mutation_allowed,
      models: document2.models,
      ...document2.automatic_check === void 0 ? {} : { automaticCheck: document2.automatic_check }
    };
  })
);
function parseModelList(value) {
  const result = safeParse(modelListSchema, value);
  if (!result.success) throw new Error(message("models.invalidResponse"));
  return result.output;
}

// web/scripts/discovery/api.ts
function modelRoute(action) {
  if (action === "read") return browserRoutes.models.read;
  if (action === "refresh") return browserRoutes.models.refresh;
  return browserRoutes.models.rollback;
}
function metadataStatus(list) {
  if (list.isDamaged) return message("models.damaged");
  if (list.isBundled || list.retrievedAt === null) return message("models.installedList");
  return message("models.lastRefresh", { date: formatDate(list.retrievedAt) });
}
async function requestModels(fetcher, signal, action, revision) {
  const options = {
    method: action === "read" ? "GET" : "POST",
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.discoveryTimeoutMilliseconds)
    ]),
    headers: { "Content-Type": "application/json", "X-OpenRouter-Comfy": "1" }
  };
  if (action === "rollback") options.body = JSON.stringify({ revision });
  let response;
  try {
    response = await fetcher(modelRoute(action), options);
  } catch {
    throw new Error(message("models.unreachable"));
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(message("models.invalidResponse"));
  }
  if (!response.ok) {
    throw new Error(parsePublicError(body) ?? message("models.requestFailed"));
  }
  return parseModelList(body);
}

// web/scripts/discovery/dialog.ts
var current;
function automaticStatus(check2) {
  if (!check2) return "";
  if (!check2.enabled) return message("models.checksOff");
  if (check2.running) return message("models.checkRunning");
  if (check2.error) return check2.error;
  if (check2.updateAvailable === true) return message("models.listChanged");
  if (check2.checkedAt)
    return message("models.checkSchedule", {
      date: formatDate(check2.checkedAt),
      hours: check2.intervalHours
    });
  return message("models.checkDue");
}
var ModelDialog = class {
  /**
   * Build the searchable model browser.
   * @param fetcher - ComfyUI's local API client.
   * @param reloadNodes - Reads ComfyUI's node definitions again, so the dropdowns show a changed list.
   */
  constructor(fetcher, reloadNodes2) {
    this.fetcher = fetcher;
    this.reloadNodes = reloadNodes2;
    this.dialog.className = "openrouter-dialog openrouter-models";
    this.dialog.setAttribute("aria-labelledby", "openrouter-models-title");
    const heading = element("h2", message("models.title"));
    heading.id = "openrouter-models-title";
    const close = button(message("close"));
    close.setAttribute("aria-label", message("models.close"));
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
    const header = element("header");
    header.append(heading, close);
    const searchLabel = element("label", message("models.search"));
    this.search.type = "search";
    this.search.setAttribute("placeholder", message("models.searchPlaceholder"));
    searchLabel.append(this.search);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.list.setAttribute("aria-label", message("models.title"));
    const sources = element("details");
    sources.append(
      element("summary", message("models.sources")),
      this.checked,
      this.automatic,
      element("p", message("models.refreshNotice"))
    );
    this.dialog.append(
      header,
      this.actions(),
      this.status,
      searchLabel,
      this.count,
      this.calculation(),
      sources,
      this.list
    );
    for (const input of [this.search, this.inputTokens, this.outputTokens, this.videoSeconds]) {
      input.addEventListener("input", this.updateView.bind(this));
    }
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
  }
  fetcher;
  reloadNodes;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  search = element("input");
  inputTokens = element("input");
  outputTokens = element("input");
  videoSeconds = element("input");
  refresh = button(message("models.refresh"));
  rollback = button(message("models.restore"));
  status = element("p", message("models.readingLocal"));
  checked = element("p");
  automatic = element("p");
  count = element("p");
  list = element("ul");
  modelList;
  /**
   * Build actions to refresh or restore the model list.
   * @returns The model browser actions.
   */
  actions() {
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener("click", this.updateModels.bind(this, "refresh"));
    this.rollback.addEventListener("click", this.updateModels.bind(this, "rollback"));
    const actions = element("div");
    actions.className = "openrouter-actions";
    actions.append(this.refresh, this.rollback);
    return actions;
  }
  /**
   * Build the optional price calculation: input tokens, output tokens, and video seconds.
   * @returns The collapsed calculation controls.
   */
  calculation() {
    const calculation = element("details");
    calculation.append(element("summary", message("pricing.calculate")));
    for (const [input, text, maximum, step] of [
      [this.inputTokens, message("pricing.inputTokens"), browserLimits.maxCalculatorTokens, "1"],
      [this.outputTokens, message("pricing.outputTokens"), browserLimits.maxCalculatorTokens, "1"],
      [
        this.videoSeconds,
        message("pricing.videoSeconds"),
        browserLimits.maxCalculatorSeconds,
        "any"
      ]
    ]) {
      const label = element("label", text);
      input.type = "number";
      input.min = "0";
      input.max = String(maximum);
      input.step = step;
      label.append(input);
      calculation.append(label);
    }
    calculation.append(element("p", message("pricing.totalTimeNotice")));
    return calculation;
  }
  /**
   * Read the calculator's amounts; nothing to estimate until a box holds a valid number.
   * @returns The entered amounts, with empty boxes as zero, or nothing when none is entered.
   */
  readAmounts() {
    const boxes = [this.inputTokens, this.outputTokens, this.videoSeconds];
    if (boxes.every((box) => box.value === "") || boxes.some((box) => !box.validity.valid))
      return void 0;
    const [inputTokens, outputTokens, videoSeconds] = boxes.map(
      (box) => box.value === "" ? 0 : box.valueAsNumber
    );
    return {
      inputTokens: inputTokens ?? 0,
      outputTokens: outputTokens ?? 0,
      videoSeconds: videoSeconds ?? 0
    };
  }
  /** Update matching models and calculations from the current controls. */
  updateView() {
    const query = this.search.value.trim().toLowerCase();
    const amounts = this.readAmounts();
    const rows = document.createDocumentFragment();
    for (const model of this.modelList?.models ?? []) {
      const label = `${model.id} ${model.name} ${model.nodes.join(" ")}`;
      if (label.toLowerCase().includes(query)) rows.appendChild(buildModelRow(model, amounts));
    }
    const visible = rows.childElementCount;
    this.list.replaceChildren();
    this.list.appendChild(rows);
    setText(
      this.count,
      message("models.count", {
        visible,
        total: this.modelList?.models.length ?? 0
      })
    );
  }
  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   */
  updateModels(action) {
    this.refresh.disabled = this.rollback.disabled = true;
    setText(
      this.status,
      action === "refresh" ? message("models.checking") : message("models.reading")
    );
    void this.requestModels(action);
  }
  /**
   * Apply a model-list response while the dialog is open.
   * @param action - The requested list operation.
   * @returns When the request and action cleanup finish.
   */
  async requestModels(action) {
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action,
        this.modelList?.revision
      );
      if (this.controller.signal.aborted) return;
      this.displayModels(next, action);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(this.status, error instanceof Error ? error.message : message("models.readFailed"));
    } finally {
      this.restoreActions();
    }
  }
  /**
   * Display a model list and the outcome of its requested operation.
   * @param next - The validated local model list.
   * @param action - The completed list operation.
   */
  displayModels(next, action) {
    this.modelList = next;
    setText(this.checked, metadataStatus(next));
    setText(this.automatic, automaticStatus(next.automaticCheck));
    let status = message("models.reread");
    if (action === "refresh") status = message("models.refreshed");
    if (action === "rollback") status = message("models.restored");
    if (action !== "read") {
      this.reloadNodes();
      status = `${status} ${message("models.reloadNodes")}`;
    }
    setText(this.status, status);
    this.updateView();
  }
  /** Re-enable allowed list changes after the current request finishes. */
  restoreActions() {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.modelList?.mutationAllowed;
    this.rollback.disabled = !this.modelList?.mutationAllowed || !this.modelList.canRollback;
  }
  /** Show the dialog and read the local model list. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateModels("read");
  }
  /** Stop pending requests and return focus to the caller. */
  dispose() {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openModels(fetcher, reloadNodes2) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, reloadNodes2);
  current.show();
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
  integer_settings: unknown(),
  settings: unknownRecordSchema,
  credential_limit: unknown()
});
var checkSettingsSchema = object({ model_auto_check: boolean() });
var credentialLimitSchema = pipe(number(), safeInteger(), minValue(1));
function parseDefinitions(value) {
  const document2 = safeParse(unknownRecordSchema, value);
  if (!document2.success) throw new Error(message("settings.invalidResponse"));
  if (!Object.hasOwn(document2.output, "model_interval_hours")) {
    throw new Error(message("settings.incompleteResponse"));
  }
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
  const definitions = parseDefinitions(document2.integer_settings);
  const checkSettings = safeParse(checkSettingsSchema, document2.settings);
  const credentialLimit = safeParse(credentialLimitSchema, document2.credential_limit);
  if (!checkSettings.success || !credentialLimit.success) {
    throw new Error(message("settings.invalidChecks"));
  }
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
var current2;
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
      this.modelUpdates(),
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
  modelCheckFields = element("fieldset");
  automatic = element("input");
  interval = element("input");
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
      if (name === "model_interval_hours") continue;
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
   * Build the controls for checking public model sources.
   * @returns The automatic model check form.
   */
  modelUpdates() {
    const form = element("form");
    this.modelCheckFields.disabled = true;
    const automaticLabel = element("label", message("settings.automaticChecks"));
    this.automatic.type = "checkbox";
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element("label", message("settings.checkInterval"));
    this.interval.type = "number";
    this.interval.step = "1";
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.modelCheckFields.append(
      element("legend", message("settings.modelUpdates")),
      automaticLabel,
      intervalLabel,
      element("p", message("settings.checkNotice")),
      button(message("settings.saveChecks"), "submit")
    );
    form.append(this.modelCheckFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveModelUpdates(this.configuration);
    });
    return form;
  }
  /**
   * Save automatic checks without changing the displayed model list.
   * @param configuration - The settings and revision currently shown.
   */
  saveModelUpdates(configuration) {
    const settings = {
      model_auto_check: this.automatic.checked,
      model_interval_hours: this.interval.valueAsNumber
    };
    if (settings.model_auto_check === configuration.settings.model_auto_check && settings.model_interval_hours === configuration.settings.model_interval_hours) {
      setText(this.status, message("settings.noCheckChanges"));
      return;
    }
    this.updateSettings(message("settings.checksSaved"), browserRoutes.settings.values, "PATCH", {
      revision: configuration.revision,
      settings
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
    const interval = configuration.definitions.model_interval_hours;
    this.interval.min = String(interval.minimum);
    this.interval.max = String(interval.maximum);
    setText(
      this.source,
      {
        missing: message("settings.missingKey"),
        saved: message("settings.savedKey"),
        environment: message("settings.environmentKey")
      }[configuration.credentialSource]
    );
    this.automatic.checked = configuration.settings.model_auto_check;
    this.interval.value = String(configuration.settings.model_interval_hours);
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
    this.keyFields.disabled = this.limitFields.disabled = this.modelCheckFields.disabled = true;
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
        this.keyFields.disabled = this.limitFields.disabled = this.modelCheckFields.disabled = !this.configuration?.mutationAllowed;
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
    if (current2 === this) current2 = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openSettings(fetcher) {
  if (current2?.dialog.open) {
    current2.dialog.focus();
    return;
  }
  current2 = new SettingsDialog(fetcher);
  current2.show();
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
  const restoreValues = (restore = false) => {
    const selected = widget.value;
    for (const child of canvasNode.widgets ?? []) {
      if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
      restoredWidgets.add(child);
      const key = `${selected}/${child.name}`;
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
function reloadNodes() {
  app2.extensionManager.command.execute("Comfy.RefreshNodeDefinitions");
}
function refreshGraph() {
  for (const canvasNode of app2.rootGraph.nodes) {
    for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
  }
}
app2.registerExtension({
  name: "comfyui-openrouter",
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
  nodeCreated: addNodeControls,
  afterConfigureGraph: refreshGraph,
  commands: [
    {
      id: "OpenRouter.OpenSettings",
      label: message("settings.menu"),
      function: openSettings.bind(null, requestLocal)
    },
    {
      id: "OpenRouter.OpenModels",
      label: message("models.menu"),
      function: openModels.bind(null, requestLocal, reloadNodes)
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "OpenRouter"],
      commands: ["OpenRouter.OpenSettings", "OpenRouter.OpenModels"]
    }
  ]
});
