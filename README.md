# MarkItDown Enhanced

[English](./README_en.md) | 中文版

[![PyPI](https://img.shields.io/pypi/v/markitdown.svg)](https://pypi.org/project/markitdown/)
![PyPI - Downloads](https://img.shields.io/pypi/dd/markitdown)
[![Official Repo](https://img.shields.io/badge/官方仓库-microsoft/markitdown-blue)](https://github.com/microsoft/markitdown)

> [!NOTE]
> 这是 [微软 MarkItDown](https://github.com/microsoft/markitdown) 的增强分支，专注于表格转换、图片提取和 MCP 支持。

## 与官方版本的区别

| 功能 | 官方版 | 增强版 |
|------|--------|--------|
| 表格转换 | 基础支持 | 完整支持 rowspan/colspan 展开、合并单元格处理 |
| 图片提取 | 不支持 | CLI 和 MCP 全面支持 |
| XLSX 增强 | 无 | 处理合并单元格、检测表头、清理 NaN 值 |
| MCP 服务器 | 有 | 有（功能更丰富）|

## 安装

从 PyPI 安装（官方版，不含增强功能）：
```bash
pip install 'markitdown[all]'
```

从本仓库安装（增强版）：
```bash
git clone https://github.com/zz1151258647/markitdown.git
cd markitdown
pip install -e 'packages/markitdown[all]'
```

## 快速开始

### 命令行

```bash
markitdown path-to-file.pdf -o document.md
```

### Python API

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.docx")
print(result.text_content)
```

## 增强功能详解

### 图片提取（CLI & MCP）

```bash
# CLI 带图片提取
py -m markitdown 文档.docx -o 输出.md -i --images-output-dir ./output
```

```python
# Python API 带图片提取
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert(
    "文档.docx",
    extract_images=True,
    images_output_dir="output",
    images_prefix="img"
)
```

### MCP 服务器

MCP 服务器支持图片提取和文件保存：

```python
convert_to_markdown(
    uri="file:///path/to/doc.docx",
    extract_images=True,
    images_output_dir="/path/to/output",
    output_markdown_path="/path/to/output/doc.md"
)
```

> [!TIP]
> MarkItDown 现已提供 MCP（Model Context Protocol）服务器，可与 Claude Desktop 等 LLM 应用集成。详见 [markitdown-mcp](https://github.com/zz1151258647/markitdown/tree/main/packages/markitdown-mcp)。

### 其他修复

- **rowspan/colspan 展开**：表格合并单元格正确展开
- **表格结构修复**：移除空行和重复分隔线
- **XLSX 增强**：处理合并单元格、检测表头、清理 NaN 值

完整文档请参阅 [README_ENHANCED.md](./README_ENHANCED.md)。

---

## 完整功能列表

MarkItDown 目前支持以下格式的转换：

- PDF
- PowerPoint
- Word
- Excel
- 图片（EXIF 元数据和 OCR）
- 音频（EXIF 元数据和语音转录）
- HTML
- 基于文本的格式（CSV、JSON、XML）
- ZIP 文件（遍历内容）
- Youtube 链接
- EPubs
- ……还有更多！

## 为什么选择 Markdown？

Markdown 与纯文本非常接近，标记或格式最少，但仍然提供了一种表示重要文档结构的方法。主流 LLM（如 OpenAI 的 GPT-4o）本身就能"理解"Markdown，并且经常在未提示的情况下将 Markdown 融入其响应中。这表明它们已在大量 Markdown 格式的文本上进行了训练，并且能够很好地理解 Markdown。作为附带好处，Markdown 约定也具有很高的 token 效率。

## 前提条件
MarkItDown 需要 Python 3.10 或更高版本。建议使用虚拟环境以避免依赖冲突。

使用标准 Python 安装，可以使用以下命令创建和激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
```

如果使用 `uv`，可以使用以下命令创建虚拟环境：

```bash
uv venv --python=3.12 .venv
source .venv/bin/activate
# 注意：在此虚拟环境中安装包时请务必使用 'uv pip install' 而非仅使用 'pip install'
```

如果您使用 Anaconda，可以使用以下命令创建虚拟环境：

```bash
conda create -n markitdown python=3.12
conda activate markitdown
```

## 安装

要安装 MarkItDown，请使用 pip：`pip install 'markitdown[all]'`。或者，您也可以从源代码安装：

```bash
git clone git@github.com:zz1151258647/markitdown.git
cd markitdown
pip install -e 'packages/markitdown[all]'
```

## 使用方法

### 命令行

```bash
markitdown path-to-file.pdf > document.md
```

或使用 `-o` 指定输出文件：

```bash
markitdown path-to-file.pdf -o document.md
```

您也可以通过管道传输内容：

```bash
cat path-to-file.pdf | markitdown
```

### 可选依赖项
MarkItDown 具有可选依赖项，用于激活各种文件格式。在本文档的前面部分，我们使用 `[all]` 选项安装了所有可选依赖项。但是，您也可以单独安装它们以获得更多控制。例如：

```bash
pip install 'markitdown[pdf, docx, pptx]'
```

将仅安装 PDF、DOCX 和 PPTX 文件的依赖项。

目前有以下可选依赖项可用：

* `[all]` 安装所有可选依赖项
* `[pptx]` 安装 PowerPoint 文件的依赖项
* `[docx]` 安装 Word 文件的依赖项
* `[xlsx]` 安装 Excel 文件的依赖项
* `[xls]` 安装旧版 Excel 文件的依赖项
* `[pdf]` 安装 PDF 文件的依赖项
* `[outlook]` 安装 Outlook 邮件的依赖项
* `[az-doc-intel]` 安装 Azure 文档智能的依赖项
* `[audio-transcription]` 安装音频转录 wav 和 mp3 文件的依赖项
* `[youtube-transcription]` 安装获取 YouTube 视频转录的依赖项

### 插件

MarkItDown 还支持第三方插件。插件默认禁用。要列出已安装的插件：

```bash
markitdown --list-plugins
```

要启用插件，请使用：

```bash
markitdown --use-plugins path-to-file.pdf
```

要查找可用插件，请在 GitHub 上搜索标签 `#markitdown-plugin`。要开发插件，请参见 `packages/markitdown-sample-plugin`。

#### markitdown-ocr 插件

`markitdown-ocr` 插件为 PDF、DOCX、PPTX 和 XLSX 转换器添加了 OCR 支持，使用 LLM Vision 从嵌入式图像中提取文本——采用与 MarkItDown 已用于图像描述的相同 `llm_client` / `llm_model` 模式。无需新的 ML 库或二进制依赖项。

**安装：**

```bash
pip install markitdown-ocr
pip install openai  # 或任何 OpenAI 兼容的客户端
```

**用法：**

传递与图像描述相同的 `llm_client` 和 `llm_model`：

```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o",
)
result = md.convert("document_with_images.pdf")
print(result.text_content)
```

如果未提供 `llm_client`，插件仍会加载，但 OCR 会被静默跳过，使用标准内置转换器。

有关详细文档，请参阅 [`packages/markitdown-ocr/README.md`](packages/markitdown-ocr/README.md)。

## 增强功能

这是微软 MarkItDown 原版的增强分支，增加了以下功能：

### 图片提取（CLI & MCP）

```bash
# CLI 带图片提取
py -m markitdown 文档.docx -o 输出.md -i --images-output-dir ./output
```

```python
# Python API 带图片提取
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert(
    "文档.docx",
    extract_images=True,
    images_output_dir="output",
    images_prefix="img"
)
```

### MCP 服务器

MCP 服务器支持图片提取和文件保存：

```python
convert_to_markdown(
    uri="file:///path/to/doc.docx",
    extract_images=True,
    images_output_dir="/path/to/output",
    output_markdown_path="/path/to/output/doc.md"
)
```

### 其他修复

- **rowspan/colspan 展开**：表格合并单元格正确展开
- **表格结构修复**：移除空行和重复分隔线
- **XLSX 增强**：处理合并单元格、检测表头、清理 NaN 值

完整文档请参阅 [README_ENHANCED.md](./README_ENHANCED.md)。

### Azure 文档智能

要使用 Microsoft 文档智能进行转换：

```bash
markitdown path-to-file.pdf -o document.md -d -e "<document_intelligence_endpoint>"
```

有关如何设置 Azure 文档智能资源的更多信息，请参见[此处](https://learn.microsoft.com/zh-cn/azure/ai-services/document-intelligence/how-to-guides/create-document-intelligence-resource?view=doc-intel-4.0.0)。

### Python API

Python 中的基本用法：

```python
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False) # 设置为 True 以启用插件
result = md.convert("test.xlsx")
print(result.text_content)
```

Python 中的文档智能转换：

```python
from markitdown import MarkItDown

md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert("test.pdf")
print(result.text_content)
```

要将大型语言模型用于图像描述（目前仅适用于 pptx 和图像文件），请提供 `llm_client` 和 `llm_model`：

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o", llm_prompt="可选的自定义提示")
result = md.convert("example.jpg")
print(result.text_content)
```

### Docker

```sh
docker build -t markitdown:latest .
docker run --rm -i markitdown:latest < ~/your-file.pdf > output.md
```

## 贡献

本项目欢迎贡献和建议。大多数贡献需要您同意贡献者许可协议（CLA），声明您有权并实际授予我们使用您的贡献的权利。有关详细信息，请访问 https://cla.opensource.microsoft.com。

当您提交拉取请求时，CLA 机器人将自动确定您是否需要提供 CLA，并相应地装饰 PR（例如，状态检查、评论）。只需按照机器人提供的说明操作即可。您只需要在所有使用 CLA 的 repos 中执行此操作一次。

本项目采用 [Microsoft 开源行为准则](https://opensource.microsoft.com/codeofconduct/)。
有关详细信息，请参阅[行为准则常见问题](https://opensource.microsoft.com/codeofconduct/faq/)或通过 [opencode@microsoft.com](mailto:opencode@microsoft.com) 联系，提出任何其他问题或评论。

### 如何贡献

您可以通过查看问题或帮助审查 PR 来提供帮助。任何问题或 PR 都欢迎，但我们也标记了一些为"开放贡献"和"开放审查"，以帮助促进社区贡献。当然，这些只是建议，欢迎您以任何您喜欢的方式做出贡献。

<div align="center">

|            | 所有                                                            | 特别需要社区帮助                                                                                                                              |
| ---------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **问题**   | [所有问题](https://github.com/zz1151258647/markitdown/issues)   | [开放贡献的问题](https://github.com/zz1151258647/markitdown/issues?q=is%3Aissue+is%3Aopen+label%3A%22open+for+contribution%22)             |
| **PRs**    | [所有 PR](https://github.com/zz1151258647/markitdown/pulls)     | [开放审查的 PR](https://github.com/zz1151258647/markitdown/pulls?q=is%3Apr+is%3Aopen+label%3A%22open+for+reviewing%22)                     |

</div>

### 运行测试和检查

- 导航到 MarkItDown 包：

  ```sh
  cd packages/markitdown
  ```

- 在您的环境中安装 `hatch` 并运行测试：

  ```sh
  pip install hatch  # 其他安装 hatch 的方式：https://hatch.pypa.io/dev/install/
  hatch shell
  hatch test
  ```

  （替代方案）使用已安装所有依赖项的 Devcontainer：

  ```sh
  # 在 Devcontainer 中重新打开项目并运行：
  hatch test
  ```

- 提交 PR 前运行预提交检查：`pre-commit run --all-files`

### 贡献第三方插件

您还可以通过创建和共享第三方插件来做出贡献。详见 `packages/markitdown-sample-plugin`。

## 商标

本项目可能包含项目、产品或服务的商标或标识。经授权使用 Microsoft 商标或标识必须遵守并遵循
[Microsoft 的商标和品牌指南](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general)。
在修改后的版本中使用 Microsoft 商标或标识不得造成混淆或暗示 Microsoft 赞助。
任何第三方商标或标识的使用均须遵守这些第三方的政策。
