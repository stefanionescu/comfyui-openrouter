# Image: Generate

Generate or edit images with any OpenRouter image model. Connect **images** to **Save Image**, and **svg** to **Save SVG** for vector models. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input                      | What it takes                                                                                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `prompt`                   | What to draw or change.                                                                                                       |
| `model`                    | Every model in OpenRouter's image list; by default `google/gemini-3.1-flash-image`. Choose **other model ID** to type any ID. |
| `model.resolution`         | The size class, such as `1K` or `4K`, from the values the model lists.                                                        |
| `model.aspect_ratio`       | The shape, such as `16:9`, from the values the model lists.                                                                   |
| `model.quality`            | The quality, from the values the model lists.                                                                                 |
| `model.background`         | `transparent`, `opaque`, or `auto`. A transparent background needs PNG or WebP.                                               |
| `model.output_format`      | The file format: `png`, `jpeg`, `webp`, or `svg` for vector models.                                                           |
| `model.output_compression` | JPEG and WebP quality, from the model's range.                                                                                |
| `model.count`              | How many images to make, within the model's range.                                                                            |
| `model.references`         | Images to edit or combine, one per socket, up to the model's limit. Every image of a batch is sent.                           |
| `seed`                     | Number used by the model to vary its output, sent when the model accepts a seed.                                              |
| `variation`                | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.                   |
| `options`                  | From **Request Options**, to choose providers or pass extra fields.                                                           |

## Outputs

| Output   | What it carries                                                                                              |
| -------- | ------------------------------------------------------------------------------------------------------------ |
| `images` | A list of the raster images, each at its own size; the nodes connected to it do not run when there are none. |
| `masks`  | A list with one mask per raster image, from its transparency; zeros for an opaque image.                     |
| `svg`    | Every SVG file a vector model made, for ComfyUI's **Save SVG**.                                              |

## Run

1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the prompt, choose the model, and connect any reference images.
1. Select **Run**.

Each control under **model** starts at **model default**, which sends nothing and leaves the value to the model. FLUX models return JPEG unless you choose `png`; JPEG has no transparency, so its mask is empty. A failed image request is not billed: OpenRouter bills only completed images.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter image generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
