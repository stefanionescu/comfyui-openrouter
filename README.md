# ComfyUI OpenRouter

ComfyUI OpenRouter is a ComfyUI extension that runs any model on OpenRouter
with your own API key. Its nodes cover six kinds of work:

- **Chat** asks any chat model a question, with images, video, audio, and
  documents, and returns text, reasoning, images, or speech.
- **Image** generates and edits images, with masks and SVG files.
- **Video** makes a video from a prompt, frames, or references, and collects
  a video that kept running after a cancel.
- **Audio** turns text into speech, in a copied voice if you want, and speech
  into text, timed segments, timed words, and subtitles.
- **Search** turns text and images into embeddings, lists of numbers that put
  similar items close together, and ranks them against a query.
- **Decisions** answer typed questions with Jev, OpenRouter's decision model.
  Jev answers with probabilities instead of text, so its answers can switch
  what a workflow does next.

Separate parts handle separate concerns:

- OpenRouter passes each request to the model's provider and bills your
  OpenRouter account.
- This extension checks each input against the chosen model before it sends
  anything, sends the request from your ComfyUI server with your key, and
  turns the reply into ComfyUI images, video, audio, and text.
- ComfyUI's own save nodes write the files.

Every run of a paid node sends a paid request. Check the model, its price in
**OpenRouter models**, and how many runs a list of inputs causes before you
press **Run**. Models make mistakes: review generated media, text, and Jev's
answers before you rely on them.

