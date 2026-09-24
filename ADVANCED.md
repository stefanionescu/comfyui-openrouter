# ComfyUI OpenRouter Advanced Guide

This guide builds on the [README](README.md). It covers what each node sends,
the settings and limits, models, caching, video recovery, development,
and what each message means.

## Contents

- [Data and storage](#data-and-storage)
- [What each node sends](#what-each-node-sends)
- [Keys and access](#keys-and-access)
- [Settings](#settings)
- [Models](#models)
- [Caching and reruns](#caching-and-reruns)
- [Recover a video](#recover-a-video)
- [Limits](#limits)
- [When a node stops](#when-a-node-stops)
- [Update or remove](#update-or-remove)
- [Development](#development)
- [Package and publish](#package-and-publish)
- [Troubleshooting](#troubleshooting)

## Data and storage

- Paid requests go from the ComfyUI server to OpenRouter with your key. The
  model's provider receives the prompts, media, and documents.
- The model check reads OpenRouter's public page for each model ID, without
  the key.
- The private folder holds the key, the settings, and the video job records.
  ComfyUI's save nodes write the outputs.
- Paid requests are sent exactly once, since a dropped connection may already
  have reached OpenRouter.

## What each node sends

Each paid node checks its inputs, waits for one of the **parallel requests**
slots, checks the model ID, sends one request, and turns the reply into ComfyUI
outputs. Media are converted in a worker thread, so ComfyUI stays responsive.

- **Chat: Ask** sends the prompt and the media: images as PNG, videos as MP4,
  and audio as WAV. PDFs go to OpenRouter's PDF engine; text files go as text.
  Earlier turns come from **conversation**. It returns the text, the reasoning
  when the model shares it, and any images the model made. Speech comes back
  as 24 kHz mono PCM.
- **Chat: Attach Document** reads one file from ComfyUI's input folder and
  passes it to **Chat: Ask**.
- **Image: Generate** sends the prompt, the chosen settings, the count, and each
  reference image as PNG. It returns images, their masks (white is
  transparent), and SVG files.
- **Video: Generate** sends the prompt, the chosen settings, and the frames or
  references. It records the job as soon as OpenRouter accepts it, checks it
  every **video check interval**, and downloads the MP4 when it is ready.
- **Video: Download** checks one recorded job and downloads its video. Status
  checks and downloads are free.
- **Audio: Speak** sends the text, the voice, the speed, and the voice sample as
  WAV when one is connected. It returns the audio as PCM or MP3.
- **Audio: Transcribe** sends the clip as WAV, with the language and the
  timestamps you ask for. It returns the text, the segments, SRT subtitles, and
  the timed words.
- **Search: Embed** sends every text line and image in one request. It compares
  each embedding with the first one locally.
- **Search: Rank** sends the query and every text line and image in one request.
  It returns them in order, with their scores.
- **Decision: Ask** sends the situation and the questions to OpenRouter's alpha
  decisions API, which serves decision models such as TypeSafe's Jev.
  **Decision: Read Answer** reads one answer locally.
- **Request Options** holds settings that each connected paid node adds to its
  request. A node stops with an error on a setting its request type rejects.

## Keys and access

Save the key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter
settings**. The key is stored in the private folder and used only by the
server. The first request that uses it validates it.

`OPENROUTER_API_KEY`, set where ComfyUI starts, takes precedence over a saved
key. **Clear Saved Key** deletes the saved copy; revoke keys at openrouter.ai.

The key and settings can be changed only over a direct local connection to the
ComfyUI server. For remote access, a reverse proxy, or multi-user mode, set
`OPENROUTER_API_KEY` instead.

The private folder is:

| System  | Folder                                               |
| ------- | ---------------------------------------------------- |
| macOS   | `~/Library/Application Support/OpenRouterComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/openrouter-comfy` |
| Windows | `%LOCALAPPDATA%\OpenRouterComfyUI`                   |

To use another folder, set `OPENROUTER_COMFY_STATE_DIRECTORY` to an absolute
path outside the extension, ComfyUI, and ComfyUI's input, output, temporary,
and user folders. Files are stored unencrypted, with owner-only permissions
where the system supports them.

## Settings

Change these in **OpenRouter settings**. New requests use the saved values; a
running request keeps its own. One MiB is 1,048,576 bytes.

| Setting                        | Default | Range      | What it limits                                               |
| ------------------------------ | ------- | ---------- | ------------------------------------------------------------ |
| request timeout (seconds)      | 600     | 10 to 3600 | How long one paid request may take.                          |
| maximum upload size (MiB)      | 64      | 1 to 512   | The media and documents in one request.                      |
| maximum download size (MiB)    | 512     | 16 to 4096 | The largest reply, image, audio, or video accepted.          |
| parallel requests              | 4       | 1 to 16    | Requests running at once in one ComfyUI run.                 |
| video check interval (seconds) | 15      | 5 to 120   | The time between video status checks.                        |
| maximum video wait (minutes)   | 30      | 1 to 240   | How long one run waits for a video.                          |
| resubmit hold (minutes)        | 30      | 0 to 1440  | How long an uncertain video request blocks an identical one. |

If another window saved the settings after you opened them, reload and make
your change again. Invalid values are refused, and the saved settings are kept.

## Models

Each paid node has a **model** field that takes any model ID from
openrouter.ai/models, with an optional variant suffix such as `:nitro`. Before
it sends, the node reads OpenRouter's public page for that model, without the
key, and stops with an error when:

- the field is empty;
- OpenRouter has no model with that ID;
- the model makes something the node does not return, such as a video model in
  **Image: Generate**.

The check runs once per model each time ComfyUI starts. It also tells the node
whether the model's providers take a seed, and for **Chat: Ask** a temperature;
the node sends them only then. Every other setting is sent only when you change
it from **model default** or 0. OpenRouter ignores or refuses a setting the
model does not take, and a refusal shows its reason.

The default model of each node is:

| Node              | Default model                         |
| ----------------- | ------------------------------------- |
| Chat: Ask         | `google/gemini-3.5-flash`             |
| Image: Generate   | `google/gemini-3.1-flash-image`       |
| Video: Generate   | `google/veo-3.1-fast`                 |
| Audio: Speak      | `google/gemini-3.1-flash-tts-preview` |
| Audio: Transcribe | `openai/whisper-large-v3-turbo`       |
| Search: Embed     | `openai/text-embedding-3-small`       |
| Search: Rank      | `cohere/rerank-v3.5`                  |
| Decision: Ask     | `typesafe/jev-1.13`                   |

**Audio: Speak** starts with the voice `Kore`, which its default model needs.
Other speech models name their own voices.

### Prices

openrouter.ai/models lists each model's prices. Each request's charge is listed
at openrouter.ai/activity. To cap spending, set a credit limit on the key at
openrouter.ai.

## Caching and reruns

- ComfyUI reuses a node's result while its inputs are unchanged. Change **run
  number** to send the same request again. Each request is billed.
- A paid node's **seed** changes after each run unless its control is **fixed**,
  so running again sends a new request. The examples use **fixed**.
- Saving a different key invalidates the cached results. Changing settings
  keeps them.
- ComfyUI keeps only the last run's results by default, so running another
  workflow in between sends the requests again.
- Free requests, such as model checks, video checks, and video downloads, are
  tried up to three times when OpenRouter is busy or the connection drops. Paid
  requests are sent exactly once.
- ComfyUI's cancel stops the wait. A chat model still bills the tokens it
  produced, and a video job keeps running and is billed.

## Recover a video

**Video: Generate** records each job as soon as OpenRouter accepts it. A video
job always runs to completion at OpenRouter and is billed, even when you cancel
the run, ComfyUI restarts, or **maximum video wait** passes.

To get the video, add **Video: Download**, choose the job in **job**, and
select **Run**. Press R to list jobs started after the page loaded. Running the
identical request again on **Video: Generate** also picks up the recorded job.

If the connection closes before OpenRouter confirms a video request, the video
may be running and billed. The extension records the request as uncertain and
refuses an identical one for **resubmit hold (minutes)**; check
openrouter.ai/activity meanwhile. A job is removed from the list once its video
is downloaded, or when OpenRouter reports that it failed, was cancelled, or
expired.

## Limits

| Item                              | Limit                                                          |
| --------------------------------- | -------------------------------------------------------------- |
| Chat image sockets                | 16; every image in a batch is sent.                            |
| Chat video and audio sockets      | 4 each.                                                        |
| Documents in one chat request     | 8.                                                             |
| Chat prompt                       | 1,000,000 characters.                                          |
| Conversation                      | 200 turns.                                                     |
| Output tokens                     | Up to 1,000,000; 0 leaves it to the model.                     |
| Image side                        | 8192 pixels; larger images are refused.                        |
| Images from one request           | 1 to 10.                                                       |
| Image reference sockets           | 16; every image in a batch is sent.                            |
| Video reference sockets           | 8 images, 2 videos, 2 audio clips.                             |
| Video duration                    | Up to 60 seconds; 0 leaves it to the model.                    |
| Speech text                       | 100,000 characters.                                            |
| Voice sample                      | 15 MiB.                                                        |
| Search items in one request       | 256, with up to 16 image sockets.                              |
| Embedding dimensions              | Up to 8192; 0 leaves it to the model.                          |
| Decision questions                | 32; 2 to 32 options; 2 to 10 levels.                           |
| Decision situation                | 200,000 characters.                                            |
| Answer threshold                  | 0.5 by default.                                                |
| Providers in one list             | 32.                                                            |
| Provider options and extra fields | 64 KB each.                                                    |
| Upload and download size          | 64 MiB and 512 MiB by default, set in **OpenRouter settings**. |

## When a node stops

Paid nodes check these conditions before sending, so a refused input is free.
Every paid node also stops when its model ID is empty or unknown, or the model
makes something the node does not return; see [models](#models).

**Chat: Ask** stops when:

- The prompt is empty or too long, or the conversation is too long.
- The media are over the upload limit.
- The answer schema is not a JSON object.

**Chat: Attach Document** stops when:

- No file is chosen, or the file is outside the input folder.
- The file is not a PDF or text file, is over the upload limit, or is not UTF-8
  text.
- More than 8 documents are chained.

**Image: Generate** stops when:

- The prompt is empty.
- A transparent background is asked for with JPEG.

**Video: Generate** stops when:

- There is no prompt and no first frame.
- Frames and references are both connected, or a frame is a batch.
- An identical request is on hold after an uncertain submission.

**Audio: Speak** stops when the text is empty or too long, or the voice sample
is too large. **Audio: Transcribe** stops when the language is not a two-letter
code, or the clip is a batch.

**Search: Embed** and **Search: Rank** stop when there are no items or more than 256. **Search: Rank** also stops
when the query is empty.

**Decision: Add Question** stops when the name is invalid or used twice, the
question is empty, the list already has 32 questions, or the answer type's
fields are incomplete.

**Decision: Ask** stops when the situation is empty or too long. **Decision:
Read Answer** stops when no question has the name.

**Request Options** stops when a provider list or a JSON field cannot be read.
A paid node stops when the options include a setting its request does not
accept.

Once a request is sent, OpenRouter's answer decides:

| Status   | Meaning                                                          |
| -------- | ---------------------------------------------------------------- |
| 400      | OpenRouter refused the request; the message gives the reason.    |
| 401      | The key is missing or invalid.                                   |
| 402      | The account or key is out of credit.                             |
| 403      | OpenRouter blocked the request; the message gives the reason.    |
| 404      | OpenRouter cannot serve the model; the message gives the reason. |
| 408, 524 | The provider took too long.                                      |
| 413      | The request is too large.                                        |
| 429      | OpenRouter is limiting requests.                                 |
| 502      | The provider failed. Failed image requests are free.             |
| 503      | No provider meets the request's routing requirements.            |
| 529      | The provider is overloaded.                                      |

## Update or remove

Stop ComfyUI before changing the extension.

To update, replace the whole `custom_nodes/comfyui-openrouter` folder with the
new version, install its `requirements.txt` with ComfyUI's Python, restart
ComfyUI, and reload its window. Keep only one copy in `custom_nodes`. Open the
updated examples in a new tab; saved graphs keep their own notes and layout.

To remove the extension, move its folder out of `custom_nodes` and restart.
Leave shared Python packages, since other extensions may use them. The private
folder stays after an update or removal. To delete the saved key, settings,
and job records, delete the [private folder](#keys-and-access).

## Development

### Setup

Development needs Git and mise. To install mise, run
`curl https://mise.run | sh`. Tell the checks where ComfyUI is, in
`.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

`.mise.local.toml` is ignored by Git. Then install the tools, the locked
dependencies, the Semgrep rules, and the Git hooks:

```shell
mise trust && mise run repo:setup
```

### Generated files

```shell
mise run repo:deps:export          # Regenerate requirements.txt from pyproject.toml
mise run comfy:frontend:build      # Build the browser files
mise run comfy:workflows:build     # Build the 13 example workflows
mise run comfy:nodes:schema        # Print the node descriptions the workflow build reads
```

The example workflows are generated from `scripts/workflows/descriptions/`.
Each category has a module. `notes.py` holds the group notes and subgraph
descriptions, and `texts.py` holds the titles. The build reads the node
descriptions through ComfyUI's Python and runs offline. Node sizes follow ComfyUI's own layout, so a workflow keeps its layout
when it loads.

### Full check

```shell
mise run repo:check                # Run every check below
```

This runs `repo:deps:verify`, `repo:format:check`, `repo:lint`, `repo:type`,
`comfy:frontend:check`, `comfy:nodes:check`, `comfy:workflows:check`,
`repo:security`, `repo:licenses`, and `repo:links:external`. A change is ready
when the full check passes.

### Format

```shell
mise run repo:format               # Format Python, pyproject.toml, web, and Markdown files
mise run repo:format:check         # List files that need formatting
```

This uses Ruff for Python, pyproject-fmt for `pyproject.toml`, and Prettier for
web and Markdown files.

### Lint

```shell
mise run repo:lint                 # Run every linter
```

- `repo:lint:policy`: repository structure, naming, and function rules.
- `repo:lint:python`: Ruff, the custom Python rules, import-linter, pydoclint,
  interrogate, deptry, and vulture.
- `repo:lint:frontend`: ESLint, naming, stylelint, knip, madge, and jscpd.
- `repo:lint:shell`, `repo:lint:hooks`, and `repo:lint:mise`: shell syntax,
  ShellCheck, shfmt, and the shell rules.
- `repo:lint:docs`: markdownlint, typos, and local links.
- `repo:lint:quality`: the quality tools and their configuration.

### Types

```shell
mise run repo:type                 # Check Python and TypeScript types
```

This runs basedpyright in strict mode against your ComfyUI installation, and
`tsc` for the browser code.

### Generated-file checks

```shell
mise run comfy:frontend:check      # The browser files match their source
mise run comfy:nodes:check         # The help pages and menus match the nodes
mise run comfy:workflows:check     # The workflows match their descriptions, and the README links each one
```

The workflow check also requires every node to appear in at least one
workflow.

### Security and licenses

```shell
mise run repo:security             # Run the secret, code, and dependency scanners
mise run repo:licenses             # Check dependency licenses
```

`repo:security` runs Gitleaks, Bearer, Bandit, the Python and Bun advisory
audits, Semgrep with the pinned rules, and CodeQL for Python and the browser
code.

### Git hooks

`mise run repo:setup` installs the hooks:

- **pre-commit** checks for private files and staged secrets, then runs the
  source, formatting, type, and browser-file checks.
- **commit-msg** checks the [conventional
  commit](https://www.conventionalcommits.org/) format, `type(scope): subject`.
- **pre-push** runs the full check.

To skip a run, set `SKIP_HOOKS=1`. To skip only part of it, set `SKIP_LINT=1`
(the pre-commit checks), `SKIP_ENV_CHECK=1` (the private-file check), or
`SKIP_COMMITLINT=1` (the commit message check).

### Test a change

Testing is manual. Restart ComfyUI after Python changes, or rebuild the
browser files and reload the window after browser changes, then run the
workflows your change affects. Paid nodes are billed, so test with inexpensive
models.

### Code layout

`src/` holds only packages. The package's `__init__.py` holds the `Extension`
class ComfyUI loads, and imports the nodes and routes when ComfyUI calls it.

| Package      | Holds                                                                               |
| ------------ | ----------------------------------------------------------------------------------- |
| `nodes`      | The node classes and the inputs they share                                          |
| `comfy`      | ComfyUI glue: running a request with progress and cancel, media, routes, runtime    |
| `openrouter` | Every request to OpenRouter, the model check, and the one module that sends the key |
| `settings`   | The private settings, their local routes, and the checks that keep them local       |
| `storage`    | The private files: settings, the saved key, and video job records                   |
| `types`      | Records, type aliases, JSON parsing, and the `OpenRouterError` every message uses   |
| `config`     | Constants and messages, with no code                                                |

The build scripts keep their paths in `scripts/paths.py`, the ComfyUI nodes the
workflows use in `scripts/nodes/host.py`, and their type aliases in
`scripts/types.py`.

### Import rules

Each package imports only the packages below it:

```text
src.nodes
src.comfy
src.openrouter | src.settings
src.storage
src.types
src.config
```

- ComfyUI is imported only in `src/nodes/`, `src/comfy/`, and the package's
  `__init__.py`.
- All OpenRouter code is in `src/openrouter/`, and
  `src/openrouter/transport.py` is the one place that sends the key.
- The import contracts in `pyproject.toml` enforce these rules.
- Node names, descriptions, and tooltips are in each node's `io.Schema` call.
- Every other message is a constant in `src/config/messages/`, or in
  `web/scripts/text.ts` for the dialogs. Every other fixed value, such as a
  limit, a step, a file name, or a route, is a constant in `src/config/`.

### Function names

Every function in `src/`, `scripts/`, and `__init__.py` starts with a verb from
the table in `rules/NAMING.md`, or is an `is_` or `has_` predicate. In each
module and class, private functions come first, `__all__` lists no private
name, and a function only its own module uses is private. `repo:lint:policy`
checks all four.

### README images

The README's images are in `docs/images/`:

- `banner.svg` and `node-map.svg` are SVG files; edit them as text. They use two
  palettes: ComfyUI's ink `#211927`, panels `#312C34`, text `#C2BFB9`, and yellow
  `#F0FF41`, and OpenRouter's indigo `#6366F1`. In the node map, a paid node has
  an indigo bar and a free one a grey bar, and links are yellow.
- `workflow-choose-group.png` is the **Choose** group of image-01 at 100% zoom.

Keep each image under 100 KB, and give it alt text in the README.

### Change text

- **A message:** edit its constant in `src/config/messages/`, and the matching
  heading under [troubleshooting](#troubleshooting).
- **A node's labels or tooltips:** edit its `io.Schema` call in `src/nodes/`,
  then its help page in `web/docs/`.
- **The dialogs:** edit `web/scripts/text.ts`, then rebuild the browser files.
- **A workflow's notes:** edit `scripts/workflows/descriptions/notes.py`; for
  titles, `texts.py`; for nodes, models, or prompts, the workflow's module. Then
  rebuild the workflows.
- **A node's default model:** edit `src/config/generation/models.py`, then the
  table under [models](#models) and the node's help page.

## Package and publish

The Comfy Registry package is made with
[comfy-cli](https://github.com/Comfy-Org/comfy-cli). These steps use version
1.20.0.

1. Create a publisher and a publishing key in the
   [Comfy Registry](https://docs.comfy.org/registry/publishing). This key is
   separate from your OpenRouter key.
2. In `pyproject.toml`, set `[tool.comfy].PublisherId` to your publisher ID, add
   `Repository` under `[project.urls]`, and set `[project].version`. Use a new
   version number for each release.
3. Rebuild the generated files:

    ```sh
    mise run repo:deps:export
    mise run comfy:frontend:build
    mise run comfy:workflows:build
    ```

4. Commit everything. The packer takes only files Git tracks, and
   `.comfyignore` leaves out development files.
5. Build and check the package:

    ```sh
    mise run comfy:release:package
    ```

    This runs the full check, builds `node.zip` with `comfy node pack`, lists
    its contents, and scans it for secrets.

6. Publish:

    ```sh
    mise run comfy:release:publish
    ```

    This repeats the package checks, then asks for the publishing key. The
    publisher ID is public and permanent; the key stays private.

7. Install the published version with ComfyUI Manager, and check that the nodes,
   menus, help pages, and templates load.

Publishing rebuilds the archive from the checkout, so publish the same commit
you packaged.

## Troubleshooting

Each heading below is a message a node or dialog shows.

### Set your OpenRouter API key in OpenRouter settings

No key is saved, and the server has no `OPENROUTER_API_KEY`. Save the key in
**OpenRouter settings**, or set the variable where ComfyUI starts and restart.

### OpenRouter did not accept the API key

OpenRouter answered 401. Check the key in **OpenRouter settings**, or in
`OPENROUTER_API_KEY`, which takes precedence. If the key was revoked, create a
new one at openrouter.ai.

### Your OpenRouter account or key has no credit left for this request

OpenRouter answered 402. Add credit at openrouter.ai/credits, or raise the key's
credit limit.

### OpenRouter refused the request

OpenRouter answered 400. The message gives the reason, such as a duration the
model does not accept. Change that value.

### OpenRouter blocked this request

OpenRouter answered 403. Moderation flagged the input, a guardrail on your
account or key blocked it, or the key lacks permission; the message gives the
reason. Change the input, the guardrail, or the key's permissions.

### The model refused to answer

The model refused instead of answering. Rephrase the prompt, or choose another
model.

### OpenRouter could not serve this model

OpenRouter answered 404. The model is unavailable now, or the key cannot use
it. Choose another model.

### No provider is available for this request

OpenRouter answered 503: no provider meets the request's routing requirements.
If **Request Options** is connected, loosen it, for example the provider lists,
**zero data retention**, or the price limits. Otherwise, try again later or
choose another model.

### The model's provider is overloaded

OpenRouter answered 529. Try again later, or choose another model.

### The model's provider failed to answer

OpenRouter answered 502. Run again, or choose another model. A failed image
request is not billed.

### The model's provider took too long to answer

OpenRouter answered 408 or 524. Try again later, or send a smaller request.

### OpenRouter is limiting requests

OpenRouter answered 429. Wait a moment, or lower **parallel requests** in
**OpenRouter settings**.

### The request is too large for OpenRouter

OpenRouter answered 413. Send fewer or smaller files.

### OpenRouter returned HTTP

OpenRouter answered with a status the extension does not recognize. Try again
later.

### ComfyUI could not reach OpenRouter

The connection failed before the request was sent, so nothing was billed.
Check the server's network connection and try again.

### The connection closed before OpenRouter answered

The connection closed after the request was sent. OpenRouter may have run and
billed it; check openrouter.ai/activity before running again.

### The request took longer than the request timeout

The request did not finish within **request timeout (seconds)**. Raise the
timeout, or send a smaller request.

### OpenRouter's reply held no result

The model returned no text, images, or audio. Run again, or choose another
model.

### OpenRouter's reply could not be read

The reply was not in the expected format. Run again; if it happens again, choose
another model.

### The OpenRouter nodes are still loading

ComfyUI has not finished loading the extension. Wait until it has started, then
run again.

### The saved OpenRouter key could not be read

The key file in the private folder cannot be read. Save the key again in
**OpenRouter settings**.

### Enter an OpenRouter API key of 1 to 1024 characters

The key was empty, too long, or started or ended with a space. Paste the whole
key.

### Remove spaces and line breaks from the OpenRouter API key

The key has a space or line break in it. Paste it again as one line.

### The settings changed in another window

Another window saved the settings after this one loaded them. Select **Reload
Settings** and make your change again.

### Choose each OpenRouter setting within its range

A setting is outside the range shown next to it. Choose a value in range.

### Enter whole numbers for the OpenRouter settings

A setting is not a whole number. Enter one.

### That OpenRouter setting cannot be changed here

The dialog sent a setting it does not edit. Reload the window.

### OpenRouter's settings file has an unknown setting

The settings file has a setting this version does not know. Remove that
setting, or delete the file to return to the defaults.

### OpenRouter's private settings could not be read

The settings file or the private folder cannot be read. Check the folder's
permissions.

### OpenRouter's private state could not be read or written

The private folder cannot be read or written. Check its permissions.

### Keep OpenRouter's private state outside ComfyUI

`OPENROUTER_COMFY_STATE_DIRECTORY` points inside ComfyUI, the extension, or a
media folder. Choose a folder outside them and restart ComfyUI.

### Set OPENROUTER_COMFY_STATE_DIRECTORY to an absolute folder path

The variable holds a relative path. Set it to an absolute path.

### An OpenRouter state file is larger than expected

A file in the private folder is over its size limit. Delete it. A video job
record can be deleted once you have its video.

### Write a prompt or connect a first frame

**Video: Generate** has no prompt and no first frame. Write a prompt, or connect
an image to **first frame**.

### Connect first or last frames, or references, not both

**Video: Generate** has both frames and references connected. OpenRouter would
use the frames and ignore the references, so disconnect one kind.

### Connect one image for each frame, not a batch

A frame of **Video: Generate** received several images. Connect one image.

### Connect at most this many references

**Video: Generate** has too many references of one kind. The limits are 8
images, 2 videos, and 2 audio clips.

### The video was not ready within the maximum video wait

The video was still being made after **maximum video wait (minutes)**.
OpenRouter keeps making it; get it with **Video: Download**, or raise the wait.

### OpenRouter could not make the video

The job failed; the message gives OpenRouter's reason. Change the input it
names, or choose another model.

### OpenRouter cancelled the video job

OpenRouter cancelled the job; the message gives the reason. Run the node again
to start a new job.

### The video job expired before it finished

The job expired at OpenRouter. Run the node again to start a new job.

### Choose an unfinished video job from the list

**Video: Download** has no recorded job chosen. Press R to refresh the list,
then choose a job.

### An earlier identical video request may have been accepted

An identical request is on hold after an uncertain submission. Wait the minutes
the message gives, or look for the job at openrouter.ai/activity.

### The connection closed before OpenRouter confirmed the video request

The video may be running and billed; check openrouter.ai/activity. An identical
request is refused for **resubmit hold (minutes)**.

### OpenRouter's video address was not on openrouter.ai

The finished job gave a download address outside openrouter.ai, so the key was
not sent there. Try **Video: Download** again later.

### Type a model ID from openrouter.ai/models

The node's **model** field is empty. Type a model ID, such as
`google/gemini-3.5-flash`.

### OpenRouter has no model named this ID

OpenRouter lists no model with the typed ID. Copy the ID from the model's page
at openrouter.ai/models; IDs are lowercase, in the form `author/model`.

### This model does not take this node's requests

The model makes something else, such as a video model in **Image: Generate**.
Choose a model of the node's kind at openrouter.ai/models.
