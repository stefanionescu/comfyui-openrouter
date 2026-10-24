# Settings

Read this rule when you change how a program reads its settings or environment.

## Validate external values

- A missing or invalid value stops startup. The message names the variable and never prints its value.
- Parse booleans from an explicit accepted set, numbers with bounds, URLs through the URL parser, and lists with a
  declared separator. Treat an empty required value as missing.

## Reading settings

- Each process reads the environment in one module and passes the values in.
- Parse each value once at startup and expose a typed, immutable settings object.
- Do not add a hierarchy or a generic settings module for one value.

## Settings structure

- A settings file imports no application code.
- Defaults live in the schema that validates the file, not scattered through readers.
- State one precedence order in the settings module: command-line flag, environment variable, project file,
  default. That module resolves it; readers never merge sources themselves.
