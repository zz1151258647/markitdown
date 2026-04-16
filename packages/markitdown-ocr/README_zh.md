# MarkItDown OCR 插件

[English](./README.md) | 中文版

用于 MarkItDown 的 LLM Vision 插件，可从 PDF、DOCX、PPTX 和 XLSX 文件中嵌入的图像提取文本。

使用与 MarkItDown 已支持图像描述的相同 `llm_client` / `llm_model` 模式——无需新的 ML 库或二进制依赖项。

## 功能特性

- **增强型 PDF 转换器**：从 PDF 中的图像提取文本，对扫描文档提供全页 OCR 回退
- **增强型 DOCX 转换器**：对 Word 文档中的图像进行 OCR
- **增强型 PPTX 转换器**：对 PowerPoint 演示文稿中的图像进行 OCR
- **增强型 XLSX 转换器**：对 Excel 电子表格中的图像进行 OCR
- **上下文保留**：插入提取文本时保持文档结构和流程

## 安装

```bash
pip install markitdown-ocr
```

该插件使用您已有的任何 OpenAI 兼容客户端。如果您还没有，请安装一个：

```bash
pip install openai
```

## 使用方法

### 命令行

```bash
markitdown document.pdf --use-plugins --llm-client openai --llm-model gpt-4o
```

### Python API

与图像描述一样，将 `llm_client` 和 `llm_model` 传递给 `MarkItDown()`：

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

如果未提供 `llm_client`，插件仍会加载，但 OCR 会被静默跳过——回退到标准内置转换器。

### 自定义提示

为专业文档覆盖默认提取提示：

```python
md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o",
    llm_prompt="从此图像中提取所有文本，保留表格结构。",
)
```

### 任何 OpenAI 兼容的客户端

可与任何遵循 OpenAI API 的客户端配合使用：

```python
from openai import AzureOpenAI

md = MarkItDown(
    enable_plugins=True,
    llm_client=AzureOpenAI(
        api_key="...",
        azure_endpoint="https://your-resource.openai.azure.com/",
        api_version="2024-02-01",
    ),
    llm_model="gpt-4o",
)
```

## 工作原理

当调用 `MarkItDown(enable_plugins=True, llm_client=..., llm_model=...)` 时：

1. MarkItDown 通过 `markitdown.plugin` 入口点组发现插件
2. 它调用 `register_converters()`，转发所有 kwargs，包括 `llm_client` 和 `llm_model`
3. 插件从这些 kwargs 创建一个 `LLMVisionOCRService`
4. 四个 OCR 增强型转换器以 **优先级 -1.0** 注册——在优先级 0.0 的内置转换器之前

当文件被转换时：

1. OCR 转换器接受文件
2. 从文档中提取嵌入式图像
3. 每张图像随提取提示一起发送到 LLM
4. 返回的文本被内联插入，保留文档结构
5. 如果 LLM 调用失败，转换将在没有该图像文本的情况下继续

## 支持的文件格式

### PDF

- 嵌入式图像通过位置提取（通过 `page.images` / page XObjects）并内联 OCR，与垂直阅读顺序周围的文本交错。
- **扫描 PDF**（没有可提取文本的页面）会被自动检测：每页以 300 DPI 渲染，作为全页图像发送到 LLM。
- **格式错误的 PDF**（pdfplumber/pdfminer 无法打开的，例如截断的 EOF）会使用 PyMuPDF 页面渲染重试，因此仍可恢复内容。

### DOCX

- 图像通过文档部件关系（`doc.part.rels`）提取。
- OCR 在 DOCX→HTML→Markdown 管道执行之前运行：占位符标记被注入 HTML，以便 markdown 转换器不会转义 OCR 标记，并且在转换后替换最终占位符为格式化的 `*[Image OCR]...[End OCR]*` 块。
- 文档流程（标题、段落、表格）在 OCR 块周围完全保留。

### PPTX

- 支持图片形状、具有图像的占位符形状以及组内的图像。
- 形状按每张幻灯片的从上到下阅读顺序处理。
- 如果配置了 `llm_client`，则首先向 LLM 请求描述；当没有返回描述时，OCR 作为回退使用。

### XLSX

- 提取工作表（`sheet._images`）中嵌入的图像。
- 单元格位置根据图像锚点坐标计算（列/行 → Excel 字母表示法）。
- 图像列在数据表之后的 `### Images in this sheet:` 部分列出——它们不会交错到表行中。

### 输出格式

每个提取的 OCR 块都包装为：

```text
*[Image OCR]
<extracted text>
[End OCR]*
```

## 故障排除

### 输出中缺少 OCR 文本

最可能的原因是缺少 `llm_client` 或 `llm_model`。请验证：

```python
from openai import OpenAI
from markitdown import MarkItDown

md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),   # 必需
    llm_model="gpt-4o",    # 必需
)
```

### 插件未加载

确认插件已安装并被发现：

```bash
markitdown --list-plugins   # 应显示：ocr
```

### API 错误

插件将 LLM API 错误作为警告传播，并继续转换。请检查您的 API 密钥、配额以及所选模型是否支持视觉输入。

## 开发

### 运行测试

```bash
cd packages/markitdown-ocr
pytest tests/ -v
```

### 从源代码构建

```bash
git clone https://github.com/zz1151258647/markitdown.git
cd markitdown/packages/markitdown-ocr
pip install -e .
```

## 贡献

欢迎贡献！请参阅 [MarkItDown 仓库](https://github.com/zz1151258647/markitdown) 了解指南。

## 许可证

MIT——请参阅 [LICENSE](LICENSE)。

## 变更日志

### 0.1.0（初始版本）

- PDF、DOCX、PPTX、XLSX 的 LLM Vision OCR
- 扫描 PDF 的全页 OCR 回退
- 上下文感知的内联文本插入
- 基于优先级的转换器替换（无需代码更改）
