# Video: Generate

Make a video with any OpenRouter video model, from a prompt, first and last frames, or references. Connect **video** to **Save Video**. Each run sends one paid OpenRouter request with your OpenRouter key, then checks the job until the video is ready.

## Inputs

| Input                    | What it takes                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `prompt`                 | What the video shows. It may be empty when a first frame is connected.                                              |
| `model`                  | Every model in OpenRouter's video list; by default `google/veo-3.1-fast`. Choose **other model ID** to type any ID. |
| `model.duration`         | The length in seconds, from the durations the model lists; the shortest is the default.                             |
| `model.resolution`       | The resolution, from the values the model lists.                                                                    |
| `model.aspect_ratio`     | The shape, from the values the model lists.                                                                         |
| `model.generate_audio`   | Whether the video has sound, for models that make sound.                                                            |
| `model.first_frame`      | One image the video starts from.                                                                                    |
| `model.last_frame`       | One image the video ends on, for models that take one.                                                              |
| `model.reference_images` | Images the video follows, for models that take references; leave the frames empty to use them.                      |
| `model.reference_videos` | Videos the video follows, for models that take them.                                                                |
| `model.reference_audio`  | Audio the video follows, for models that take it.                                                                   |
| `model.upscale_factor`   | How much an upscaling model enlarges the video.                                                                     |
| `model.creativity`       | How freely an upscaling model adds detail.                                                                          |
| `seed`                   | Number used by the model to vary its output, sent when the model accepts a seed.                                    |
| `variation`              | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.         |
| `options`                | From **Request Options**, to pass provider options.                                                                 |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `video` | The MP4 video.  |

## Run

1. To start from a finished workflow, open **video-01-animate-a-product-shot** from **Browse Templates → comfyui-openrouter**.
1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the prompt, choose the model and its duration, and connect any frames.
1. Select **Run**. Jobs take from half a minute to several minutes.

Video is priced per second. OpenRouter records the job as soon as it accepts it, and this extension keeps a private record of it. ComfyUI's cancel stops waiting but not the job, which OpenRouter keeps making and billing; collect it later with **Video: Download**. Running the identical request again resumes the recorded job instead of paying for a second one. When the connection closes before OpenRouter confirms the request, the identical request is held back for the **resubmit hold (minutes)** setting; check openrouter.ai/activity. Large reference videos count toward the maximum upload size in OpenRouter settings.

Review each video before you use it.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
