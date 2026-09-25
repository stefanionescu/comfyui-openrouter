# Chat: Attach Document

Attaches a PDF or text file from ComfyUI's input folder to **Chat: Ask**. Chain
several of these nodes to attach several files.

## Inputs

| Input       | What it takes                                                                  |
| ----------- | ------------------------------------------------------------------------------ |
| `file`      | A PDF, text, Markdown, CSV, or JSON file at the top of ComfyUI's input folder. |
| `documents` | Documents from another **Chat: Attach Document**. One request takes up to 8.   |

## Outputs

| Output      | What it carries                                         |
| ----------- | ------------------------------------------------------- |
| `documents` | The earlier documents plus this one, for **Chat: Ask**. |

## Use

1. Put the file in ComfyUI's input folder and press R to refresh the list.
2. Choose it in **document**.
3. Connect **documents** to **Chat: Ask**.

**Chat: Ask**'s **PDF engine** sets how OpenRouter reads a PDF. A text file must
be UTF-8. An edited file is read again on the next run.
Example: **chat-01-write-a-product-listing**.

[OpenRouter PDF documentation](https://openrouter.ai/docs/guides/overview/multimodal/pdfs)
