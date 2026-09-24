# Image: Generate

Generates or edits images with any image model on OpenRouter.

## Inputs

| Input                | What it takes                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------- |
| `model`              | Any image model ID from openrouter.ai/models; the default is `google/gemini-3.1-flash-image`. |
| `resolution`         | The size, such as `1K` or `4K`.                                                               |
| `aspect_ratio`       | The shape, such as `16:9`.                                                                    |
| `quality`            | The quality.                                                                                  |
| `background`         | `transparent`, `opaque`, or `auto`. A transparent background needs PNG or WebP.               |
| `output_format`      | `png`, `jpeg`, `webp`, or `svg` for vector models.                                            |
| `output_compression` | JPEG and WebP quality.                                                                        |
| `count`              | How many images to make.                                                                      |
| `references`         | Images to edit or combine, one per socket. Every image in a batch is sent.                    |
| `seed`               | Varies the output, for models that take a seed.                                               |
| `run_number`         | Change it to send the same request again.                                                     |
| `prompt`             | What to draw or change.                                                                       |
| `options`            | Settings from **Request Options**.                                                            |

**model default** sends nothing, so the model uses its own default.

## Outputs

| Output   | What it carries                                                                               |
| -------- | --------------------------------------------------------------------------------------------- |
| `images` | The images. Connected nodes are skipped when it is empty.                                     |
| `masks`  | One mask per image, from its transparency. White is transparent; opaque images are all black. |
| `svg`    | The SVG files a vector model made, for **Save SVG**.                                          |

## Use

1. Write the prompt and type the model ID.
2. Connect any reference images.
3. Connect **images** to **Save Image**, or **svg** to **Save SVG**, and select
   **Run**.

Examples: **image-01-pick-the-best-image-for-an-occasion** and
**image-04-design-a-logo**. FLUX models return JPEG unless you choose `png`, and
JPEG is always opaque.

[OpenRouter image generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
