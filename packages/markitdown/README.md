# MarkItDown Enhanced

基于微软 [markitdown](https://github.com/microsoft/markitdown) 的 DOCX 转 Markdown 增强版本。

## 主要改动

### 1. 修复 rowspan/colspan 展开问题

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

### 2. 图片提取功能

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

### 3. 移除"图 N"编号

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

### 4. 修复表格结构

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

## 使用方法

```python
from markitdown import MarkItDown
import os
import shutil

docx_path = "产品需求文档.docx"
output_dir = "output"

# 清理并创建输出目录
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# 生成 Markdown 文件名（继承原文档名）
md_filename = os.path.splitext(os.path.basename(docx_path))[0] + '.md'

# 转换
markitdown = MarkItDown()
result = markitdown.convert(
    docx_path,
    extract_images=True,           # 启用图片提取
    images_output_dir=output_dir,   # 输出目录
    images_prefix="img"             # 图片前缀
)

# 保存 Markdown
with open(os.path.join(output_dir, md_filename), 'w', encoding='utf-8') as f:
    f.write(result.markdown)
```

---

## 工作流程

```
DOCX → mammoth → _fix_html_tables → _extract_images_from_base64 → convert_soup(展开rowspan) → Markdown
```

---

---

### 5. XLSX 转换器增强

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
| 版本名称 | 主要功能模块 | 优势 | 劣势 | 适合场景与行业； |
| --- | --- | --- | --- | --- |
| 语音调度版（精简） | 1、配套NC；<br>2、包含点对点语音通话； | 1、部署简单；<br>2、界面功能简洁； | ... |
```

---

## 修改的文件

| 文件 | 说明 |
|------|------|
| `converters/_docx_converter.py` | HTML 预处理、图片提取 |
| `converters/_markdownify.py` | rowspan 展开、表格/图片/链接转换 |
| `converters/_xlsx_converter.py` | XLSX 转换：合并单元格、Header 检测、换行符处理 |

---

## 原版地址

https://github.com/microsoft/markitdown

## 许可

继承原项目 MIT 许可
