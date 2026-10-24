# Writing

Read this rule when you write text that people read in files: documentation, comments, messages, and commit messages.

TALKING.md covers what you say to the user.

Write in plain language under `ISO 24495-1`: short sentences and common words. State the action or result early. Explain
a technical term when the reader needs it.

## Evidence

Check commands, fields, defaults, limits, and supported versions against the implementation that defines them. A
measurement does not guarantee future results. When evidence lacks required facts, narrow the claim. Link external facts
to the primary source; never invent behavior to complete a page.

Preserve exact API identifiers, public messages, official product names, and legal license text. Keep private reasoning
and temporary notes out of shipped content. Examples use fictional people, safe values, and `example.com` addresses.

## Voice

Use active voice when the actor matters. Address the reader as you in procedures. Use imperatives for requirements and
label optional steps. Put a condition before its action and keep one main idea per sentence. Name the subject instead of
relying on an ambiguous pronoun.

Avoid idioms, unexplained abbreviations, and decorative wording. Use literal terms that survive translation. Keep one
term for each concept. Dates shown to people include their time zone; machine values retain their required format.

## References

See the [Google developer documentation style guide](https://developers.google.com/style) for general writing guidance.
Project-specific requirements take precedence.
