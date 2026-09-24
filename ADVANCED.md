# ComfyUI OpenRouter Advanced Guide

This guide is for people who already run the workflows described in the
[README](README.md). It defines what each node sends, decides, and returns,
lists the settings, limits, and defaults, and covers recovery, development,
and troubleshooting. Each node's native **Info** explains its inputs and
model-specific limits.

The extension keeps five fixed boundaries:

- Every paid request goes from the ComfyUI server to OpenRouter with your key.
  OpenRouter passes it to the model's provider, which receives your prompts,
  media, and documents.
- Model-list refreshes and automatic checks read OpenRouter's public lists and
  send no key.
- The extension saves four things in its private state folder: the key, the
  settings, the model lists, and the video job records. ComfyUI's save nodes
  write every output. The extension keeps no logs and no copy of prompts or
  outputs.
- A paid request is never retried, because it may have reached OpenRouter
  before its connection failed.
- Every message, label, and workflow note is in English.

## Contents

- [Run architecture](#run-architecture)
- [Keys and access](#keys-and-access)
- [Request limits](#request-limits)
- [Prices](#prices)
- [Model updates](#model-updates)
- [Caching and reruns](#caching-and-reruns)
- [Recovery](#recovery)
- [Limits and defaults](#limits-and-defaults)
- [When a run stops](#when-a-run-stops)
- [Update or remove](#update-or-remove)
- [Language](#language)
- [Developer workflow](#developer-workflow)
- [Official packaging and publishing](#official-packaging-and-publishing)
- [Troubleshooting](#troubleshooting)

## Run architecture

Each paid node follows the same steps. It reads its inputs and the chosen
model's entry in the saved model list, and refuses what the model cannot take.
It waits for one of the **parallel requests** slots, sends one request to
OpenRouter, and turns the reply into ComfyUI outputs. Media are encoded and
decoded in a worker thread, so ComfyUI stays responsive. An output the model
did not make stops the nodes connected to it.

What each node sends and returns:

- **Chat: Ask** sends one chat completion. The message holds the prompt, then the media: images as PNG, videos as MP4, and audio clips as WAV, each encoded in the request. A PDF goes as a file for OpenRouter's PDF engine, and a text file as text. Earlier turns come from **conversation**. It returns the
  text, the reasoning when the model shares it, and any images the model drew.
  A spoken answer is streamed as 24 kHz mono PCM audio.
- **Chat: Attach Document** reads one file from ComfyUI's input folder and
  sends nothing itself.
- **Image: Generate** sends one image request with the prompt, the chosen
  fields, the count, and each reference as a PNG data URL. It returns raster
  images with their masks, where white marks the transparent area, and SVG
  files separately.
- **Video: Generate** sends one video job with the prompt, the chosen fields,
  and the frames or references. It records the job as soon as OpenRouter
  accepts it, checks its status every **video check interval**, and downloads
  the MP4 from openrouter.ai when it is ready.
- **Video: Download** checks the status of one recorded job and downloads its
  video. It sends no paid request.
- **Audio: Speak** sends the text, the voice, the speed, and the voice sample as
  WAV when it is connected. It returns the audio OpenRouter sends, raw PCM or
  MP3.
- **Audio: Transcribe** sends the clip as WAV, with the language and the
  timestamps asked for. It returns the text, the segments, SRT subtitles, and
  the timed words.
- **Search: Embed** sends every text line and image in one request. The
  similarities are worked out on your computer, by comparing each vector with
  the first.
- **Search: Rank** sends the query and every text line and image in one
  request, and returns them in order of relevance with their scores.
- **Decision: Ask** sends the situation and the questions from **Decision: Add
  Question** to OpenRouter's alpha decisions API. **Decision: Read Answer**
  reads one answer locally and sends nothing.
- **Request Options** sends nothing itself. A paid node adds its provider
  choices and extra fields to its own request, and refuses a field its request
  type does not accept.

## Keys and access

Open **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**. Saving a
key clears the entry field and stores the value in the private server state
folder. The saved value is never returned to the window or written into a
workflow. Saving a key does not check it with OpenRouter; the next request shows
OpenRouter's answer if the key is wrong.

`OPENROUTER_API_KEY` in the ComfyUI server environment takes precedence over a
saved key. **Clear Saved Key** removes only the saved value; it does not revoke
the key at OpenRouter. Change an environment key where ComfyUI is launched,
then restart ComfyUI.

Changing settings or the key requires a local, single-user connection. Open the
ComfyUI window on the computer running its server and connect directly to the
local address. Remote connections, reverse proxies, and multi-user mode cannot
change them; set the server environment key for those setups.

The default state folders are:

| Platform | Folder                                               |
| -------- | ---------------------------------------------------- |
| macOS    | `~/Library/Application Support/OpenRouterComfyUI`    |
| Linux    | `${XDG_STATE_HOME:-~/.local/state}/openrouter-comfy` |
| Windows  | `%LOCALAPPDATA%\OpenRouterComfyUI`                   |

`OPENROUTER_COMFY_STATE_DIRECTORY` can select another absolute private path. It
must be outside the extension, ComfyUI's folder, and its input, output,
temporary, and user folders. The folder holds the saved key, the settings, the
saved model lists, and the video job records. Files use owner-only permissions
where supported. They are not encrypted; other code running as the same
operating-system user can read them.

## Request limits

**request timeout (seconds)** limits each request to OpenRouter. **maximum video
wait (minutes)** limits how long one run waits for a video job. **Advanced
limits** holds the upload and download sizes, the parallel request count, the
video check interval, and the resubmit hold. One MiB is 1,048,576 bytes.

New requests use saved settings; a running request keeps its own. If another
window saves settings first, reload before making your changes again. Invalid
settings leave the previous file intact.

| Setting                        | Default | Range      | Effect                                                       |
| ------------------------------ | ------- | ---------- | ------------------------------------------------------------ |
| request timeout (seconds)      | 600     | 10 to 3600 | The total time one paid request may take.                    |
| maximum upload size (MiB)      | 64      | 1 to 512   | The encoded media and documents in one request.              |
| maximum download size (MiB)    | 512     | 16 to 4096 | The largest reply, image, audio, or video accepted.          |
| parallel requests              | 4       | 1 to 16    | Requests in flight at once in one ComfyUI run.               |
| video check interval (seconds) | 15      | 5 to 120   | The time between video status checks.                        |
| maximum video wait (minutes)   | 30      | 1 to 240   | How long one run waits for a video job.                      |
| resubmit hold (minutes)        | 30      | 0 to 1440  | How long an uncertain video request blocks an identical one. |
| check interval (hours)         | 24      | 1 to 8760  | The time between automatic model-list checks.                |

## Prices

Open **ComfyUI menu → Extensions → OpenRouter → OpenRouter models** for each
model's prices. Token and character prices are shown per million; video prices
per second of video. Expand **Calculate a price** and enter input tokens, output
tokens, or video seconds to multiply the listed prices. Token prices add up. A
video model lists one price per choice of sound and resolution, so its estimate
is a range from the cheapest choice to the dearest. The estimate is not a
quote; OpenRouter decides each charge. A model without a listed price, or with
prices the dialog cannot estimate, shows none.

Nodes show no usage or cost. Each request's charge is listed at
openrouter.ai/activity. To cap spending, set a credit limit on the key at
openrouter.ai. Refresh the model list for current prices.

## Model updates

Open **ComfyUI menu → Extensions → OpenRouter → OpenRouter models** to search
the list that came with this version or your last saved list. Opening the
dialog reads local information. Each entry shows the nodes that list the model,
its prices, and a link to its page on OpenRouter.

**Refresh Models** reads OpenRouter's three public model lists: every model, the
image models, and the video models. It saves the result privately and the node
dropdowns reload to show it. The default models of the nodes are:

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

A model OpenRouter no longer lists stays in the saved list, so saved workflows
that use it still load; its prices show a warning, and running it shows
OpenRouter's own reason. To use a model the list does not hold, choose **other
model ID** in the node's dropdown and type its ID. A written ID is sent
unchanged, with every control the node offers.

A failed refresh leaves the current list intact. A refresh that lists far more
or far fewer models than the saved list is refused, so a broken reply cannot
replace a good list. **Restore Previous List** restores the list saved before
the latest refresh. Only the local ComfyUI user can change the list. When the
saved list cannot be read, the nodes show the list that came with this version
until a refresh replaces it.

### Automatic checks

Under **OpenRouter settings → Model updates**, enable checks and choose an
interval in hours. Checks are on by default and run every 24 hours while
ComfyUI runs. Changes take effect within one minute.

Checks read the same public lists as a refresh. They report changes without
replacing the saved list. Expand **Model sources and automatic checks** in the
models dialog, then select **Refresh Models** to save the checked list. Failed
checks keep the list and retry at the configured interval. Closing ComfyUI stops
checking.

## Caching and reruns

- ComfyUI reuses a cached result while a node's inputs are unchanged. Change
  **run number** to send the same request again; each run is billed.
- The **seed** of a paid node changes after each run unless its control is
  **fixed**, so queuing again sends a new request. The examples ship with the
  seed control on **fixed**.
- Saving a different key starts a new cache, so no result made with another
  key is reused. Changing settings keeps the cache.
- By default, ComfyUI keeps only the most recent run's results, so running
  another workflow in between sends the requests again.
- Paid requests are never retried. Requests that bill nothing, such as model
  lists, video status checks, and video downloads, are retried up to three
  times after a busy reply or a dropped connection.
- ComfyUI's cancel stops waiting during every request. A chat model bills the
  tokens it produced before the cancel, and a video job keeps running and
  billing.

## Recovery

Read the error and the node's native **Info** before trying again.

| Problem                 | Next step                                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| Missing or rejected key | Check OpenRouter settings and any server environment key, which takes precedence.                    |
| Refused input           | Read OpenRouter's reason in the message; it names the value to change, such as a supported duration. |
| Unavailable model       | Choose another model, or refresh the model list.                                                     |
| Video not ready in time | Collect it with **Video: Download**; OpenRouter keeps making it.                                     |
| Uncertain request       | Check openrouter.ai/activity before running again; the request may have been billed.                 |

### Recover a video job

**Video: Generate** records each job privately as soon as OpenRouter accepts it,
before it starts waiting. ComfyUI's cancel stops waiting but not the job, which
OpenRouter keeps making and billing, because OpenRouter has no way to cancel a
video job. Add **Video: Download**, choose the job in **job**, and
select **Run** to collect it; press R to list jobs recorded after the node
definitions were read. Running the identical request again on **Video:
Generate** resumes the recorded job instead of paying for a second one.

When the connection closes before OpenRouter confirms a video request, the
request may be running and billed. The extension records it as uncertain and
refuses the identical request for the **resubmit hold (minutes)** setting; check
openrouter.ai/activity in the meantime. A job's record is removed after its
video downloads, or when OpenRouter reports that it failed, was cancelled, or
expired.

## Limits and defaults

| Value                          | Limit or default                                       |
| ------------------------------ | ------------------------------------------------------ |
| Chat image sockets             | 16; every image of a batch is sent.                    |
| Chat video and audio sockets   | 4 each.                                                |
| Documents in one chat request  | 8.                                                     |
| Chat prompt                    | 1,000,000 characters.                                  |
| Conversation                   | 200 turns.                                             |
| Output tokens                  | The model's limit; 0 leaves it to the model.           |
| Image side                     | 8192 pixels; larger images are refused, never resized. |
| Images from one image request  | The model's range, up to 10.                           |
| Image reference sockets        | The model's limit, up to 16.                           |
| Video reference sockets        | 8 images, 2 videos, 2 audio clips.                     |
| Written video duration         | 1 to 60 seconds; 0 leaves it to the model.             |
| Speech text                    | 100,000 characters.                                    |
| Voice sample                   | 15 MiB.                                                |
| Search items in one request    | 256; image sockets 16.                                 |
| Embedding dimensions           | Up to 8192; 0 leaves them to the model.                |
| Decision questions             | 32; 2 to 32 options; 2 to 11 levels.                   |
| Decision situation             | 200,000 characters.                                    |
| Answer threshold               | 0.5.                                                   |
| Provider slugs in one list     | 32.                                                    |
| Provider options, extra fields | 64 KB each.                                            |
| Upload and download size       | 64 MiB and 512 MiB, from OpenRouter settings.          |

## When a run stops

A paid node checks its inputs against the chosen model before it sends
anything, so a refused input costs nothing.

**Chat: Ask** stops before sending when:

- The prompt is empty or too long, or the conversation is too long.
- The media is above the upload limit.
- A connected image, video, or audio clip is a kind the model does not read.
- The output token limit is above the model's.
- The answer schema is not a JSON object.

**Chat: Attach Document** stops when:

- No file is chosen, or the file is outside the input folder.
- The file is not a PDF or text file, is above the upload limit, or is not
  UTF-8 text.
- More than 8 documents are chained.

**Image: Generate** stops before sending when:

- The prompt is empty.
- The image count or the number of references is outside the model's range.
- A transparent background is asked of a JPEG.

**Video: Generate** stops before sending when:

- There is neither a prompt nor a first frame.
- Frames and references are both connected, or a frame is a batch.
- The model does not take a last frame or that kind of reference.
- An identical request is on hold after an uncertain submission.

**Audio: Speak** stops before sending when the text is empty or too long, or
the voice sample is too large. **Audio: Transcribe** stops when the language is
not a two-letter code or the clip is a batch.

**Search: Embed** and **Search: Rank** stop when:

- There are no items, or more than 256.
- Images reach a model that does not read them.
- For **Search: Rank**, the query is empty.

**Decision: Add Question** stops when:

- The name is not valid or is used twice.
- The question is empty, or the list already holds 32 questions.
- The answer type's fields are incomplete.

**Decision: Ask** stops when the situation is empty or too long. **Decision:
Read Answer** stops when no question has the name.

**Request Options** stops when a provider list or a JSON field cannot be read.
A paid node stops when the options hold a field its request type does not
accept.

After sending, OpenRouter's answer decides:

| Status   | Meaning                                                               |
| -------- | --------------------------------------------------------------------- |
| 400      | OpenRouter refused the request; the message gives its reason.         |
| 401      | The key is missing or invalid.                                        |
| 402      | The account or key has no credit left.                                |
| 403      | The model's provider refused the input; the message gives its reason. |
| 404      | OpenRouter could not serve the model; the message gives its reason.   |
| 408, 524 | The provider took too long.                                           |
| 413      | The request is too large.                                             |
| 429      | OpenRouter is limiting requests.                                      |
| 502      | The provider failed. A failed image request is not billed.            |
| 503, 529 | No provider can serve the model now.                                  |

## Update or remove

Finish or cancel active work, then stop ComfyUI before changing the extension.

To update, replace the whole `custom_nodes/comfyui-openrouter` folder with the
new version, install its runtime requirements using ComfyUI's Python, and
restart. Refresh the ComfyUI window.

Keep only one installed copy in `custom_nodes` to avoid duplicate nodes and menus.

Open an updated example in a new workflow tab. Existing tabs and saved graphs
keep their own notes, prompts, and layout.

To remove the extension, move its folder outside `custom_nodes` and restart.
Keep shared Python dependencies that other packs may use. Removing or updating
the extension keeps its private state folder. To remove the saved key, settings,
model lists, and job records too, delete only its
[state folder](#keys-and-access). Deleting a saved key does not revoke it at
OpenRouter.

## Language

The extension's text is English, and ComfyUI's language setting does not change
it. Dropdowns show the values OpenRouter receives, such as model IDs and `1:1`;
the node guides explain them. Workflow notes and node titles are saved in the
graph in English.

## Developer workflow

### Setup

Development needs **Git** and **mise**. If mise is not installed, install it
first with `curl https://mise.run | sh`. Use a repository checkout, and set the
ComfyUI installation used for schema and type checks in `.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

`mise.toml` sets no default. Do not commit machine paths or credentials.

Install the toolchain, the locked dependencies, the Semgrep rule packs, and the
Git hooks:

```shell
mise trust && mise run repo:setup   # Install tools, dependencies, rules, and hooks
```

### Generated files

```shell
mise run repo:deps:export          # Regenerate requirements.txt from pyproject.toml
mise run comfy:models:build        # Rebuild the bundled model list from OpenRouter's public lists
mise run comfy:frontend:build      # Compile the browser files
mise run comfy:workflows:build     # Rebuild the 13 workflows from their descriptions
mise run comfy:nodes:schema        # Print the node descriptions the workflow build reads
```

The workflows are built, not hand-saved. `scripts/workflows/descriptions/`
says what each one holds, one module per category. `notes.py` holds each
group's note and the subgraph descriptions, and `texts.py` the titles. Each step
after the inputs is a subgraph, whose ID comes from its workflow and name. The build
reads the node schemas through the ComfyUI interpreter, with the bundled model
list; it needs no running ComfyUI server and sends no request. Node heights
follow the sum ComfyUI's page computes, so a workflow keeps its layout when it
loads.

`comfy:models:build` reads the network and is not part of the complete check.
It fails when OpenRouter lists a kind of model that no node serves, so a new
kind of model is noticed before a release.

### Complete check

```shell
mise run repo:check                # Run every check below
```

This runs:

- `repo:deps:verify`
- `repo:format:check`
- `repo:lint`
- `repo:type:python` and `repo:type:frontend`
- `comfy:frontend:check`, `comfy:nodes:check`, and `comfy:workflows:check`
- `repo:security`
- `repo:licenses`
- `repo:links:external`

Only the complete check proves a change is green.

### Format

```shell
mise run repo:format               # Format Python, pyproject.toml, web, and documentation files
mise run repo:format:check         # Report files that need formatting
```

Formatters: `ruff format` for Python, `pyproject-fmt` for `pyproject.toml`, and
Prettier for web and documentation files.

### Lint

```shell
mise run repo:lint                 # Run every linter
```

This runs one task per concern:

- `repo:lint:policy`: repository structure, naming, and function rules.
- `repo:lint:python`: Ruff, the custom Python rules, import-linter,
  pydoclint, interrogate, deptry, and vulture.
- `repo:lint:frontend`: ESLint, naming, stylelint, knip, madge, and jscpd.
- `repo:lint:shell`, `repo:lint:hooks`, and `repo:lint:mise`: shell syntax,
  ShellCheck, shfmt, and the shell rules.
- `repo:lint:docs`: markdownlint, typos, and local links.
- `repo:lint:quality`: the quality tools and their configuration.

### Types

```shell
mise run repo:type                 # Check Python and TypeScript types
```

This runs basedpyright in strict mode against the configured ComfyUI
installation, and `tsc` for the browser files.

### Generated-output checks

```shell
mise run comfy:frontend:check      # Browser files match their source
mise run comfy:nodes:check         # Help pages and menus match the node schemas
mise run comfy:workflows:check     # Workflows match their descriptions; README links every one
```

The workflow check also reports a node that no workflow places.

### Security and licenses

```shell
mise run repo:security             # Run the secret, code, and dependency scanners
mise run repo:licenses             # Check dependency licenses
```

`repo:security` runs Gitleaks, Bearer, Bandit, the Python and Bun advisory
audits, Semgrep with the pinned rule packs, and CodeQL for Python and the
frontend. `repo:licenses` checks the Python and frontend dependency licenses.

### Git hooks

`mise run repo:setup` installs the hooks. Set `SKIP_HOOKS=1` to skip one run,
`SKIP_LINT=1` to skip the pre-commit source, formatting, type, and browser-file
checks, `SKIP_ENV_CHECK=1` to skip only the private-file guard, or
`SKIP_COMMITLINT=1` to skip only the commit message check.

- **pre-commit** runs the private-file guard, the staged-secrets scan, source
  checks, formatting, types, and the browser-file check.
- **commit-msg** enforces the [conventional
  commit](https://www.conventionalcommits.org/) format, `type(scope): subject`.
- **pre-push** runs the complete `mise run repo:check`.

### Runtime verification

Restart ComfyUI after Python changes. Rebuild the browser files and reload the
browser after frontend changes. The project has no automated test suites:
verify a change by running the affected workflows in the loaded checkout. Paid
nodes send billed requests, so choose inexpensive models while testing.

### Code boundaries

The packages stack in one order, and a package imports only packages below it:

```text
src.extension
src.nodes
src.comfy
src.runtime
src.execution | src.discovery | src.settings
src.http
src.credentials
src.storage | src.serialization | src.tasks | src.paths
src.errors
src.state
src.config
```

- Only `src/nodes/`, `src/comfy/`, and `src/extension.py` import ComfyUI's
  modules; `src/execution/` never touches ComfyUI, and the nodes never touch
  HTTP. The import contracts in `pyproject.toml` hold these rules.
- `src/execution/transport.py` is the only code that sends the key.
- Node display names, descriptions, and tooltips live in each `io.Schema` call,
  because that is ComfyUI's contract.
- Every other message a person reads is a named constant in
  `src/config/messages/`, and in `web/scripts/text.ts` for the dialogs.

### Change messages and workflow notes

- To change a message a node shows, edit its constant in
  `src/config/messages/`. The [troubleshooting](#troubleshooting) headings
  quote the messages, so change the matching heading too.
- To change a node's labels or tooltips, edit its `io.Schema` call in
  `src/nodes/`, then its help page in `web/docs/`.
- To change the dialogs' text, edit `web/scripts/text.ts`, then rebuild the
  browser files.
- To change a workflow's group notes or subgraph descriptions, edit
  `scripts/workflows/descriptions/notes.py`; for titles, edit `texts.py` in the
  same folder. To change its nodes, models, or
  prompts, edit its module in the same folder. Then rebuild the workflows.
- To change a node's default model, edit `src/config/generation/models.py`.
  The default must be in the bundled model list, which `mise run
comfy:models:build` refreshes.

## Official packaging and publishing

Use [Comfy's official CLI](https://github.com/Comfy-Org/comfy-cli) to create and
publish the Registry package. The commands below use comfy-cli 1.20.0.

1. Create a publisher and publishing API key in
   [Comfy Registry](https://docs.comfy.org/registry/publishing). The publishing
   key is separate from the OpenRouter key.
2. Set `[tool.comfy].PublisherId` to that publisher's ID in `pyproject.toml`,
   add `[project.urls]` with `Repository` and `Issues`, and choose an unused
   semantic version in `[project].version`. Published versions cannot be
   overwritten.
3. Build the distribution files:

    ```sh
    mise run comfy:models:build
    mise run repo:deps:export
    mise run comfy:frontend:build
    mise run comfy:workflows:build
    ```

4. Commit the reviewed source and built files. The official packer selects
   Git-tracked paths and reads their current working-tree content. New untracked
   files are omitted. `.comfyignore` excludes development files.
5. Run the release task:

    ```sh
    mise run comfy:release:package
    ```

    This runs the project checks, including network-backed dependency, security,
    and link checks. It then calls `comfy node pack`, lists the contents of
    `node.zip`, and scans the archive for secrets.

6. Publish when ready. This repeats the package checks before publishing:

    ```sh
    mise run comfy:release:publish
    ```

    Enter the Registry publishing key at the hidden prompt. No `.env` file is
    required. This CLI does not read `REGISTRY_ACCESS_TOKEN` automatically.

    Choose the publisher ID yourself when creating the account. Comfy requires
    this public ID in the committed `pyproject.toml`; it cannot be renamed after
    account creation. The API key authorizes publishing and stays private.

7. Install the published version through ComfyUI Manager and check node loading,
   menus, help, and templates in that installation.

Publishing creates a new archive from the checkout. Keep the source, built
files, tracked paths, metadata, `.comfyignore`, and CLI version unchanged after
inspection. The publish command does not upload the previously inspected ZIP.

## Troubleshooting

### Set your OpenRouter API key in OpenRouter settings

No key is saved and the server has no `OPENROUTER_API_KEY`. Save the key in
**OpenRouter settings**, or set the variable where ComfyUI starts and restart it.

### OpenRouter did not accept the API key

OpenRouter answered 401. Check the key in **OpenRouter settings** or in the
server's `OPENROUTER_API_KEY`, which takes precedence, and create a new key at
openrouter.ai if it was revoked.

### Your OpenRouter account or key has no credit left for this request

OpenRouter answered 402. Add credits at openrouter.ai/credits, or raise the
key's credit limit.

### OpenRouter refused the request

OpenRouter answered 400, and the message gives its reason, such as a duration
the video model does not accept or a model ID that does not exist. Change the
value it names.

### The model's provider refused this input

The provider's content checker refused the prompt or media, and the message
gives its reason. Change the input, or choose another model.

### The model refused to answer

The model answered with a refusal instead of an answer. Rephrase the prompt, or
choose another model.

### OpenRouter could not serve this model

OpenRouter answered 404. The model or its variant is not available now, or the
key cannot use it. Choose another model, or refresh the model list.

### No provider can serve this model right now

OpenRouter answered 503 or 529. Try again later, or choose another model.

### The model's provider failed to answer

OpenRouter answered 502. Run again, or choose another model. A failed image
request is not billed.

### The model's provider took too long to answer

OpenRouter answered 408 or 524. Try again later, or send a smaller request.

### OpenRouter is limiting requests

OpenRouter answered 429. Wait a moment before running again, or lower
**parallel requests** in OpenRouter settings.

### The request is too large for OpenRouter

OpenRouter answered 413. Send fewer or smaller images, videos, audio clips, or
documents.

### OpenRouter returned HTTP

OpenRouter answered with a status this extension does not describe. Try again
later.

### ComfyUI could not reach OpenRouter

The connection failed before the request was sent, so nothing was billed.
Check the server's network connection and try again.

### The connection closed before OpenRouter answered

The connection closed after the request was sent. OpenRouter may have run and
billed it; check openrouter.ai/activity before running again.

### The request took longer than the request timeout

The request did not finish within **request timeout (seconds)** in OpenRouter
settings. Raise the timeout, or send a smaller request.

### OpenRouter's reply held no result

The model answered without text, images, or audio. Run again, or choose
another model.

### OpenRouter's reply could not be read

OpenRouter's reply had an unexpected form. Run again; if it repeats, choose
another model.

### The OpenRouter nodes are still loading

ComfyUI has not finished loading the extension. Wait for it to finish starting,
then run again.

### The saved OpenRouter key could not be read

The key file in the state folder is unreadable. Save the key again in
**OpenRouter settings**.

### Enter an OpenRouter API key of 1 to 1024 characters

The key field was empty, too long, or had spaces at either end. Paste the whole
key.

### Remove spaces and line breaks from the OpenRouter API key

The key had a space or line break inside it. Paste it again as one piece.

### The settings changed in another window

Another window saved the settings after this one read them. Select **Reload
Settings** and make the change again.

### Choose each OpenRouter setting within its range

A setting is outside the range shown next to it. Choose a value within it.

### Enter whole numbers for the OpenRouter settings

A setting is not a whole number. Enter one.

### Choose on or off for automatic model checks

The settings file holds a value that is not on or off. Save the setting again
in **OpenRouter settings**.

### That OpenRouter setting cannot be changed here

The request named a setting the dialog does not edit. Reload the window.

### OpenRouter's settings file has an unknown setting

The settings file in the state folder has a setting this version does not know.
Remove it, or delete the file to go back to the defaults.

### OpenRouter's private settings could not be read

The settings file or the state folder cannot be read. Check the state folder's
permissions.

### OpenRouter's private state could not be read or written

The state folder cannot be read or written. Check its permissions.

### Keep OpenRouter's private state outside ComfyUI

`OPENROUTER_COMFY_STATE_DIRECTORY` points inside ComfyUI, the extension, or a
media folder. Choose a private folder outside them and restart ComfyUI.

### Set OPENROUTER_COMFY_STATE_DIRECTORY to an absolute folder path

The variable holds a relative path. Set it to an absolute folder path.

### An OpenRouter state file is larger than expected

A file in the state folder has grown beyond its limit. Delete that file; a
video job record can be removed after you collect its video.

### Write a prompt or connect a first frame

**Video: Generate** has an empty prompt and no first frame. Write a prompt, or
connect an image to **first frame**.

### Connect first or last frames, or references, not both

**Video: Generate** has both frames and references connected. OpenRouter uses
the frames and ignores the references, so disconnect one kind.

### Connect one image for each frame, not a batch

A frame of **Video: Generate** received several images. Connect one image.

### Connect at most this many references

**Video: Generate** has more references of one kind than a request takes:
8 images, 2 videos, or 2 audio clips.

### This model does not accept these references

The chosen video model does not take this kind of reference. Disconnect it, or
choose a model that does.

### This model does not accept a last frame

The chosen video model takes only a first frame. Disconnect the last frame, or
choose a model that takes one.

### The video was not ready within the maximum video wait

The job was still running after **maximum video wait (minutes)**. OpenRouter
keeps making it; collect it with **Video: Download**, or raise the wait.

### OpenRouter could not make the video

The job failed, and the message gives OpenRouter's reason. Change the input it
names, or choose another model.

### OpenRouter cancelled the video job

OpenRouter cancelled the job, and the message gives its reason. Run the node
again to start a new job.

### The video job expired before it finished

The job expired at OpenRouter. Run the node again to start a new job.

### Choose an unfinished video job from the list

**Video: Download** names no recorded job. Press R to refresh the list, then
choose a job.

### An earlier identical video request may have been accepted

An identical request is on hold after an uncertain submission. Wait the minutes
the message names, or check openrouter.ai/activity for the job.

### The connection closed before OpenRouter confirmed the video request

The video request may be running and billed; check openrouter.ai/activity. The
identical request is held for **resubmit hold (minutes)**.

### OpenRouter's video address was not on openrouter.ai

The finished job named a download address outside openrouter.ai, so the key
was not sent there. Try **Video: Download** again later.

### OpenRouter's model list could not be read

A refresh or check could not reach OpenRouter's public lists. Check the
connection and select **Refresh Models** again.

### OpenRouter's model list had an unexpected format

OpenRouter's public list could not be read as expected, so the saved list was
kept. Try again later.

### OpenRouter's model list grew more than expected in one refresh

The new list added far more models than the saved one holds, so the saved list
was kept. Try again later.

### OpenRouter's model list was much shorter than the saved one

The new list held fewer than half the saved models, so the saved list was kept.
Try again later.

### A model refresh is already running

Wait for the refresh to finish before starting another or restoring the
previous list.

### Choose a model ID from the list or type one in the form author/model

The **model ID** of **other model ID** is empty or not in the form
`author/model`. Type the full ID, such as `openai/gpt-audio-mini`.
