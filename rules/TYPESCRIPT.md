# Working with TypeScript

Use these rules when writing or reviewing source files and shared tooling written
in TypeScript.

Start with the compiler and import settings for the code's runtime. Then read the sections for the
change you are making.

## Contents

- [Validate data and describe it with types](#validate-data-and-describe-it-with-types)
- [Configure the compiler and runtime](#configure-the-compiler-and-runtime)
- [Organize source files](#organize-source-files)
- [Import and export modules](#import-and-export-modules)
- [Place type declarations](#place-type-declarations)
- [Name declarations](#name-declarations)
- [Parse and represent values](#parse-and-represent-values)
- [Use objects, arrays, and destructuring](#use-objects-arrays-and-destructuring)
- [Define functions and parameters](#define-functions-and-parameters)
- [Use classes for instance behavior](#use-classes-for-instance-behavior)
- [Infer and narrow types](#infer-and-narrow-types)
- [Represent missing values](#represent-missing-values)
- [Validate external input](#validate-external-input)
- [Handle errors and asynchronous work](#handle-errors-and-asynchronous-work)
- [Document public behavior](#document-public-behavior)
- [Maintain generated code](#maintain-generated-code)

## Validate data and describe it with types

Use TypeScript to describe the values your code accepts and returns. Validate external input before
relying on those types. Type annotations disappear at runtime, so an annotation alone cannot check
an HTTP response or environment variable.

Use the project's runtime schema library or project-specific validation
functions to check incoming values. After validation, pass the resulting typed
values to the code that uses them.

Prefer plain values, small functions, discriminated unions, and modules with clear responsibilities.
Keep types simple enough that a reader can connect them to the runtime behavior. When implementation
or enforcement conflicts with these rules, fix the conflict in the affected code and checks. Change
a rule explicitly when the standard itself needs to change.

## Configure the compiler and runtime

Enable these compiler settings:

| Setting                            | What it checks                                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------------------- |
| `strict`                           | Enables TypeScript's strict type checks, including null checks and implicit `any` checks |
| `noUncheckedIndexedAccess`         | Includes `undefined` when an indexed read can refer to a missing value                   |
| `exactOptionalPropertyTypes`       | Distinguishes an absent optional property from a property set to `undefined`             |

Match module resolution and import extensions to the configured compiler and
runtime. Do not impose an import style from another runtime.

Keep the exact ESLint rule configuration with the lint tooling. Apply the
sections below for [imports](#import-and-export-modules),
[type declarations](#place-type-declarations),
[external input](#validate-external-input), [narrowing](#infer-and-narrow-types),
and [naming](#name-declarations).

## Organize source files

Write source files as UTF-8. Place imports before implementation so readers can see a module's
dependencies before reading its behavior.

- Use `const` for bindings that are not reassigned.
- Use `let` when reassignment is needed. Never use `var`.
- Keep side-effect imports rare. Make their purpose clear at the import site.
- Keep triple-slash references out of handwritten source. Generated declarations
  follow their generator's requirements.
- Keep file comments about the code's purpose. Remove change-history notes, stale paths, and
  generated examples that are not part of the working code.

Choose direct code and descriptive names that readers can search for. Explain a module's purpose
when its name and public API do not make that purpose clear.

## Import and export modules

Use ES module syntax.

- Use `import type` for symbols used only as types.
- Use `export type` when re-exporting type-only symbols.
- Use named imports and exports for application modules. Keep mutable exports such as `export let`
  out of public module APIs.
- Use default exports only for files whose tools require them.
- Keep default exports out of other modules.
- Use modules for namespacing. Do not create a class or exported object solely to collect unrelated
  functions under one name.
- Do not use `namespace`, `module`, or `import x = require(...)`.

Re-export only from an `index` barrel module, with at most 20 re-exports and no
name exported twice. Every other module declares what it exports: it does not
only re-export, and it does not export a constant that renames another binding.

Follow the [runtime import policy](#configure-the-compiler-and-runtime) when choosing extensions.

## Place type declarations

Put a reusable type beside the shared behavior it describes or in the
subproject's established type directory. Keep generated types and shared
handwritten types in their respective modules.

Use `type` aliases for object shapes. Keep type-only modules free of runtime behavior and imports
with side effects. Do not add an interface to bypass a lint rule.

Keep local types beside their implementation. Move a type to a shared module
when multiple modules use the same data shape or API. Choose its location based
on those consumers rather than placing all types in a global directory.

## Name declarations

Follow [NAMING.md](NAMING.md) for declaration names, files, directories, role words,
and framework exceptions. Apply the configured naming checks for the source you change.

## Parse and represent values

Represent values explicitly so a reader can tell how input becomes application data.

- Use literal unions or `as const` objects for fixed sets of values. Do not use TypeScript enums.
- Parse strings, numbers, booleans, and dates explicitly when they enter through user input,
  environment variables, or provider responses.
- Avoid implicit coercion of those external values.
- Check values explicitly when `0`, `''`, `false`, `null`, and `undefined` have different meanings.
  A truthiness check groups them together and can discard a valid value.

Use `as const` when preserving literal types helps describe a fixed value set. Keep the resulting
runtime object easy to read.

## Use objects, arrays, and destructuring

Use object literals to group related inputs when a long positional parameter list would be hard to
read.

- Add an object type annotation when the object implements a shared API or its shape needs to be
  explicit. Prefer that annotation to an `as SomeType` assertion.
- Use destructuring when it makes the fields being used easier to see. Keep the local names clear
  and consistent with the source fields.
- Use `T[]` for simple arrays.
- Use `Array<T>` or `ReadonlyArray<T>` when the element type is complex.
- Use readonly arrays or properties when callers are expected to leave them unchanged.

With `noUncheckedIndexedAccess`, an indexed read can include `undefined`. Check that the value
exists before using it. Keep that check in production code instead of replacing it with a non-null
assertion.

## Define functions and parameters

Declare the inputs and outputs that callers rely on. Let TypeScript infer local details when the
result is clear.

- Annotate exported function return types.
- Annotate callback parameters when TypeScript cannot infer their types clearly.
- Avoid reassigning parameters; use a local variable for a value that changes during the function.
- Use a discriminated union or an options object when it expresses the inputs more clearly than
  overloads.
- Add generic parameters only when they describe a useful relationship between types. Give them
  descriptive names when a single `T` does not explain their role.

Make a parameter optional when omitting it is a supported use of the function. Update callers that
are missing required input instead of marking that input optional.

## Use classes for instance behavior

Use a class when each instance needs its own identity or encapsulated state. Use plain functions and
objects for stateless behavior.

- Keep constructors focused on initializing the instance.
- Use `override` when overriding a class member.
- Use decorators only when the project's approved toolchain requires them.
- Do not create static container classes solely for namespacing.

Use a module with named exports when the behavior does not need per-instance identity or state.

## Infer and narrow types

Keep public APIs explicit and let TypeScript infer local values. For an untrusted value, start with
`unknown` and narrow it with checks that establish its type.

- Avoid `any`, including assertions to `any`.
- Avoid double assertions and broad `as` casts.
- Keep non-null assertions out of production code.
- Validate the value, use a typed helper, or correct the source type before considering a cast.
- Use a discriminated union for known variants. Its discriminant property lets a check select the
  fields available in each variant.
- Give type aliases a clear purpose. Avoid aliases that only rename another type without explaining
  a distinct use or relationship.
- Follow [type declaration rules](#place-type-declarations) for object shapes.

## Represent missing values

Choose a type that matches how absence is represented in the data.

- Prefer optional properties and parameters over `| undefined` when omission is supported.
- Do not create aliases such as `type Foo = Bar | undefined`. Add the possibility of absence where
  that specific input, property, or result can be missing.
- Normalize external empty strings, missing fields, and `null` values when they enter the
  application. Preserve differences that matter to the operation.
- Check missing values before use. Do not replace those checks with non-null assertions in
  production code.

With `exactOptionalPropertyTypes`, `property?: T` allows the property to be absent. A required
`property: T | undefined` keeps the property present while allowing its value to be `undefined`.
Choose the form that matches the data and how callers use it.

## Validate external input

Validate values at the point where external data enters the application. Use
the project's runtime schema library or validation functions for:

- HTTP bodies, query strings, route parameters, and headers;
- environment variables;
- provider responses;
- file input and generated data sources.

After validation, pass the checked values to domain code with their resulting types. Keep parsing
and rejection close to the entry point so the rest of the application can rely on the checked shape.
Do not pass raw request objects or unchecked `unknown` values through unrelated domain code.

## Handle errors and asynchronous work

Follow [GENERAL.md](GENERAL.md#logging). Do not add loggers, logging libraries,
console logging, or stack-trace output. Report failures through typed results,
exceptions, or the interface's defined error surface.

Throw an `Error` instance or a project-specific subclass. Preserve enough context to diagnose the
failure safely.

- Use `new Error(...)` or the relevant `Error` subclass.
- Do not throw strings, numbers, plain objects, or unvalidated provider payloads.
- Treat caught values as `unknown`. Narrow them before reading properties.
- Preserve the original cause when wrapping an error.
- Keep each `try` block close to the operation whose failure it handles.
- Remove catch blocks that only rethrow the same error.
- Use `Promise.all` for independent work with a bounded number of concurrent operations.
- Use sequential `await` when ordering, rate limits, or failure isolation require it.

## Document public behavior

Explain what callers need to know to use an API correctly.

- Document exported APIs when their purpose is not clear from their names and types.
- Explain invariants, access checks, concurrency behavior, and runtime assumptions that callers need
  to preserve. An invariant is a condition that stays true before and after an operation.
- Put type information in TypeScript declarations rather than repeating it in JSDoc.
- Follow [GENERAL.md](GENERAL.md#documentation-requirements) for comment
  coverage and [present-state wording](GENERAL.md#present-state-only).
- Give every ESLint disable directive a specific explanation.

Use JSDoc for public API behavior, assumptions, and caller obligations. Keep descriptions close to
the declarations they explain, and update them when the behavior changes.

## Maintain generated code

Regenerate TypeScript through the tool that owns the output. Keep source schema
changes and regenerated types together.

- Leave generated type files to their generator.
- Change the generator when its output needs a style or structure change, or document the required
  exception.
- Keep handwritten adapters around generated types small and beside the code that needs them.
- Apply style refactors to handwritten source and generators, rather than editing generated output
  by hand.
