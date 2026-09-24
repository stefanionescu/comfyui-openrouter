# Video: Generate

Makes a video with any video model on OpenRouter, from a prompt, first and last
frames, or reference media. Each run is one paid request, priced per second of
video; prices are in **OpenRouter models**.

## Inputs

| Input                    | What it takes                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| `prompt`                 | What the video shows. It can be empty when a first frame is connected.                          |
| `model`                  | Any video model; the default is `google/veo-3.1-fast`. Choose **other model ID** to type an ID. |
| `model.duration`         | The length in seconds. The shortest is the default.                                             |
| `model.resolution`       | The resolution.                                                                                 |
| `model.aspect_ratio`     | The shape.                                                                                      |
| `model.generate_audio`   | Whether the video has sound.                                                                    |
| `model.first_frame`      | One image the video starts from.                                                                |
| `model.last_frame`       | One image the video ends on.                                                                    |
| `model.reference_images` | Images the video follows. Leave the frames empty to use them.                                   |
| `model.reference_videos` | Videos the video follows.                                                                       |
| `model.reference_audio`  | Audio the video follows.                                                                        |
| `model.upscale_factor`   | How much an upscaling model enlarges the video.                                                 |
| `model.creativity`       | How much detail an upscaling model adds.                                                        |
| `seed`                   | Varies the output, for models that take a seed.                                                 |
| `variation`              | **run number**: change it to send the same request again.                                       |
| `options`                | Settings from **Request Options**.                                                              |

The settings under **model** show what the chosen model accepts.

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Use

1. Write the prompt, choose the model and duration, and connect any frames.
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
