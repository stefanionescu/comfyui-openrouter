# Chat: Attach Document

Attach a PDF or text file from ComfyUI's input folder to **Chat: Ask**. Each node adds one file to the documents it receives, so several nodes in a row attach several files. It sends nothing to OpenRouter.

## Inputs

| Input       | What it takes                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------ |
| `file`      | A PDF, text, Markdown, CSV, or JSON file at the top of ComfyUI's input folder.                   |
| `documents` | The earlier documents, from another **Chat: Attach Document**; up to 8 documents in one request. |

## Outputs

| Output      | What it carries                                                      |
| ----------- | -------------------------------------------------------------------- |
| `documents` | The earlier documents and this one, for **Chat: Ask**'s `documents`. |

## Run

1. To start from a finished workflow, open **chat-01-write-a-product-listing** from **Browse Templates → comfyui-openrouter**.
1. Put the file in ComfyUI's input folder and press R so the list shows it.
1. Choose it in **document** and connect **documents** to **Chat: Ask**.

A PDF is sent as a file, and OpenRouter reads it for models without file input; **Chat: Ask**'s **PDF reader** chooses how. A text file is sent as text and must be UTF-8. Each file counts toward the maximum upload size in OpenRouter settings. An edited file is read again on the next run.

[OpenRouter PDF documentation](https://openrouter.ai/docs/guides/overview/multimodal/pdfs)
