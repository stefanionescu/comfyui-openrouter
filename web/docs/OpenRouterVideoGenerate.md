# Video: Generate

Makes a video with any video model on OpenRouter, from a prompt, first and last
frames, or reference media.

## Inputs

| Input              | What it takes                                                                          |
| ------------------ | -------------------------------------------------------------------------------------- |
| `model`            | Any video model ID from openrouter.ai/models; the default is `google/veo-3.1-fast`.    |
| `duration`         | The length in seconds; 0 leaves it to the model.                                       |
| `resolution`       | The resolution.                                                                        |
| `aspect_ratio`     | The shape.                                                                             |
| `generate_audio`   | Whether the video has sound.                                                           |
| `upscale_factor`   | How much an upscaling model enlarges the video; 0 sends nothing.                       |
| `creativity`       | How much detail an upscaling model adds; 0 sends nothing.                              |
| `reference_images` | Images the video follows: one, a batch, or a list. Leave the frames empty to use them. |
| `reference_videos` | Videos the video follows: one or a list.                                               |
| `reference_audio`  | Audio the video follows: one, a batch, or a list.                                      |
| `seed`             | Varies the output, for models that take a seed.                                        |
| `run_number`       | Change it to send the same request again.                                              |
| `prompt`           | What the video shows. It can be empty when a first frame is connected.                 |
| `first_frame`      | One image the video starts from; a batch or list is refused.                           |
| `last_frame`       | One image the video ends on; a batch or list is refused.                               |
| `options`          | Settings from **Request Options**.                                                     |

A setting left at **model default** or 0 sends nothing, so the model uses its
own default. Before anything is paid, the node reads the model's entry in
OpenRouter's video list and refuses a duration, resolution, aspect ratio, frame,
sound, or upscale setting the model does not take, naming what it does take.

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Use

1. Write the prompt, type the model ID and duration, and connect any frames.
2. Connect **video** to **Save Video**.
3. Select **Run**. A video takes from half a minute to several minutes.

Example: **video-01-animate-a-product-shot**.

A video job always runs to completion at OpenRouter, even if you cancel the run
or ComfyUI restarts; download it with **Video: Download**. Running the identical
request again picks up that job. If the connection closes before OpenRouter
confirms a request, the identical request is refused for **video retry delay
(minutes)**; check openrouter.ai/activity meanwhile. Reference videos count
toward the maximum upload size.

[OpenRouter video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
