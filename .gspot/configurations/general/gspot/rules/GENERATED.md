# Generated Code

Read this rule when you change a generated file, or the code that writes one.

- Never edit a generated file by hand. Change the source or the generator, and rerun its command.
- Mark generated paths in `.gitattributes` with `linguist-generated`; for example, `output/** linguist-generated`. A
  folder named `generated/` does not make its files generated.
- A generated file equals a fresh run of its command. A difference shows a defect in the change.
- Do not commit build output (`dist/`, `coverage/`, compiled assets) unless the deployment reads it from the repository,
  and then declare it.

## Readable output

- Where the format allows comments, start the file with a header. Name the generator and the command that writes it. Add
  one line that states the file's purpose. A folder that `.gitattributes` marks generated as a whole needs no header in
  its files.
- Group the items of a generated list, such as an ignore file, under a comment that states their purpose, one section
  per source. Write each item once.
- Write one item per line, in a stable order. Use the formatter's layout.
- Keep code that a program runs in a source file that the checks read, not in a string inside the generator.
