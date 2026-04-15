---
name: markitdown
version: 1.0.0
description: "将 PDF/Word/Excel/PPT/图片/音频/HTML 等文档转换为 Markdown。当用户需要转换文档格式、提取文档内容、给 AI 分析文档、或者将文档转为文本时使用。"
metadata:
  requires:
    bins: ["python", "markitdown"]
---

# MarkItDown 文档转换

将各种格式文档转换为 Markdown，供 AI 分析或文本处理。

## 命令

**重要：默认行为会截断图片。当需要提取图片时，必须加 `-i` 选项。**

```bash
# 标准转换（不保留图片内容）
markitdown <文件路径> -o <输出.md>

# 推荐：提取文档图片到文件夹，Markdown 中引用本地路径
markitdown document.pdf -i --images-output-dir ./images -o document.md

# 示例：Word 文档转 MD 并提取图片
markitdown report.docx -i --images-output-dir ./report_images -o report.md

# 指定图片前缀（方便管理）
markitdown document.pdf -i --images-output-dir ./images --images-prefix myimg -o document.md

# 从 stdin 读取（指定文件类型）
cat document.pdf | markitdown -x pdf > document.md

# 保留 base64 图片（默认截断）
markitdown document.pdf --keep-data-uris

# 使用 Document Intelligence（需 Azure 配置）
markitdown document.pdf -d -e <endpoint>

# 使用第三方插件
markitdown document.pdf -p

# 查看已装插件
markitdown --list-plugins
```

**完整工作流：**
1. 转换时加 `-i --images-output-dir <文件夹>` 提取图片
2. 图片保存到指定文件夹，MD 文件中用相对路径引用（如 `images/img_0.png`）
3. 图片文件夹与 MD 文件在同一目录下

## 支持格式

| 格式 | 后缀 | 说明 |
|------|------|------|
| PDF | `.pdf` |  |
| Word | `.docx` |  |
| Excel | `.xlsx` / `.xls` |  |
| PowerPoint | `.pptx` |  |
| 图片 | `.jpg` / `.png` 等 | EXIF + OCR |
| 音频 | `.mp3` / `.wav` 等 | 语音转录（需 ffmpeg） |
| HTML | `.html` / `.htm` |  |
| CSV | `.csv` |  |
| JSON | `.json` |  |
| XML | `.xml` |  |
| ZIP | `.zip` | 遍历内容 |
| EPUB | `.epub` |  |
| Outlook MSG | `.msg` |  |
| 微信公众号 | URL |  |
| YouTube | URL | 字幕转文本 |

## 场景选择

- **文档转 Markdown（推荐含图片提取）**：
  ```bash
  # 图片一并提取，MD 中引用本地路径
  markitdown file.ext -i --images-output-dir ./images -o output.md
  ```
- **只转文字不要图片**：直接 `markitdown file.ext -o output.md`（图片 base64 会被截断）
- **OCR 识别图片文字**：用图片格式直接转换（内置 OCR）
- **语音转文字**：用音频文件（需安装 ffmpeg）
- **批量转换**：

  ```bash
  for f in *.docx; do
    mkdir -p "${f%.docx}_images"
    markitdown "$f" -i --images-output-dir "./${f%.docx}_images" -o "${f%.docx}.md"
  done
  ```

## 依赖说明

| 功能 | 依赖 | 安装命令 |
|------|------|---------|
| 核心转换 | 内置 | `pip install markitdown` |
| Word/Excel/PPT | optional | `pip install 'markitdown[all]'` |
| PDF | optional | `pip install 'markitdown[pdf]'` |
| 语音转录 | optional | `pip install 'markitdown[audio-transcription]'` + ffmpeg |
| Azure 文档智能 | optional | `pip install 'markitdown[az-doc-intel]'` |

常用全量安装：`pip install 'markitdown[all]'`
