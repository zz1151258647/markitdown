# MarkItDown

[English](./README.md) | 中文版

> [!IMPORTANT]
> MarkItDown 是一个 Python 包和命令行工具，用于将各种文件转换为 Markdown（例如，用于索引、文本分析等）。
>
> 更多信息和完整文档，请参阅 GitHub 上的项目 [README.md](https://github.com/zz1151258647/markitdown)。

## 安装

## 安装

### 从 PyPI（推荐）

```bash
pip install markitdown-z
```

### 从 GitHub Release

```bash
pip install https://github.com/zz1151258647/markitdown/releases/download/v0.1.5.post3/markitdown_z-0.1.5.post3-py3-none-any.whl
```

### 从源代码

```bash
git clone git@github.com:zz1151258647/markitdown.git
cd markitdown
pip install -e packages/markitdown
```

## 使用方法

### 命令行

```bash
markitdown-z path-to-file.pdf > document.md
```

### Python API

```python
from markitdown_z import MarkItDown

md = MarkItDown()
result = md.convert("test.xlsx")
print(result.text_content)
```

### 更多信息

更多信息和完整文档，请参阅 GitHub 上的项目 [README.md](https://github.com/zz1151258647/markitdown)。

## 商标

本项目可能包含项目、产品或服务的商标或标识。经授权使用 Microsoft 商标或标识必须遵守并遵循
[Microsoft 的商标和品牌指南](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general)。
在修改后的版本中使用 Microsoft 商标或标识不得造成混淆或暗示 Microsoft 赞助。
任何第三方商标或标识的使用均须遵守这些第三方的政策。
