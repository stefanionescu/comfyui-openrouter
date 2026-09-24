# Image: Generate

Generates or edits images with any image model on OpenRouter. Each run is one
paid request; prices are in **OpenRouter models**.

## Inputs

| Input                      | What it takes                                                                                             |
| -------------------------- | --------------------------------------------------------------------------------------------------------- |
| `prompt`                   | What to draw or change.                                                                                   |
| `model`                    | Any image model; the default is `google/gemini-3.1-flash-image`. Choose **other model ID** to type an ID. |
| `model.resolution`         | The size, such as `1K` or `4K`.                                                                           |
| `model.aspect_ratio`       | The shape, such as `16:9`.                                                                                |
| `model.quality`            | The quality.                                                                                              |
| `model.background`         | `transparent`, `opaque`, or `auto`. A transparent background needs PNG or WebP.                           |
| `model.output_format`      | `png`, `jpeg`, `webp`, or `svg` for vector models.                                                        |
| `model.output_compression` | JPEG and WebP quality.                                                                                    |
| `model.count`              | How many images to make.                                                                                  |
| `model.references`         | Images to edit or combine, one per socket. Every image in a batch is sent.                                |
| `seed`                     | Varies the output, for models that take a seed.                                                           |
| `variation`                | **run number**: change it to send the same request again.                                                 |
| `options`                  | Settings from **Request Options**.                                                                        |

The settings under **model** show the values the chosen model offers.
**model default** uses the model's own default.

## Outputs

| Output   | What it carries                                                                               |
| -------- | --------------------------------------------------------------------------------------------- |
| `images` | The images. Connected nodes are skipped when it is empty.                                     |
| `masks`  | One mask per image, from its transparency. White is transparent; opaque images are all black. |
| `svg`    | The SVG files a vector model made, for **Save SVG**.                                          |

## Use

1. Write the prompt and choose the model.
2. Connect any reference images.
3. Connect **images** to **Save Image**, or **svg** to **Save SVG**, and select
   **Run**.

Examples: **image-01-pick-the-best-image-for-an-occasion** and
**image-04-design-a-logo**. FLUX models return JPEG unless you choose `png`, and
JPEG is always opaque. OpenRouter bills only completed images.

[OpenRouter image generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
