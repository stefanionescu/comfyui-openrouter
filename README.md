# ![comfyui-openrouter: a ComfyUI extension that runs any OpenRouter model](docs/images/banner.svg)

[![ComfyUI 0.34.6 or later](docs/images/badge-comfyui.svg)](#requirements)
[![Frontend 1.49.6 or later](docs/images/badge-frontend.svg)](#requirements)
[![Python 3.12 or later](docs/images/badge-python.svg)](#requirements)
[![MIT license](docs/images/badge-license.svg)](LICENSE.md)

Run any OpenRouter model in ComfyUI with your own API key.

- **Chat:** ask with images, video, audio, or documents; get text, images, or
  speech.
- **Image:** generate and edit images, with masks and SVG files.
- **Video:** make a video from a prompt, frames, or references.
- **Audio:** text to speech, with voice cloning, and transcription with
  timestamps and subtitles.
- **Search:** embed and rank text and images.
- **Decision:** ask a decision model, such as TypeSafe's Jev, typed questions
  and get probabilities.
- **Request Options:** providers, price limits, and extra request fields for any
  paid node.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [First run](#first-run)
- [Example workflows](#example-workflows)
- [Nodes](#nodes)
- [Models](#models)
- [How a run works](#how-a-run-works)
- [Development](#development)
- [Common problems](#common-problems)
- [License](#license)

## Requirements

- Python 3.12 or later.
- ComfyUI 0.34.6 or later, with frontend 1.49.6 or later in the 1.x series.
- An OpenRouter API key.

## Install

Put the extension in `ComfyUI/custom_nodes/comfyui-openrouter`, install its
`requirements.txt` with ComfyUI's Python, and restart ComfyUI.

### Comfy Desktop

1. In the instance chooser, select the **⋮** icon on the instance card, then
   **Manage**.
2. Under **About**, copy **Location**. In that folder, find the `ComfyUI` folder
   that holds `main.py`, and put the extension in its `custom_nodes` folder.
3. Select **Terminal** in the same panel and run:

```sh
pip install -r custom_nodes/comfyui-openrouter/requirements.txt
```

### macOS or Linux

From the ComfyUI folder:

```sh
.venv/bin/python -m pip install -r custom_nodes/comfyui-openrouter/requirements.txt
```

With uv:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/comfyui-openrouter/requirements.txt
```

### Windows

From the ComfyUI folder, in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\comfyui-openrouter\requirements.txt
```

### Windows portable

From the folder that holds `ComfyUI` and `python_embeded`, in PowerShell:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\comfyui-openrouter\requirements.txt
```

To update or remove the extension, see the
[advanced guide](ADVANCED.md#update-or-remove).

## First run

1. Save your API key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter
   settings**.
2. Open **Browse Templates → comfyui-openrouter →
   decision-01-verify-then-escalate** and select **Run**.
3. Read the answer in **Answer**, and Jev's check in **Summary**.

To send the same request again, change **run number**.

## Example workflows

| Workflow                                                                                                          | Input                               |
| ----------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| [Chat: Write a Product Listing](example_workflows/chat-01-write-a-product-listing.json)                           | Two product photos and a spec sheet |
| [Chat: Caption a Training Set](example_workflows/chat-02-caption-a-training-set.json)                             | A folder of images                  |
| [Image: Pick the Best Image for an Occasion](example_workflows/image-01-pick-the-best-image-for-an-occasion.json) | A brief                             |
| [Image: Reject Distorted Images](example_workflows/image-02-reject-distorted-images.json)                         | A subject                           |
| [Image: Edit with the Best Idea](example_workflows/image-03-edit-with-the-best-idea.json)                         | A product photo and a campaign      |
| [Image: Design a Logo](example_workflows/image-04-design-a-logo.json)                                             | A brand description                 |
| [Video: Animate a Product Shot](example_workflows/video-01-animate-a-product-shot.json)                           | A brief                             |
| [Video: Recover a Cancelled Video](example_workflows/video-02-recover-a-cancelled-video.json)                     | A cancelled video job               |
| [Audio: Triage a Voicemail](example_workflows/audio-01-triage-a-voicemail.json)                                   | A voicemail                         |
| [Audio: Dub a Clip](example_workflows/audio-02-dub-a-clip.json)                                                   | A short clip of one speaker         |
| [Search: Answer from Help Articles](example_workflows/search-01-answer-from-help-articles.json)                   | A question and help articles        |
| [Search: Choose a Hero Image](example_workflows/search-02-choose-a-hero-image.json)                               | A brief                             |
| [Decision: Verify a Quick Answer, Then Escalate](example_workflows/decision-01-verify-then-escalate.json)         | Notes and a question                |

They are in **Browse Templates → comfyui-openrouter**. Start with each
workflow's **Start Here** note; each step is a subgraph. Media inputs start
empty.

![Screenshot of the Choose group in image-01: a note explains the step, two Decision: Add Question nodes hold Jev's questions, and the Choose subgraph node shows its inputs and its approved and review folders.](docs/images/workflow-choose-group.png)

After an update, open the examples in a new tab to get the new versions.

## Nodes

The nodes are under **OpenRouter** in the node menu, and each has a help page.

![Node map. Chat: Attach Document feeds Chat: Ask. Decision: Add Question feeds Decision: Ask, which feeds Decision: Read Answer. Request Options feeds any paid node. Video: Download collects a job Video: Generate left running, so no link joins them. Paid nodes have an indigo bar.](docs/images/node-map.svg)

| Node                                                                | What it does                                                           | Paid |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---- |
| [Chat: Ask](web/docs/OpenRouterChatAsk.md)                          | Asks a model a question, with images, video, audio, or documents.      | Yes  |
| [Chat: Attach Document](web/docs/OpenRouterChatAttachDocument.md)   | Attaches a PDF or text file from ComfyUI's input folder.               | No   |
| [Image: Generate](web/docs/OpenRouterImageGenerate.md)              | Generates or edits images, with masks and SVG files.                   | Yes  |
| [Video: Generate](web/docs/OpenRouterVideoGenerate.md)              | Makes a video from a prompt, frames, or reference media.               | Yes  |
| [Video: Download](web/docs/OpenRouterVideoDownload.md)              | Downloads a video that OpenRouter kept making after a run stopped.     | No   |
| [Audio: Speak](web/docs/OpenRouterAudioSpeak.md)                    | Turns text into speech, optionally in a cloned voice.                  | Yes  |
| [Audio: Transcribe](web/docs/OpenRouterAudioTranscribe.md)          | Turns speech into text, with timed segments, words, and subtitles.     | Yes  |
| [Search: Embed](web/docs/OpenRouterSearchEmbed.md)                  | Turns text and images into embeddings and compares them.               | Yes  |
| [Search: Rank](web/docs/OpenRouterSearchRank.md)                    | Ranks text and images by how well they match a query.                  | Yes  |
| [Decision: Add Question](web/docs/OpenRouterDecisionAddQuestion.md) | Adds a yes-or-no, one-choice, or score question.                       | No   |
| [Decision: Ask](web/docs/OpenRouterDecisionAsk.md)                  | Asks a decision model, such as Jev, the questions about a situation.   | Yes  |
| [Decision: Read Answer](web/docs/OpenRouterDecisionReadAnswer.md)   | Reads one answer as text, a yes flag, and numbers.                     | No   |
| [Request Options](web/docs/OpenRouterRequestOptions.md)             | Sets providers, price limits, and extra request fields for paid nodes. | No   |

The decision nodes use OpenRouter's alpha decisions API
(`/api/alpha/decisions`), which OpenRouter may still change.

## Models

Each paid node takes any model ID from
[openrouter.ai/models](https://openrouter.ai/models), with an optional variant
suffix such as `:nitro`.

![Chat: Ask on the canvas: sockets for a conversation, documents, images, videos, audio, and options; then the model field set to google/gemini-3.5-flash, the reasoning effort, max tokens, temperature, outputs, aspect ratio, voice, PDF engine, seed, and run number; and the answer schema, prompt, and system prompt boxes at the bottom.](docs/images/chat-ask-node.png)

Before sending, the node checks the model against OpenRouter's public listings
and stops if the ID is unknown, the model makes something else, or it does not
take what you connected or chose. The error names what the model does take. The
[advanced guide](ADVANCED.md#models) lists every check and each node's default
model.

Each media socket, such as **images**, takes one item, a batch, or a list, and
everything connected goes in one request, each image at its own size. Join
several **Load Image** nodes with **Create List**.

## How a run works

1. The node checks its inputs and the model, and stops before anything is
   paid.
2. At most **parallel requests** requests run at once; the default is 4.
3. It sends one request with your key. A video job is recorded, checked until
   ready, and downloaded.
4. Nodes connected to an empty output, such as `images` from a text-only model,
   are skipped.

The [advanced guide](ADVANCED.md#what-each-node-sends) lists what each node
sends and returns.

## Development

Development needs mise. Point the checks at ComfyUI in `.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Install the tools, dependencies, and Git hooks, and run the full check:

```shell
mise trust
mise run repo:setup
mise run repo:check
```

Restart ComfyUI after changing Python. After changing the browser code, run
`mise run comfy:frontend:build`; after changing a workflow description, run
`mise run comfy:workflows:build`. The [advanced guide](ADVANCED.md#development)
lists every task.

## Common problems

| Problem                                      | Fix                                                                                                                                    |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| No OpenRouter nodes in the menu              | Check that the folder is `ComfyUI/custom_nodes/comfyui-openrouter`, ComfyUI is 0.34.6 or later, and the console shows no import error. |
| No **OpenRouter** entry under **Extensions** | Check that `web/extension.js` exists in the extension's folder, then reload the window.                                                |
| The settings cannot be changed               | ComfyUI runs in multi-user mode or is open from another computer. Set `OPENROUTER_API_KEY` where ComfyUI starts instead.               |
| `pydantic` cannot be imported                | Install `requirements.txt` with the Python that runs ComfyUI, then restart.                                                            |
| Node help is missing                         | Reinstall the whole extension, including `web/docs`.                                                                                   |
| The templates are missing                    | Reinstall the whole extension, including `example_workflows`.                                                                          |
| Nodes or menus appear twice                  | Keep one `comfyui-openrouter` folder in `custom_nodes`; move copies elsewhere.                                                         |

More in the [advanced guide's troubleshooting](ADVANCED.md#troubleshooting).

## License

[MIT](LICENSE.md).
