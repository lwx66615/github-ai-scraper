# 动态关键词库与可视化输出设计文档

## 概述

为 GitHub AI Scraper 添加两个新功能：
1. **动态关键词库** - 自动从爬取内容中提取关键词，持续丰富搜索词库
2. **Markdown 输出** - 生成易读的 Markdown 表格文件

## 需求详情

### 需求 1：动态关键词库

**目标：** 每次爬取后自动提取关键词，补充到关键词库，使后续搜索更精准。

**用户选择：**
- 存储位置：单独的 `keywords.txt` 文件
- 触发时机：每次爬取后自动提取
- 关键词上限：默认 100 个，可配置
- 提取来源：topics + description + name（全部来源）

### 需求 2：Markdown 表格输出

**目标：** 爬取后生成 Markdown 格式的表格文件，方便查看和分享。

**用户选择：**
- 文件格式：Markdown 表格
- 输出模式：单文件（所有仓库）
- 输出目录：`./output/repositories.md`

## 技术设计

### 文件结构

```
github-ai-scraper/
├── keywords.txt              # 关键词库（每行一个关键词）
├── output/                   # 输出目录
│   └── repositories.md       # Markdown 表格
├── src/ai_scraper/
│   ├── keywords/             # 新增：关键词模块
│   │   ├── __init__.py
│   │   └── extractor.py      # 关键词提取器
│   └── ...
└── ai-scraper.yaml           # 更新：添加 max_keywords 配置
```

### 模块设计

#### 1. KeywordExtractor 类

**文件：** `src/ai_scraper/keywords/extractor.py`

**职责：**
- 从仓库数据中提取关键词
- 过滤停用词和无效词
- 管理关键词文件读写

**接口设计：**

```python
class KeywordExtractor:
    def __init__(self, keywords_file: Path, max_keywords: int = 100):
        """初始化提取器。

        Args:
            keywords_file: 关键词文件路径
            max_keywords: 关键词数量上限
        """

    def load_keywords(self) -> set[str]:
        """加载现有关键词。"""

    def save_keywords(self, keywords: set[str]) -> None:
        """保存关键词到文件。"""

    def extract_from_repos(self, repos: list[Repository]) -> set[str]:
        """从仓库列表提取关键词。

        提取来源：
        - topics: 直接收集
        - description: 分词 + 词频统计
        - name: 按 - _ 分割提取
        """

    def merge_keywords(self, new_keywords: set[str]) -> set[str]:
        """合并新关键词，限制数量。"""

    def get_keywords_for_search(self) -> list[str]:
        """获取用于搜索的关键词列表。"""
```

**提取规则：**

| 来源 | 提取方式 | 示例 |
|------|----------|------|
| topics | 直接收集 | `["ai", "machine-learning"]` → `ai`, `machine-learning` |
| description | 分词 + 过滤 | `"Industrial-strength NLP in Python"` → `industrial-strength`, `nlp`, `python` |
| name | 按 `-` `_` 分割 | `"awesome-ai-toolkit"` → `awesome`, `ai`, `toolkit` |

**过滤规则：**
- 停用词过滤（the, is, a, for, to, and 等）
- 长度过滤（最少 2 个字符）
- 数字过滤（纯数字不保留）
- 大小写统一（转小写）

#### 2. Markdown 输出模块

**文件：** `src/ai_scraper/output/markdown.py`

**职责：**
- 生成 Markdown 表格
- 管理输出目录

**接口设计：**

```python
class MarkdownExporter:
    def __init__(self, output_dir: Path):
        """初始化导出器。

        Args:
            output_dir: 输出目录路径
        """

    def export_repositories(self, repos: list[Repository]) -> Path:
        """导出仓库列表为 Markdown 表格。

        Returns:
            生成的文件路径
        """

    def _format_table(self, repos: list[Repository]) -> str:
        """格式化为 Markdown 表格。"""
```

**输出格式：**

```markdown
# AI Repositories

**更新时间:** 2026-05-09 19:00:00
**总计:** 7 个仓库

| Name | Stars | Language | Description | URL |
|------|-------|----------|-------------|-----|
| explosion/spaCy | 33,557 | Python | Industrial-strength NLP | [GitHub](https://github.com/explosion/spaCy) |
| olivia-ai/olivia | 3,719 | Go | AI assistant | [GitHub](https://github.com/olivia-ai/olivia) |
```

### 配置更新

**文件：** `ai-scraper.yaml`

```yaml
# 新增配置项
keywords:
  file: ./keywords.txt
  max_keywords: 100

output:
  dir: ./output
  filename: repositories.md
```

### CLI 集成

**修改文件：** `src/ai_scraper/cli.py`

**scrape 命令流程：**

```
1. 执行爬取
2. 保存到数据库
3. 提取关键词 → 更新 keywords.txt
4. 生成 Markdown → 保存到 output/repositories.md
5. 输出统计信息
```

**新增命令：**

```bash
# 查看当前关键词库
ai-scraper keywords list

# 手动触发关键词提取
ai-scraper keywords extract

# 清空关键词库
ai-scraper keywords clear
```

### 数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                         scrape 命令                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  GitHub API     │
                    │  爬取仓库数据    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  AIFilter       │
                    │  过滤 AI 相关    │
                    └─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │  Database   │ │  Keywords   │ │  Markdown   │
      │  SQLite     │ │  Extractor  │ │  Exporter   │
      └─────────────┘ └─────────────┘ └─────────────┘
              │               │               │
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │  .db 文件   │ │ keywords.txt│ │  .md 文件   │
      └─────────────┘ └─────────────┘ └─────────────┘
```

## 测试计划

### 单元测试

| 测试文件 | 测试内容 |
|----------|----------|
| `test_keywords.py` | KeywordExtractor 提取、过滤、合并逻辑 |
| `test_output.py` | MarkdownExporter 表格生成 |

### 集成测试

- 爬取后验证 keywords.txt 更新
- 爬取后验证 repositories.md 生成
- 关键词数量限制验证

## 实现任务

1. 创建 `keywords` 模块
2. 创建 `output` 模块
3. 更新配置文件
4. 集成到 `scrape` 命令
5. 添加 `keywords` 子命令
6. 编写测试
