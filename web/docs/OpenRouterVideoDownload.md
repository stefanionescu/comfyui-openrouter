# Video: Download

Downloads a video that OpenRouter kept making after a run stopped: you cancelled
it, ComfyUI restarted, or it waited too long.

## Inputs

| Input | What it takes                                                               |
| ----- | --------------------------------------------------------------------------- |
| `job` | A video job started on this server, shown as its ID, model, and start time. |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Use

1. Choose the job in **job**. Press R to list jobs started after the page
   loaded.
2. Connect **video** to **Save Video**.
3. Select **Run**.

A job leaves the list once its video is downloaded, or when it fails, is
cancelled, or expires. Example: **video-02-recover-a-cancelled-video**.

[OpenRouter video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
