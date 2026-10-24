# Documentation

Read this rule when you write or change documentation.

## Before you write

Read the existing pages. Identify the reader, their task, starting state, permissions, and risks. Describe supported
behavior. Before the install steps, state limitations that rule out use.

Keep durable product information in its documentation. Link to its reference instead of copying procedures or
configuration tables. When behavior changes, update the reference and examples.

## Pages

Give each page one purpose and a title that names its task or subject. Explain its purpose before its sections. Keep the
shortest successful path in the README and link to specialist guides. Document real subprojects. Describe behavior
instead of adding folder trees or file inventories. Mention a path only when the reader must use it.

Use the renderer's Markdown. Keep routine pages free of custom layout HTML or CSS. A component that some viewers cannot
show needs a text alternative. Use paragraphs, lists, and tables to match what readers need to compare.

Say what a feature does in everyday words.

Use inline code for exact commands, values, fields, and identifiers. Bold names an interface control. Blockquotes hold
attributed source text.

Keep required instructions outside collapsed panels. Delete obsolete content. A badge belongs only where its accurate
state affects a reader's decision.

## Examples and procedures

An example teaches one idea and uses the supported API. Include imports, setup, and the context readers need. Label an
incomplete fragment and say what it omits. Keep volatile output out of examples unless the public API defines its exact
text.

State the starting folder and prerequisites before commands. Explain placeholders. Separate output from commands, or
comment it out where a copied block must run. State the expected result when the command output does not make success
clear. Give each system alternative a complete procedure.

A destructive step names its scope, irreversible effects, backup, and recovery before the action. Keep permissions,
verification, and recovery beside the steps that need them. Use secure defaults and least privilege. Examples do not
silently turn off access checks. Keep authentication, retries, and advanced variants outside minimal examples unless
needed for correctness.

Start troubleshooting with the observable symptom and common causes. Diagnose before a reset or other destructive
recovery. Preserve exact public errors and remove private data from examples.

Do not write the current release number in prose or examples. Write `<version>` and say once where to find the number,
or generate the text from the dependency file.

## Reference pages

Use the names and values of the API the page documents. Explain public behavior without requiring readers to inspect its
code. A command reference covers inputs, outputs, exit codes, working folder, permissions, and side effects. An API
reference covers identity, inputs, outputs, failures, pagination, and limits. A library reference covers initialization,
cleanup, concurrency, errors, compatibility, and types. A settings reference covers scope, precedence, defaults,
secrets, and reloads.

Show settings with their parent keys. Distinguish missing, empty, and null values when they act differently. Explain
required environment variable formats and failures. Describe releases by their effect on readers and required actions.

A known issue states its trigger, risk, and verified workaround. A deprecation names support, replacement, and
migration. A retirement names the unavailable functions. Security disclosures follow the project policy.

## Images and video

Match the current interface and reproduce control labels exactly. Name controls by label. A screenshot adds to a text
procedure. It does not replace instructions.

Keep media with its editable source and license. Use screenshots for interfaces, diagrams for relationships, and charts
for data. Add media when text alone does not explain the information. Report stale media.

A video needs captions and a transcript for information absent from the page. Keep the full procedure in text. Do not
embed trackers or commit video outside the project's asset workflow. Follow ACCESSIBILITY.md for alt text and color.

Keep diagrams small and draw equal concepts with the same shape. Prefer editable diagrams and descriptive file names.
List keyboard shortcuts and per-system steps in a fixed order.

## Links

Use maintained primary sources for external APIs and relative paths for repository content. A public procedure states
any account or permission needed to open a required page. See [Diátaxis](https://diataxis.fr/) and
[W3C image guidance](https://www.w3.org/WAI/tutorials/images/).
