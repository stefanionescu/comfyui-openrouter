# Bun

Read this rule when code runs on Bun.

## Module resolution

- Match internal imports to the project entry point and TypeScript configuration. Bun
  [resolves TypeScript directly](https://bun.sh/docs/runtime/module-resolution), including explicit `.ts` imports and
  extensionless paths. Do not assume the project outputs `.js` files.

## APIs

- Use a `Bun.*` API only where the project runs on Bun alone, and say so in the file header.
