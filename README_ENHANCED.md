# MarkItDown Enhanced

基于微软 [markitdown](https://github.com/microsoft/markitdown) 的增强版本，增加了图片提取、XLSX 转换增强等功能。

---

## 主要改动

### 1. CLI 新增图片提取参数

**修改文件：** `packages/markitdown/src/markitdown/__main__.py`

**新增参数：**
```bash
-i, --extract-images      # 开启图片提取
--images-output-dir <目录> # 图片输出目录
--images-prefix <前缀>     # 图片名前缀（默认 img）
```

**使用示例：**
```bash
py -m markitdown 文档.docx -o 输出.md -i --images-output-dir ./output
```

---

### 2. MCP 服务新增图片提取和保存文件功能

**修改文件：** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

**新增参数：**
```python
convert_to_markdown(
    uri="file:///path/to/doc.docx",
    extract_images=True,           # 启用图片提取
    images_output_dir="/path",    # 图片输出目录
    images_prefix="img",          # 图片前缀
    output_markdown_path="/path/doc.md"  # 保存 markdown 文件
)
```

**MCP 配置：** 项目根目录 `.mcp.json` 已配置 markitdown-mcp 服务

---

### 3. 图片提取功能

将 Word 文档中的 base64 图片解码提取到独立文件夹，使用相对路径引用。

**转换前：** 图片以 base64 形式内嵌在 HTML 中

**转换后：**
```
output/
├── 产品文档.md
└── images/
    ├── img1.png
    ├── img2.png
    └── ...
```

Markdown 中的图片引用：
```markdown
![截图](images/img1.png)
```

---

### 4. 移除"图 N"编号

原版会在图片前添加"图 1"、"图 2"等编号文本，现已移除。

**原版输出：**
```markdown
图 1 ![截图](img1.png)
```

**修复后：**
```markdown
![截图](images/img1.png)
```

---

### 5. 修复 rowspan/colspan 展开问题

**问题：** Word 表格中的合并单元格（rowspan）在转换为 Markdown 时只显示首行内容，后续行对应列为空。

**示例（原始 Word 表格）：**
| 产品 | 功能模块 | 负责人 |
| --- | --- | --- |
| 产品A | 用户管理 | 张三 |
| 产品A | 订单管理 | ← 空白 |
| 产品A | 财务报表 | ← 空白 |

**修复后：**
| 产品 | 功能模块 | 负责人 |
| --- | --- | --- |
| 产品A | 用户管理 | 张三 |
| 产品A | 订单管理 | 张三 |
| 产品A | 财务报表 | 张三 |

---

### 6. 修复表格结构

原版 markdownify 对全 `<td>` 表格会错误生成空行和重复分隔线，新版本直接生成标准 Markdown 表格。

**原版错误输出：**
```markdown
|  |  |  |
| --- | --- | --- |
| 编号 | 名称 | 说明 |
| --- | --- | --- |  ← 重复的分隔线
| 1 | 测试 | 内容 |
```

**修复后：**
```markdown
| 编号 | 名称 | 说明 |
| --- | --- | --- |
| 1 | 测试 | 内容 |
```

---

### 7. XLSX 转换器增强

**功能：**
- 正确处理合并单元格，自动填充值
- 智能检测 Header 行（跳过全相同值标题行）
- 过滤 sub-header 行（第一列为空且其他列值相同的行）
- 处理单元格内换行符，转换为 `<br>` 标签
- 自动清理 NaN 值和 Unnamed 列

**问题修复：**
- ❌ 合并单元格只显示第一个值
- ❌ Header 行检测错误
- ❌ 出现 "Unnamed: 1"、"Unnamed: 2" 等列名
- ❌ NaN 值未清理
- ❌ 空行未移除
- ❌ 单元格内换行符导致表格行被拆散

**修复后：**
```markdown
## 清单总览
| 产品 | 功能模块 | 负责人 | 状态 |
| --- | --- | --- | --- |
| 产品A | 用户管理<br>订单管理<br>财务管理 | 张三 | 开发中 |
| 产品B | 数据分析 | 李四 | 已上线 |
```

---

## 支持格式

| 格式 | 支持情况 |
|------|---------|
| DOCX | ✅ 完全支持（含图片提取） |
| XLSX | ✅ 完全支持（含合并单元格处理） |
| PDF | ✅ 有文字层的 PDF |
| PPTX | ✅ 支持 |
| DOC | ❌ 不支持（老格式，需转换为 DOCX） |

---

## 使用方法

### CLI

```bash
# 基本转换
py -m markitdown 文档.docx -o 输出.md

# 带图片提取
py -m markitdown 文档.docx -o 输出.md -i --images-output-dir ./output
```

### Python API

```python
from markitdown import MarkItDown

markitdown = MarkItDown()
result = markitdown.convert(
    "文档.docx",
    extract_images=True,
    images_output_dir="output",
    images_prefix="img"
)

with open("output/文档.md", "w", encoding="utf-8") as f:
    f.write(result.markdown)
```

### MCP

在 Claude Code 或其他 MCP 客户端中配置：
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "C:\\Users\\xxx\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
      "args": ["-m", "markitdown_mcp"]
    }
  }
}
```

---

## 工作流程

```
DOCX → mammoth → _fix_html_tables → _extract_images_from_base64 → convert_soup(展开rowspan) → Markdown
```

---

## 修改的文件

| 文件 | 说明 |
|------|------|
| `packages/markitdown/src/markitdown/__main__.py` | CLI 参数：新增图片提取相关参数 |
| `packages/markitdown/src/markitdown/converters/_docx_converter.py` | HTML 预处理、图片提取 |
| `packages/markitdown/src/markitdown/converters/_markdownify.py` | rowspan 展开、表格/图片/链接转换 |
| `packages/markitdown/src/markitdown/converters/_xlsx_converter.py` | XLSX 转换：合并单元格、Header 检测、换行符处理 |
| `packages/markitdown-mcp/src/markitdown_mcp/__main__.py` | MCP 工具：新增图片提取和保存文件参数 |
| `.mcp.json` | MCP 服务配置 |

---

## 原版地址

https://github.com/microsoft/markitdown

---

## 许可

继承原项目 MIT 许可
