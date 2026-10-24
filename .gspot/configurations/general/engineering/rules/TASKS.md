# Task Runners

Read this rule when you change `mise` tasks, `package.json` scripts, a `Makefile`, or another task runner.

## Task behavior

- Reuse the task names the project has. Add a task only when asked.
- Do not add empty section markers or scripts that only echo a placeholder.
- When a step fails, the task stops and exits with an error.

## Task organization

- Use one declared task runner per project.
- Name tasks in kebab-case with a colon namespace, such as `check:fix` or `deploy:staging`.
- Use the runner's declarative commands and dependency ordering. Keep substantial parsing, branching, and process
  control in the code that implements that behavior.
- Give each task a concise description in the runner's list.
- Do not compute an argument by running code inside the task definition, such as a template `exec()` that evaluates a
  source file. Put the value where the tool reads it, or in the task script.
- Write a command line once. When tasks differ in one part, write a single task that takes that part as an argument.
- A task script runs commands. It does not import the internals of a workspace package.