This is not ComfyUI's built-in OpenRouter node, which bills your Comfy account
and offers a fixed list of models.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Make your first request](#make-your-first-request)
- [Choose a workflow](#choose-a-workflow)
- [Nodes](#nodes)
- [Find and refresh models](#find-and-refresh-models)
- [How a run works](#how-a-run-works)
- [Develop the extension](#develop-the-extension)
- [Fix a setup problem](#fix-a-setup-problem)
- [Advanced guide](#advanced-guide)

## Requirements

- **Python 3.12 or later** in the environment that runs ComfyUI.
- **ComfyUI 0.34.6 or later**, with **frontend 1.49.6 or later** within the
  1.x series. Older versions do not show the per-model controls or the
  OpenRouter dialogs.
- An **OpenRouter account** with credits, and an API key from
  openrouter.ai/settings/keys.
- Network access from the ComfyUI server to openrouter.ai.

No model weights are downloaded.

## Install

The extension includes its built browser files. You do not need Bun, mise, or
development dependencies to use it.

1. Stop ComfyUI after active work finishes.
2. Place the extension at `ComfyUI/custom_nodes/comfyui-openrouter`. Put
   `__init__.py` and `requirements.txt` directly inside that folder.
3. Install `requirements.txt` using the Python environment that runs ComfyUI.
   Choose the command below for your installation.
4. Start ComfyUI, then refresh its window.

### Comfy Desktop

1. On the home screen, open the installation's **⋮** menu and select **Manage**.
2. Open **About** and copy **Location** to find the installation folder. Inside it,
   find the `ComfyUI` folder containing `main.py` and place the extension at
   `custom_nodes/comfyui-openrouter`.
3. Open **Terminal** in the same Manage panel. Desktop opens the ComfyUI folder
   and activates that installation's Python environment. Run:

```sh
pip install -r custom_nodes/comfyui-openrouter/requirements.txt
```

Start the installation after the command finishes. See
[Comfy Desktop's Manage panel](https://docs.comfy.org/installation/desktop/usage/manage)
for the folder and terminal controls.

### Manual installation: macOS or Linux

Run from the ComfyUI directory. Replace `.venv` if your environment has another name:

```sh
.venv/bin/python -m pip install -r custom_nodes/comfyui-openrouter/requirements.txt
```

For a uv environment without pip, use:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/comfyui-openrouter/requirements.txt
```

### Manual installation: Windows

Run in PowerShell from the ComfyUI directory. Replace `.venv` if your virtual
environment has another name or location:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\comfyui-openrouter\requirements.txt
```

### Windows portable

Run in PowerShell from the folder containing `ComfyUI` and `python_embeded`:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\comfyui-openrouter\requirements.txt
```

See [update or remove](ADVANCED.md#update-or-remove) for later
package changes. Install only runtime requirements into ComfyUI's environment.

## Make your first request

1. Select the Comfy logo, then **Extensions → OpenRouter → OpenRouter settings**.
   Save your OpenRouter API key there. It stays on the server and out of workflows.
2. Open native **Browse Templates → comfyui-openrouter** and select
   **decision-01-verify-then-escalate**. You can also drag the
   [Decision: Verify a Quick Answer, Then Escalate](example_workflows/decision-01-verify-then-escalate.json)
   workflow onto the canvas. It needs no uploads.
3. Read the note at the top of each group, then edit **Notes** and **Question**.
4. Select **Run**.
5. Read the result in **Answer**, and Jev's check in **Summary**.

Use ComfyUI's cancel control to stop a run. Change **run number** to request
another run with unchanged inputs. OpenRouter lists each request's charge at
openrouter.ai/activity.

## Choose a workflow

The `example_workflows` folder holds 13 editable workflows built on real tasks.
Each one uses the newest models for its job. Jev, OpenRouter's decision model, then makes the call a person would otherwise make: which image to keep, whether a draft is distorted, or whether an answer is supported. Together they use
every node.

Open one from native **Browse Templates → comfyui-openrouter**, or drag its JSON
file onto ComfyUI. Each group has a note that says what it does, and the first
note, **Start Here**, lists the steps. Each step after the inputs is a subgraph:
select the icon at its top-right corner to see and change the nodes inside.
Examples need only native ComfyUI nodes and this extension. Media inputs start
empty; select your own image, audio, or document.

Several workflows route their results with ComfyUI's **If/Else Switch**, which
ComfyUI marks as beta. It runs only the branch it picks, so a paid node on the
other branch sends nothing.

After updating, open an example in a new tab. Existing graphs keep their saved
notes, prompts, and layout. Notes and node titles are saved in the graph in
English; changing the interface language does not translate them.

### Chat

| Workflow JSON                                                                           | Input                               | Guide                                                  |
| --------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------ |
| [Chat: Write a Product Listing](example_workflows/chat-01-write-a-product-listing.json) | Two product photos and a spec sheet | [Node guide](web/docs/OpenRouterChatAttachDocument.md) |
| [Chat: Caption a Training Set](example_workflows/chat-02-caption-a-training-set.json)   | A folder of images                  | [Node guide](web/docs/OpenRouterChatAsk.md)            |

### Images

| Workflow JSON                                                                                                     | Input                      | Guide                                                  |
| ----------------------------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------ |
| [Image: Pick the Best Image for an Occasion](example_workflows/image-01-pick-the-best-image-for-an-occasion.json) | Occasion brief             | [Node guide](web/docs/OpenRouterImageGenerate.md)      |
| [Image: Reject Distorted Images](example_workflows/image-02-reject-distorted-images.json)                         | Subject                    | [Node guide](web/docs/OpenRouterSearchEmbed.md)        |
| [Image: Edit with the Best Idea](example_workflows/image-03-edit-with-the-best-idea.json)                         | Product photo and campaign | [Node guide](web/docs/OpenRouterDecisionReadAnswer.md) |
| [Image: Design a Logo](example_workflows/image-04-design-a-logo.json)                                             | Brand brief                | [Node guide](web/docs/OpenRouterImageGenerate.md)      |

### Video

| Workflow JSON                                                                                 | Input                 | Guide                                             |
| --------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------- |
| [Video: Animate a Product Shot](example_workflows/video-01-animate-a-product-shot.json)       | Product brief         | [Node guide](web/docs/OpenRouterVideoGenerate.md) |
| [Video: Recover a Cancelled Video](example_workflows/video-02-recover-a-cancelled-video.json) | A cancelled video job | [Node guide](web/docs/OpenRouterVideoDownload.md) |

### Audio

| Workflow JSON                                                                   | Input                       | Guide                                               |
| ------------------------------------------------------------------------------- | --------------------------- | --------------------------------------------------- |
| [Audio: Triage a Voicemail](example_workflows/audio-01-triage-a-voicemail.json) | Voicemail recording         | [Node guide](web/docs/OpenRouterAudioTranscribe.md) |
| [Audio: Dub a Clip](example_workflows/audio-02-dub-a-clip.json)                 | A short clip of one speaker | [Node guide](web/docs/OpenRouterAudioSpeak.md)      |

### Search

| Workflow JSON                                                                                   | Input                          | Guide                                          |
| ----------------------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------- |
| [Search: Answer from Help Articles](example_workflows/search-01-answer-from-help-articles.json) | Customer question and articles | [Node guide](web/docs/OpenRouterSearchRank.md) |
| [Search: Choose a Hero Image](example_workflows/search-02-choose-a-hero-image.json)             | Hero brief                     | [Node guide](web/docs/OpenRouterSearchRank.md) |

### Decisions

| Workflow JSON                                                                                             | Input              | Guide                                           |
| --------------------------------------------------------------------------------------------------------- | ------------------ | ----------------------------------------------- |
| [Decision: Verify a Quick Answer, Then Escalate](example_workflows/decision-01-verify-then-escalate.json) | Notes and question | [Node guide](web/docs/OpenRouterDecisionAsk.md) |

**Request Options** appears in **Chat: Write a Product Listing**, where it keeps
the listing request away from providers that store data.

## Nodes

The nodes appear under **OpenRouter**, **OpenRouter/Chat**, **OpenRouter/Image**,
**OpenRouter/Video**, **OpenRouter/Audio**, **OpenRouter/Search**, and
**OpenRouter/Decision**. Each node's help page opens from ComfyUI's node help.

| Node                                                                | Use it to                                                                                 |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [Chat: Ask](web/docs/OpenRouterChatAsk.md)                          | Ask any chat model, with images, video, audio, or documents, for text, images, or speech. |
| [Chat: Attach Document](web/docs/OpenRouterChatAttachDocument.md)   | Attach a PDF or text file from ComfyUI's input folder.                                    |
| [Image: Generate](web/docs/OpenRouterImageGenerate.md)              | Generate or edit images, with masks and SVG files.                                        |
| [Video: Generate](web/docs/OpenRouterVideoGenerate.md)              | Make a video from a prompt, frames, or references.                                        |
| [Video: Download](web/docs/OpenRouterVideoDownload.md)              | Collect a video job that kept running after a cancel or a restart.                        |
| [Audio: Speak](web/docs/OpenRouterAudioSpeak.md)                    | Turn text into speech, optionally in a copied voice.                                      |
| [Audio: Transcribe](web/docs/OpenRouterAudioTranscribe.md)          | Turn speech into text, timed segments and words, and subtitles.                           |
| [Search: Embed](web/docs/OpenRouterSearchEmbed.md)                  | Turn text and images into vectors and compare them.                                       |
| [Search: Rank](web/docs/OpenRouterSearchRank.md)                    | Order text and images by how well they match a query.                                     |
| [Decision: Ask](web/docs/OpenRouterDecisionAsk.md)                  | Answer typed questions about a situation with probabilities.                              |
| [Decision: Add Question](web/docs/OpenRouterDecisionAddQuestion.md) | Add a yes-or-no, one-choice, or score question.                                           |
| [Decision: Read Answer](web/docs/OpenRouterDecisionReadAnswer.md)   | Turn one answer into text, a yes flag, and numbers.                                       |
| [Request Options](web/docs/OpenRouterRequestOptions.md)             | Choose providers, price caps, and extra request fields.                                   |

The decision nodes use OpenRouter's alpha decisions API. OpenRouter can change
it without notice, and a change can stop the decision nodes until the extension
is updated.

## Find and refresh models

The models that came with this version appear before the first refresh.

Open **Extensions → OpenRouter → OpenRouter models** to search the list, see
prices, and calculate a price. Select **Refresh Models** for current models and
prices; the node dropdowns then show the refreshed list.

**Refreshing the list does not install anything.** To use a model that is not listed, choose **other model ID** in any node's model dropdown and type the ID. The ID can include a suffix, such as `:online` for web search.

OpenRouter settings can enable automatic checks. They report changes; select
**Refresh Models** to save the updated list. See
[model updates](ADVANCED.md#model-updates) for how checks work and how to
restore a previous list.

## How a run works

```text
Node inputs ──▶ ComfyUI server (key and settings stay here)
                  │ checks inputs against the chosen model
                  ▼
               OpenRouter ──▶ the model's provider
                  │
                  ▼
Node outputs ◀── text, images, video, audio, and answers
```

1. A paid node reads its inputs and the chosen model's entry in the saved
   model list. It refuses an input the model cannot take before anything is
   sent, so a refused input costs nothing.
2. The node waits for a free slot. At most **parallel requests** requests are
   in flight at once; the default is 4.
3. The node sends one request from the ComfyUI server to OpenRouter with your
   key. OpenRouter passes it to the model's provider and bills your account.
4. **Video: Generate** records the video job, then checks its status until the
   video is ready and downloads it. The status checks and the download are not
   billed.
5. The node turns the reply into ComfyUI outputs. An output the model did not
   make, such as images from a text model, stops the nodes connected to it.
6. Your save nodes write the files. ComfyUI reuses a result while its inputs
   are unchanged. Change **run number** to send the same request again; each
   run is billed.

The [advanced guide](ADVANCED.md#run-architecture) lists what each node sends
and returns.

## Develop the extension

Development needs **Git** and **mise**. Point the checks at your ComfyUI
installation in `.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Install the toolchain, dependencies, and Git hooks, then run the complete check
before you push:

```shell
mise trust
mise run repo:setup
mise run repo:check
```

Restart ComfyUI after Python changes. Rebuild the browser files with
`mise run comfy:frontend:build` and the workflows with
`mise run comfy:workflows:build` after changing their sources. The [advanced
guide](ADVANCED.md#developer-workflow) lists every task and what it runs.

## Fix a setup problem

| Problem                                      | What to check                                                                                                                                 |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| No OpenRouter nodes in the menu              | The folder is `ComfyUI/custom_nodes/comfyui-openrouter`, ComfyUI is 0.34.6 or later, and the console shows no import error for the extension. |
| No **OpenRouter** entry under **Extensions** | `web/extension.js` exists in the extension's folder; reload the browser tab.                                                                  |
| "Set your OpenRouter API key..."             | Save the key in **OpenRouter settings**, or set `OPENROUTER_API_KEY` and restart ComfyUI.                                                     |
| Settings cannot be changed                   | ComfyUI runs in multi-user mode or is opened from another computer. Set `OPENROUTER_API_KEY` where ComfyUI starts instead.                    |
| A model is missing from a dropdown           | Select **Refresh Models** in **OpenRouter models**, or choose **other model ID** and type it.                                                 |
| "Value not in list" for a model              | The model left OpenRouter's list. Choose another model or type its ID in **other model ID**.                                                  |
| A video was not ready in time                | Add **Video: Download**, choose the job, and select **Run**. OpenRouter keeps making the video.                                               |
| `pydantic` cannot be imported                | Install `requirements.txt` with the Python that runs ComfyUI, then restart.                                                                   |
| Node help is missing                         | Restore the complete extension, including the guides under `web/docs`.                                                                        |
| Templates are missing                        | Confirm the extension includes `example_workflows`; you can also drag a JSON file from there onto ComfyUI.                                    |
| Duplicate nodes or menus appear              | Keep one `comfyui-openrouter` folder; move backups outside `custom_nodes`.                                                                    |

For the messages a node shows, read the [advanced guide](ADVANCED.md#troubleshooting).

Project-authored code, guides, and workflows use the [MIT license](LICENSE.md).
Third-party components keep their own license terms.

## Advanced guide

The [advanced guide](ADVANCED.md) is the reference. It covers:

- What leaves your computer, and what the extension saves.
- What each node sends, decides, and returns.
- Keys and access, request limits, and prices.
- Model updates and automatic checks.
- Caching and reruns, and recovering video jobs.
- Limits and defaults, and when a run stops.
- Updating and removing the extension, and the developer workflow.
- Changing messages and workflow notes.
- What each message means.
