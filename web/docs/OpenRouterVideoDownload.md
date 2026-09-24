# Video: Download

Collect a video job that kept running after a cancel or a restart. Connect **video** to **Save Video**. It only checks the job and downloads the video, which costs nothing more.

## Inputs

| Input | What it takes                                                                                      |
| ----- | -------------------------------------------------------------------------------------------------- |
| `job` | An unfinished video job recorded on this server, shown as its ID, model, and the time it was sent. |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Run

1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Choose the job in **unfinished job**. Press R to list jobs recorded later.
1. Select **Run**.

The list holds the jobs **Video: Generate** recorded on this server and did not finish collecting. A job's record is removed after its video downloads, or when OpenRouter reports that it failed, was cancelled, or expired.

[OpenRouter video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
