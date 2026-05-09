# markitdown-z

[English](./README.md) | [中文版](./README_zh.md)

> [!NOTE]
> This is an enhanced fork of [Microsoft MarkItDown](https://github.com/microsoft/markitdown), focused on table conversion, image extraction, and MCP support.

## Differences from Official Version

| Feature | Official | Enhanced |
|---------|----------|----------|
| Table Conversion | Basic support | Full rowspan/colspan expansion, merged cell handling |
| Image Extraction | Not supported | Full support via CLI and MCP |
| XLSX Enhancement | None | Handles merged cells, detects headers, cleans NaN values |
| MCP Server | Available | Available (richer features) |

## Installation

### From GitHub Release (Recommended)

```bash
pip install https://github.com/zz1151258647/markitdown/releases/download/v0.1.5.post3/markitdown_z-0.1.5.post3-py3-none-any.whl
```

### From source (Development)

```bash
git clone https://github.com/zz1151258647/markitdown.git
cd markitdown
pip install -e packages/markitdown
```

## Quick Start

### Command-Line

```bash
markitdown-z path-to-file.pdf -o document.md
```

### Python API

```python
from markitdown_z import MarkItDown

md = MarkItDown()
result = md.convert("document.docx")
print(result.text_content)
```

## Enhanced Features

### Image Extraction (CLI & MCP)

```bash
# CLI with image extraction
markitdown-z document.docx -o output.md -i --images-output-dir ./output
```

```python
# Python API with image extraction
from markitdown_z import MarkItDown
md = MarkItDown()
result = md.convert(
    "document.docx",
    extract_images=True,
    images_output_dir="output",
    images_prefix="img"
)
```

### MCP Server

The MCP server supports image extraction and file saving:

```python
convert_to_markdown(
    uri="file:///path/to/doc.docx",
    extract_images=True,
    images_output_dir="/path/to/output",
    output_markdown_path="/path/to/output/doc.md"
)
```

### Other Fixes

- **rowspan/colspan expansion**: Merged table cells are properly expanded
- **Table structure fix**: Empty rows and duplicate separators are removed
- **XLSX enhancements**: Handles merged cells, detects headers, cleans NaN values

For full documentation, see [README_ENHANCED.md](./README_ENHANCED.md).

---

## Full Feature List

markitdown-z currently supports the conversion from:

- PDF
- PowerPoint
- Word
- Excel
- Images (EXIF metadata and OCR)
- Audio (EXIF metadata and speech transcription)
- HTML
- Text-based formats (CSV, JSON, XML)
- ZIP files (iterates over contents)
- Youtube URLs
- EPubs
- ... and more!

## Why Markdown?

Markdown is extremely close to plain text, with minimal markup or formatting, but still provides a way to represent important document structure. Mainstream LLMs, such as OpenAI's GPT-4o, natively "speak" Markdown, and often incorporate Markdown into their responses unprompted. This suggests that they have been trained on vast amounts of Markdown-formatted text, and understand it well. As a side benefit, Markdown conventions are also highly token-efficient.

## Prerequisites

markitdown-z requires Python 3.10 or higher. It is recommended to use a virtual environment to avoid dependency conflicts.

With the standard Python installation, you can create and activate a virtual environment using the following commands:

```bash
python -m venv .venv
source .venv/bin/activate
```

If using `uv`, you can create a virtual environment with:

```bash
uv venv --python=3.12 .venv
source .venv/bin/activate
# NOTE: Be sure to use 'uv pip install' rather than just 'pip install' to install packages in this virtual environment
```

If you are using Anaconda, you can create a virtual environment with:

```bash
conda create -n markitdown-z python=3.12
conda activate markitdown-z
```

## Usage

### Command-Line

```bash
markitdown-z path-to-file.pdf > document.md
```

Or use `-o` to specify the output file:

```bash
markitdown-z path-to-file.pdf -o document.md
```

You can also pipe content:

```bash
cat path-to-file.pdf | markitdown-z
```

### Optional Dependencies

markitdown-z has optional dependencies for activating various file formats. You can install them individually for more control. For example:

```bash
pip install 'markitdown-z[pdf, docx, pptx]'
```

will install only the dependencies for PDF, DOCX, and PPTX files.

At the moment, the following optional dependencies are available:

* `[pdf]` Installs dependencies for PDF files
* `[docx]` Installs dependencies for Word files
* `[xlsx]` Installs dependencies for Excel files
* `[xls]` Installs dependencies for older Excel files
* `[pptx]` Installs dependencies for PowerPoint files
* `[outlook]` Installs dependencies for Outlook messages
* `[az-doc-intel]` Installs dependencies for Azure Document Intelligence
* `[audio-transcription]` Installs dependencies for audio transcription of wav and mp3 files
* `[youtube-transcription]` Installs dependencies for fetching YouTube video transcription

### Plugins

markitdown-z also supports 3rd-party plugins. Plugins are disabled by default. To list installed plugins:

```bash
markitdown-z --list-plugins
```

To enable plugins use:

```bash
markitdown-z --use-plugins path-to-file.pdf
```

To find available plugins, search GitHub for the hashtag `#markitdown-plugin`. To develop a plugin, see `packages/markitdown-sample-plugin`.

#### markitdown-ocr Plugin

The `markitdown-ocr` plugin adds OCR support to PDF, DOCX, PPTX, and XLSX converters, extracting text from embedded images using LLM Vision. No new ML libraries or binary dependencies required.

**Installation:**

```bash
pip install markitdown-ocr
pip install openai  # or any OpenAI-compatible client
```

**Usage:**

```python
from markitdown_z import MarkItDown
from openai import OpenAI

md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o",
)
result = md.convert("document_with_images.pdf")
print(result.text_content)
```

If no `llm_client` is provided the plugin still loads, but OCR is silently skipped and the standard built-in converter is used instead.

See [`packages/markitdown-ocr/README.md`](packages/markitdown-ocr/README.md) for detailed documentation.

### Azure Document Intelligence

To use Microsoft Document Intelligence for conversion:

```bash
markitdown-z path-to-file.pdf -o document.md -d -e "<document_intelligence_endpoint>"
```

### Python API

Basic usage in Python:

```python
from markitdown_z import MarkItDown

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
result = md.convert("test.xlsx")
print(result.text_content)
```

Document Intelligence conversion in Python:

```python
from markitdown_z import MarkItDown

md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert("test.pdf")
print(result.text_content)
```

To use Large Language Models for image descriptions (currently only for pptx and image files), provide `llm_client` and `llm_model`:

```python
from markitdown_z import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o", llm_prompt="optional custom prompt")
result = md.convert("example.jpg")
print(result.text_content)
```

### Docker

```sh
docker build -t markitdown-z:latest .
docker run --rm -i markitdown-z:latest < ~/your-file.pdf > output.md
```

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### How to Contribute

You can help by looking at issues or helping review PRs. Any issue or PR is welcome, but we have also marked some as 'open for contribution' and 'open for reviewing' to help facilitate community contributions.

<div align="center">

|            | All                                                          | Especially Needs Help from Community                                                                                                      |
| ---------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Issues** | [All Issues](https://github.com/zz1151258647/markitdown/issues) | [Issues open for contribution](https://github.com/zz1151258647/markitdown/issues?q=is%3Aissue+is%3Aopen+label%3A%22open+for+contribution%22) |
| **PRs**    | [All PRs](https://github.com/zz1151258647/markitdown/pulls)     | [PRs open for reviewing](https://github.com/zz1151258647/markitdown/pulls?q=is%3Apr+is%3Aopen+label%3A%22open+for+reviewing%22)              |

</div>

### Running Tests and Checks

- Navigate to the markitdown-z package:

  ```sh
  cd packages/markitdown
  ```

- Install `hatch` in your environment and run tests:

  ```sh
  pip install hatch  # Other ways of installing hatch: https://hatch.pypa.io/dev/install/
  hatch shell
  hatch test
  ```

  (Alternative) Use the Devcontainer which has all the dependencies installed:

  ```sh
  # Reopen the project in Devcontainer and run:
  hatch test
  ```

- Run pre-commit checks before submitting a PR: `pre-commit run --all-files`

### Contributing 3rd-party Plugins

You can also contribute by creating and sharing 3rd party plugins. See `packages/markitdown-sample-plugin` for more details.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.
