# OpenRouter Advanced Guide

Use this guide for model support, request options, media, and video recovery.
For installation, see the [README](README.md). Node help covers
[individual inputs and outputs](README.md#nodes).

## Keys and access

Save your API key in **Extensions > OpenRouter > OpenRouter Settings** from the
ComfyUI menu. The key stays on the server and out of saved workflows.
`OPENROUTER_API_KEY`, set where ComfyUI starts, overrides the saved key.

Only a direct local, single-user connection can change the key or settings.
For remote access, a reverse proxy, or multi-user mode, set `OPENROUTER_API_KEY`
on the ComfyUI server and restart it.

The extension stores settings, credentials, and task records in this private folder:

| System  | Folder                                               |
| ------- | ---------------------------------------------------- |
| macOS   | `~/Library/Application Support/OpenRouterComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/openrouter-comfy` |
| Windows | `%LOCALAPPDATA%\OpenRouterComfyUI`                   |

Set `OPENROUTER_COMFY_STATE_DIRECTORY` to use another absolute path outside
the extension and ComfyUI's folders. The extension writes unencrypted files with owner-only permissions.

## Settings

Change limits in **OpenRouter Settings**. New requests use the saved values;
changing settings does not cancel active work. Model limits also apply.

| Setting                     | Default | Range      | What it limits                                          |
| --------------------------- | ------- | ---------- | ------------------------------------------------------- |
| Request timeout (seconds)   | 180     | 10 to 3600 | How long one generation may take; for a video, the job. |
| Maximum upload size (MiB)   | 64      | 1 to 512   | The media and documents in one request.                 |
| Maximum download size (MiB) | 512     | 16 to 4096 | The largest reply, image, audio, or video accepted.     |

## Models

Use the model ID after `openrouter.ai/`, with an optional variant suffix such
as `:nitro`. The extension reads each public capability listing once per model
per ComfyUI session. **Model: Info** returns that listing without a key or
a paid generation.

Each node starts with a model for its task. The [node help](README.md#nodes)
lists the default model and supported fields.

The node checks the model's task, media support, and supported settings.
Chat checks output modalities, sampling settings, `stop`, structured output,
and token limits. Image and video nodes check their listed sizes, counts,
durations, frames, and reference capabilities. Voice cloning requires a model
that supports it.

The node sends `seed` and `reasoning_effort` only to models that support them. An unavailable
reasoning level selects the highest supported level below it, or the lowest
supported level if none is lower. The node sends other optional settings when you change them from their
documented defaults. **Audio: Speak** starts with voice `Kore` for
its default model.

## Media and outputs

Chat accepts one media item, a batch, or a list in one request. Join several
**Load Image** nodes with **Create List**. Images keep their individual sizes.
The extension sends local images, video, and audio as PNG, MP4, and WAV
respectively. PDFs use the selected PDF engine; text documents go as text.

`conversation` carries earlier chat turns. Outputs can include text, reasoning,
images, or speech according to the model. ComfyUI skips connected nodes when their output is empty. Chat speech returns 24 kHz mono PCM.

**Image: Generate** returns images, masks, and SVG files where supported.
White in a mask means transparency. Video returns MP4. **Audio: Transcribe**
can return segments, timed words, and SRT subtitles. Search nodes compare
embeddings or rank items. See each [node help](README.md#nodes) for details.

## Request options

Connect **Request Options** for provider routing, privacy requirements,
price limits, and extra request fields. The extension submits requests once
and disables provider fallback where routing supports it.

If no provider can satisfy the request, check model support and your options.
Changing `zdr` changes the privacy requirement; raising price limits changes
the permitted cost. Review those effects before relaxing either setting.
See [Request Options](web/docs/OpenRouterRequestOptions.md).

Decision nodes use OpenRouter's alpha decisions API. The API may change.
Keep decision questions and answer types consistent when chaining its nodes.

## Caching and reruns

Change `run_number` to send another request with unchanged inputs.
A non-fixed `seed` changes after each run and causes another request;
the examples use `fixed`. A different effective key invalidates cached results;
changing request limits does not.

Cancelling stops the wait. Chat can still charge for completed tokens,
and accepted video jobs continue.

## Recover a video

The extension records video jobs when OpenRouter accepts them. A job can continue
after cancellation, a restart, or a timeout. Use **Video: Download** to collect
it; press R to refresh the list.

A record leaves the list after download or when OpenRouter reports it as failed,
cancelled, or expired. Recover the existing job before submitting another video.

## Troubleshooting

| Symptom                           | Action                                                                                    |
| --------------------------------- | ----------------------------------------------------------------------------------------- |
| The key is rejected               | Check `OPENROUTER_API_KEY`, which overrides the saved key.                                |
| A request is blocked              | Check the provider's reason, account guardrails, and key permissions.                     |
| No provider can serve the request | Check model capabilities and [request options](#request-options).                         |
| An answer stops early             | Check `max_tokens` before requesting another answer.                                      |
| Inputs are rejected               | Check the node help; do not combine video frames and references.                          |
| Requests are rate-limited         | Wait before trying again, or reduce simultaneous paid nodes.                              |
| A video outlives ComfyUI          | Collect its recorded job with **Video: Download**.                                        |
| Settings cannot be changed        | Connect directly from localhost; use the environment key for remote or multi-user access. |

For an unknown setting or an oversized state file:

Stop ComfyUI and back up the affected file in the private state folder.
To reset limits, remove only `settings.json`, then restart. Keep task records
until you have recovered their outputs. Do not delete the whole state folder
to reset a setting.

## Update or remove

To update, replace `custom_nodes/openrouter`, install its runtime requirements with ComfyUI's Python, and restart
ComfyUI. Open updated examples in a new tab.

To remove the extension, move its folder outside `custom_nodes` and restart.
Private state and saved media remain. Back up state and recover outstanding
tasks before deleting the private folder: that removes the saved key,
settings, and task records. Removing a saved key does not revoke it with the provider.
