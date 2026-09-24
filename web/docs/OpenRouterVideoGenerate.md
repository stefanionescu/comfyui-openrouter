# Video: Generate

Makes a video with any video model on OpenRouter, from a prompt, first and last
frames, or reference media. Each run is one paid request, priced per second of
video; prices are at openrouter.ai/models.

## Inputs

| Input              | What it takes                                                                       |
| ------------------ | ----------------------------------------------------------------------------------- |
| `prompt`           | What the video shows. It can be empty when a first frame is connected.              |
| `model`            | Any video model ID from openrouter.ai/models; the default is `google/veo-3.1-fast`. |
| `duration`         | The length in seconds; 0 leaves it to the model.                                    |
| `resolution`       | The resolution.                                                                     |
| `aspect_ratio`     | The shape.                                                                          |
| `generate_audio`   | Whether the video has sound.                                                        |
| `first_frame`      | One image the video starts from.                                                    |
| `last_frame`       | One image the video ends on.                                                        |
| `reference_images` | Images the video follows. Leave the frames empty to use them.                       |
| `reference_videos` | Videos the video follows.                                                           |
| `reference_audio`  | Audio the video follows.                                                            |
| `upscale_factor`   | How much an upscaling model enlarges the video; 0 sends nothing.                    |
| `creativity`       | How much detail an upscaling model adds; 0 sends nothing.                           |
| `seed`             | Varies the output, for models that take a seed.                                     |
| `variation`        | **run number**: change it to send the same request again.                           |
| `options`          | Settings from **Request Options**.                                                  |

A setting left at **model default** or 0 sends nothing, so the model uses its own
default.

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Use

1. Write the prompt, type the model ID and duration, and connect any frames.
2. Connect **video** to **Save Video**.
3. Select **Run**. A video takes from half a minute to several minutes.

Example: **video-01-animate-a-product-shot**.

A video job always runs to completion at OpenRouter and is billed, even if you
cancel the run or ComfyUI restarts; download it with **Video: Download**.
Running the identical request again picks up that job. If the connection closes before OpenRouter
confirms a request, the identical request is refused for **resubmit hold
(minutes)**; check openrouter.ai/activity meanwhile. Reference videos count
toward the maximum upload size.

[OpenRouter video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
