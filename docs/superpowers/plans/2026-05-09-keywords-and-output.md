# 动态关键词库与 Markdown 输出实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 GitHub AI Scraper 添加动态关键词库和 Markdown 输出功能。

**Architecture:** 新增 `keywords` 模块负责关键词提取和管理，新增 `output` 模块负责 Markdown 表格生成，集成到现有 CLI 的 `scrape` 命令中。

**Tech Stack:** Python 3.10+, pathlib, re (正则表达式分词), 现有 ai_scraper 架构

---

## 文件结构

```
新增文件:
- src/ai_scraper/keywords/__init__.py
- src/ai_scraper/keywords/extractor.py
- src/ai_scraper/output/__init__.py
- src/ai_scraper/output/markdown.py
- tests/test_keywords.py
- tests/test_output.py
- keywords.txt (运行时生成)
- output/repositories.md (运行时生成)

修改文件:
- ai-scraper.yaml (添加配置项)
- src/ai_scraper/config.py (添加配置类)
- src/ai_scraper/cli.py (集成新功能)
```

---

## Task 1: 更新配置模块

**Files:**
- Modify: `src/ai_scraper/config.py`
- Modify: `ai-scraper.yaml`

- [ ] **Step 1: 添加 KeywordsConfig 和 OutputConfig 数据类**

在 `src/ai_scraper/config.py` 中添加：

```python
@dataclass
class KeywordsConfig:
    """Keywords configuration."""
    file: str = "./keywords.txt"
    max_keywords: int = 100


@dataclass
class OutputConfig:
    """Output configuration."""
    dir: str = "./output"
    filename: str = "repositories.md"
```

在 `Config` 类中添加新字段：

```python
@dataclass
class Config:
    """Main configuration."""
    github: GitHubConfig = field(default_factory=GitHubConfig)
    filter: FilterConfigYaml = field(default_factory=FilterConfigYaml)
    scrape: ScrapeConfigYaml = field(default_factory=ScrapeConfigYaml)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    keywords: KeywordsConfig = field(default_factory=KeywordsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

- [ ] **Step 2: 更新 load_config 函数**

在 `load_config` 函数中添加新配置的解析：

```python
def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None or not config_path.exists():
        return Config()

    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f) or {}

    processed_config = _process_config_values(raw_config)

    # ... existing code ...

    # Keywords config
    keywords_dict = processed_config.get("keywords", {})
    keywords_config = KeywordsConfig(
        file=keywords_dict.get("file", "./keywords.txt"),
        max_keywords=keywords_dict.get("max_keywords", 100),
    )

    # Output config
    output_dict = processed_config.get("output", {})
    output_config = OutputConfig(
        dir=output_dict.get("dir", "./output"),
        filename=output_dict.get("filename", "repositories.md"),
    )

    return Config(
        github=github,
        filter=filter_config,
        scrape=scrape_config,
        database=database_config,
        scheduler=scheduler_config,
        keywords=keywords_config,
        output=output_config,
    )
```

- [ ] **Step 3: 更新 ai-scraper.yaml**

添加新配置项：

```yaml
# Keywords configuration
keywords:
  file: ./keywords.txt
  max_keywords: 100

# Output configuration
output:
  dir: ./output
  filename: repositories.md
```

- [ ] **Step 4: 运行现有测试确认无破坏**

```bash
py -m pytest tests/test_config.py -v
```

Expected: PASS (3 tests)

- [ ] **Step 5: 提交配置更新**

```bash
git add src/ai_scraper/config.py ai-scraper.yaml
git commit -m "feat: add keywords and output configuration"
```

---

## Task 2: 创建关键词提取模块

**Files:**
- Create: `src/ai_scraper/keywords/__init__.py`
- Create: `src/ai_scraper/keywords/extractor.py`
- Create: `tests/test_keywords.py`

- [ ] **Step 1: 创建 keywords 包初始化文件**

创建 `src/ai_scraper/keywords/__init__.py`:

```python
"""Keywords extraction module."""

from ai_scraper.keywords.extractor import KeywordExtractor

__all__ = ["KeywordExtractor"]
```

- [ ] **Step 2: 编写关键词提取器测试**

创建 `tests/test_keywords.py`:

```python
"""Tests for keyword extraction."""

import tempfile
from pathlib import Path

import pytest

from ai_scraper.keywords.extractor import KeywordExtractor
from ai_scraper.models.repository import Repository
from datetime import datetime


def make_repo(name: str, description: str = "", topics: list = None) -> Repository:
    """Helper to create test repository."""
    return Repository(
        id=1,
        name=name,
        full_name=name,
        description=description,
        stars=100,
        language="Python",
        topics=topics or [],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url=f"https://github.com/{name}",
    )


def test_load_empty_keywords_file():
    """Test loading from non-existent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt")
        keywords = extractor.load_keywords()
        assert keywords == set()


def test_save_and_load_keywords():
    """Test saving and loading keywords."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "keywords.txt"
        extractor = KeywordExtractor(path)

        keywords = {"ai", "machine-learning", "nlp"}
        extractor.save_keywords(keywords)

        loaded = extractor.load_keywords()
        assert loaded == keywords


def test_extract_from_topics():
    """Test extracting keywords from topics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt")
        repo = make_repo("test/repo", "Test repo", topics=["ai", "machine-learning", "deep-learning"])

        keywords = extractor.extract_from_repos([repo])

        assert "ai" in keywords
        assert "machine-learning" in keywords
        assert "deep-learning" in keywords


def test_extract_from_description():
    """Test extracting keywords from description."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt")
        repo = make_repo("test/repo", "A machine learning library for natural language processing")

        keywords = extractor.extract_from_repos([repo])

        assert "machine" in keywords
        assert "learning" in keywords
        assert "natural" in keywords
        assert "language" in keywords
        assert "processing" in keywords


def test_extract_from_name():
    """Test extracting keywords from repository name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt")
        repo = make_repo("test/awesome-ai-toolkit")

        keywords = extractor.extract_from_repos([repo])

        assert "awesome" in keywords
        assert "ai" in keywords
        assert "toolkit" in keywords


def test_filter_stopwords():
    """Test that stopwords are filtered."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt")
        repo = make_repo("test/repo", "A library for the machine learning and natural language processing")

        keywords = extractor.extract_from_repos([repo])

        # Stopwords should be filtered
        assert "a" not in keywords
        assert "for" not in keywords
        assert "the" not in keywords
        assert "and" not in keywords


def test_merge_keywords_respects_limit():
    """Test that merge respects max_keywords limit."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extractor = KeywordExtractor(Path(tmpdir) / "keywords.txt", max_keywords=5)

        existing = {"a", "b", "c"}
        new = {"d", "e", "f", "g", "h"}

        merged = extractor.merge_keywords(existing, new)

        assert len(merged) <= 5


def test_get_keywords_for_search():
    """Test getting keywords as list for search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "keywords.txt"
        extractor = KeywordExtractor(path)

        keywords = {"ai", "machine-learning", "nlp"}
        extractor.save_keywords(keywords)

        result = extractor.get_keywords_for_search()

        assert isinstance(result, list)
        assert set(result) == keywords
```

- [ ] **Step 3: 运行测试确认失败**

```bash
py -m pytest tests/test_keywords.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.keywords'"

- [ ] **Step 4: 实现关键词提取器**

创建 `src/ai_scraper/keywords/extractor.py`:

```python
"""Keyword extraction from repository data."""

import re
from pathlib import Path
from typing import Optional

from ai_scraper.models.repository import Repository


# Common English stopwords to filter
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "and", "but", "if", "or", "because", "until", "while", "this", "that",
    "these", "those", "it", "its", "they", "them", "their", "what", "which",
    "who", "whom", "he", "him", "his", "she", "her", "hers", "we", "us",
    "our", "you", "your", "yours", "i", "me", "my", "mine",
}


class KeywordExtractor:
    """Extract and manage keywords from repository data."""

    def __init__(self, keywords_file: Path, max_keywords: int = 100):
        """Initialize the extractor.

        Args:
            keywords_file: Path to keywords file.
            max_keywords: Maximum number of keywords to keep.
        """
        self.keywords_file = Path(keywords_file)
        self.max_keywords = max_keywords

    def load_keywords(self) -> set[str]:
        """Load existing keywords from file.

        Returns:
            Set of keywords.
        """
        if not self.keywords_file.exists():
            return set()

        with open(self.keywords_file, "r", encoding="utf-8") as f:
            keywords = {line.strip().lower() for line in f if line.strip()}

        return keywords

    def save_keywords(self, keywords: set[str]) -> None:
        """Save keywords to file.

        Args:
            keywords: Set of keywords to save.
        """
        self.keywords_file.parent.mkdir(parents=True, exist_ok=True)

        # Sort for consistent output
        sorted_keywords = sorted(keywords)

        with open(self.keywords_file, "w", encoding="utf-8") as f:
            for keyword in sorted_keywords:
                f.write(f"{keyword}\n")

    def extract_from_repos(self, repos: list[Repository]) -> set[str]:
        """Extract keywords from repository list.

        Args:
            repos: List of repositories.

        Returns:
            Set of extracted keywords.
        """
        keywords = set()

        for repo in repos:
            # Extract from topics (highest quality)
            keywords.update(self._extract_from_topics(repo))

            # Extract from description
            keywords.update(self._extract_from_description(repo))

            # Extract from name
            keywords.update(self._extract_from_name(repo))

        return keywords

    def _extract_from_topics(self, repo: Repository) -> set[str]:
        """Extract keywords from topics."""
        return {topic.lower() for topic in repo.topics if topic}

    def _extract_from_description(self, repo: Repository) -> set[str]:
        """Extract keywords from description."""
        if not repo.description:
            return set()

        # Simple word extraction: split on non-alphanumeric
        words = re.findall(r'[a-zA-Z][a-zA-Z0-9\-]*', repo.description.lower())

        # Filter stopwords and short words
        filtered = {
            word for word in words
            if word not in STOPWORDS and len(word) >= 2 and not word.isdigit()
        }

        return filtered

    def _extract_from_name(self, repo: Repository) -> set[str]:
        """Extract keywords from repository name."""
        # Get the repo name part (after owner/)
        name = repo.name.split("/")[-1] if "/" in repo.name else repo.name

        # Split on common separators
        parts = re.split(r'[-_]', name.lower())

        # Filter stopwords and short words
        filtered = {
            part for part in parts
            if part not in STOPWORDS and len(part) >= 2 and not part.isdigit()
        }

        return filtered

    def merge_keywords(self, existing: set[str], new: set[str]) -> set[str]:
        """Merge new keywords with existing, respecting limit.

        Args:
            existing: Existing keywords.
            new: New keywords to merge.

        Returns:
            Merged keywords set (limited to max_keywords).
        """
        combined = existing | new

        if len(combined) <= self.max_keywords:
            return combined

        # Prioritize: existing first, then new by some criteria
        # For simplicity, just take first N
        return set(list(combined)[:self.max_keywords])

    def get_keywords_for_search(self) -> list[str]:
        """Get keywords as list for search queries.

        Returns:
            List of keywords.
        """
        return list(self.load_keywords())
```

- [ ] **Step 5: 运行测试确认通过**

```bash
py -m pytest tests/test_keywords.py -v
```

Expected: PASS (9 tests)

- [ ] **Step 6: 提交关键词模块**

```bash
git add src/ai_scraper/keywords/ tests/test_keywords.py
git commit -m "feat: add keyword extraction module"
```

---

## Task 3: 创建 Markdown 输出模块

**Files:**
- Create: `src/ai_scraper/output/__init__.py`
- Create: `src/ai_scraper/output/markdown.py`
- Create: `tests/test_output.py`

- [ ] **Step 1: 创建 output 包初始化文件**

创建 `src/ai_scraper/output/__init__.py`:

```python
"""Output module for generating reports."""

from ai_scraper.output.markdown import MarkdownExporter

__all__ = ["MarkdownExporter"]
```

- [ ] **Step 2: 编写 Markdown 导出器测试**

创建 `tests/test_output.py`:

```python
"""Tests for Markdown output."""

import tempfile
from datetime import datetime
from pathlib import Path

from ai_scraper.output.markdown import MarkdownExporter
from ai_scraper.models.repository import Repository


def make_repo(name: str, stars: int = 100, language: str = "Python", description: str = "Test repo") -> Repository:
    """Helper to create test repository."""
    return Repository(
        id=1,
        name=name,
        full_name=name,
        description=description,
        stars=stars,
        language=language,
        topics=["ai"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url=f"https://github.com/{name}",
    )


def test_export_creates_directory():
    """Test that export creates output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        exporter = MarkdownExporter(output_dir)

        repos = [make_repo("test/repo")]
        result_path = exporter.export_repositories(repos)

        assert output_dir.exists()
        assert result_path.exists()


def test_export_creates_markdown_file():
    """Test that export creates markdown file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MarkdownExporter(Path(tmpdir) / "output")

        repos = [make_repo("test/repo")]
        result_path = exporter.export_repositories(repos)

        assert result_path.suffix == ".md"


def test_export_includes_headers():
    """Test that export includes markdown headers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MarkdownExporter(Path(tmpdir) / "output")

        repos = [make_repo("test/repo")]
        result_path = exporter.export_repositories(repos)

        content = result_path.read_text(encoding="utf-8")

        assert "# AI Repositories" in content
        assert "更新时间" in content
        assert "总计" in content


def test_export_includes_table_headers():
    """Test that export includes table headers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MarkdownExporter(Path(tmpdir) / "output")

        repos = [make_repo("test/repo")]
        result_path = exporter.export_repositories(repos)

        content = result_path.read_text(encoding="utf-8")

        assert "| Name |" in content
        assert "| Stars |" in content
        assert "| Language |" in content
        assert "| Description |" in content
        assert "| URL |" in content


def test_export_includes_repo_data():
    """Test that export includes repository data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MarkdownExporter(Path(tmpdir) / "output")

        repos = [make_repo("test/awesome-ai", stars=1000, language="Go", description="Awesome AI toolkit")]
        result_path = exporter.export_repositories(repos)

        content = result_path.read_text(encoding="utf-8")

        assert "test/awesome-ai" in content
        assert "1000" in content
        assert "Go" in content
        assert "Awesome AI toolkit" in content


def test_export_multiple_repos():
    """Test exporting multiple repositories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MarkdownExporter(Path(tmpdir) / "output")

        repos = [
            make_repo("test/repo1", stars=100),
            make_repo("test/repo2", stars=200),
            make_repo("test/repo3", stars=300),
        ]
        result_path = exporter.export_repositories(repos)

        content = result_path.read_text(encoding="utf-8")

        assert "test/repo1" in content
        assert "test/repo2" in content
        assert "test/repo3" in content
        assert "总计: 3" in content
```

- [ ] **Step 3: 运行测试确认失败**

```bash
py -m pytest tests/test_output.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.output'"

- [ ] **Step 4: 实现 Markdown 导出器**

创建 `src/ai_scraper/output/markdown.py`:

```python
"""Markdown table exporter."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_scraper.models.repository import Repository


class MarkdownExporter:
    """Export repositories as Markdown table."""

    def __init__(self, output_dir: Path, filename: str = "repositories.md"):
        """Initialize the exporter.

        Args:
            output_dir: Directory for output files.
            filename: Output filename.
        """
        self.output_dir = Path(output_dir)
        self.filename = filename

    def export_repositories(self, repos: list[Repository]) -> Path:
        """Export repositories as Markdown table.

        Args:
            repos: List of repositories to export.

        Returns:
            Path to generated file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        content = self._format_table(repos)

        output_path = self.output_dir / self.filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def _format_table(self, repos: list[Repository]) -> str:
        """Format repositories as Markdown table.

        Args:
            repos: List of repositories.

        Returns:
            Markdown formatted string.
        """
        lines = []

        # Header
        lines.append("# AI Repositories")
        lines.append("")
        lines.append(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**总计:** {len(repos)} 个仓库")
        lines.append("")

        # Table header
        lines.append("| Name | Stars | Language | Description | URL |")
        lines.append("|------|-------|----------|-------------|-----|")

        # Table rows
        for repo in repos:
            name = repo.name
            stars = f"{repo.stars:,}"
            language = repo.language or "-"
            description = self._clean_description(repo.description)
            url = f"[GitHub]({repo.url})"

            lines.append(f"| {name} | {stars} | {language} | {description} | {url} |")

        return "\n".join(lines)

    def _clean_description(self, description: Optional[str]) -> str:
        """Clean description for table cell.

        Args:
            description: Original description.

        Returns:
            Cleaned description.
        """
        if not description:
            return "-"

        # Remove newlines and extra spaces
        cleaned = " ".join(description.split())

        # Truncate if too long
        if len(cleaned) > 50:
            cleaned = cleaned[:47] + "..."

        # Escape pipe characters
        cleaned = cleaned.replace("|", "\\|")

        return cleaned
```

- [ ] **Step 5: 运行测试确认通过**

```bash
py -m pytest tests/test_output.py -v
```

Expected: PASS (6 tests)

- [ ] **Step 6: 提交 Markdown 输出模块**

```bash
git add src/ai_scraper/output/ tests/test_output.py
git commit -m "feat: add Markdown table exporter"
```

---

## Task 4: 集成到 CLI

**Files:**
- Modify: `src/ai_scraper/cli.py`

- [ ] **Step 1: 在 scrape 命令中导入新模块**

在 `src/ai_scraper/cli.py` 顶部添加导入：

```python
from ai_scraper.keywords.extractor import KeywordExtractor
from ai_scraper.output.markdown import MarkdownExporter
```

- [ ] **Step 2: 修改 scrape 命令添加关键词提取和 Markdown 导出**

修改 `scrape` 命令的 `run_scrape` 函数，在爬取完成后添加：

```python
async def run_scrape():
    client = GitHubClient(token=config.github.token)
    db = Database(Path(config.database.path))
    db.init_db()
    filter_instance = AIFilter()

    # Initialize new modules
    keyword_extractor = KeywordExtractor(
        Path(config.keywords.file),
        max_keywords=config.keywords.max_keywords
    )
    markdown_exporter = MarkdownExporter(
        Path(config.output.dir),
        filename=config.output.filename
    )

    try:
        # ... existing scrape code ...

        # After scraping, extract keywords
        if all_repos:
            console.print("[dim]Extracting keywords...[/dim]")
            existing_keywords = keyword_extractor.load_keywords()
            new_keywords = keyword_extractor.extract_from_repos(all_repos)
            merged = keyword_extractor.merge_keywords(existing_keywords, new_keywords)
            keyword_extractor.save_keywords(merged)
            console.print(f"[dim]Keywords updated: {len(merged)} total[/dim]")

            # Export to Markdown
            console.print("[dim]Generating Markdown report...[/dim]")
            output_path = markdown_exporter.export_repositories(all_repos)
            console.print(f"[dim]Report saved to: {output_path}[/dim]")

        console.print(f"[bold green]Scraped {len(all_repos)} AI repositories[/bold green]")

    finally:
        await client.close()
        db.close()
```

- [ ] **Step 3: 添加 keywords 子命令组**

在 `src/ai_scraper/cli.py` 中添加新的命令组：

```python
@cli.group()
def keywords_cmd():
    """Keywords management."""
    pass


@keywords_cmd.command("list")
@click.pass_context
def keywords_list(ctx: click.Context):
    """List all keywords."""
    config: Config = ctx.obj["config"]
    extractor = KeywordExtractor(Path(config.keywords.file))

    keywords = extractor.get_keywords_for_search()

    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return

    console.print(f"[bold]Keywords ({len(keywords)}):[/bold]")
    for kw in sorted(keywords):
        console.print(f"  {kw}")


@keywords_cmd.command("extract")
@click.pass_context
def keywords_extract(ctx: click.Context):
    """Manually extract keywords from existing database."""
    config: Config = ctx.obj["config"]

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db = Database(Path(config.database.path))
    db.init_db()
    repos = db.get_all_repositories(limit=10000)
    db.close()

    if not repos:
        console.print("[yellow]No repositories in database.[/yellow]")
        return

    extractor = KeywordExtractor(Path(config.keywords.file), max_keywords=config.keywords.max_keywords)

    existing = extractor.load_keywords()
    new = extractor.extract_from_repos(repos)
    merged = extractor.merge_keywords(existing, new)
    extractor.save_keywords(merged)

    console.print(f"[green]Extracted {len(new)} new keywords[/green]")
    console.print(f"[green]Total: {len(merged)} keywords[/green]")


@keywords_cmd.command("clear")
@click.pass_context
def keywords_clear(ctx: click.Context):
    """Clear all keywords."""
    config: Config = ctx.obj["config"]

    extractor = KeywordExtractor(Path(config.keywords.file))
    extractor.save_keywords(set())

    console.print("[green]Keywords cleared.[/green]")


cli.add_command(keywords_cmd, name="keywords")
```

- [ ] **Step 4: 运行所有测试确认无破坏**

```bash
py -m pytest tests/ -v
```

Expected: PASS (all tests)

- [ ] **Step 5: 提交 CLI 集成**

```bash
git add src/ai_scraper/cli.py
git commit -m "feat: integrate keywords and markdown output into CLI"
```

---

## Task 5: 更新 .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 添加运行时生成的文件到 .gitignore**

在 `.gitignore` 中添加：

```
# Generated files
keywords.txt
output/
```

- [ ] **Step 2: 提交 .gitignore 更新**

```bash
git add .gitignore
git commit -m "chore: ignore generated keywords and output files"
```

---

## Task 6: 更新文档

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README 添加新功能说明**

在 README.md 的 Commands 部分添加：

```markdown
## Commands

| Command | Description |
|---------|-------------|
| `ai-scraper scrape` | Scrape AI repositories from GitHub |
| `ai-scraper list` | List scraped repositories |
| `ai-scraper trending` | Show trending repositories by star growth |
| `ai-scraper keywords list` | List all keywords |
| `ai-scraper keywords extract` | Extract keywords from database |
| `ai-scraper keywords clear` | Clear keywords |
| `ai-scraper config init` | Initialize config file |
| `ai-scraper config show` | Show current config |
| `ai-scraper db stats` | Show database statistics |
| `ai-scraper db export` | Export data to CSV/JSON |
```

在 Features 部分添加：

```markdown
## Features

- Search and filter AI-related repositories by keywords and topics
- **Dynamic keyword extraction** - Automatically learns new keywords from scraped repos
- **Markdown report generation** - Generates readable reports in `output/repositories.md`
- Local SQLite storage with trend analysis
- Configurable filtering and scraping options
- Rate limiting with GitHub API token support
- Export to CSV/JSON formats
```

- [ ] **Step 2: 提交文档更新**

```bash
git add README.md
git commit -m "docs: update README with keywords and output features"
```

---

## Task 7: 最终验证

- [ ] **Step 1: 运行所有测试**

```bash
py -m pytest tests/ -v
```

Expected: PASS (all tests)

- [ ] **Step 2: 测试完整流程**

```bash
# 测试爬取（会自动提取关键词和生成 Markdown）
py -m ai_scraper.cli scrape --max-results 10

# 检查关键词文件
py -m ai_scraper.cli keywords list

# 检查 Markdown 输出
cat output/repositories.md
```

- [ ] **Step 3: 推送到 GitHub**

```bash
git push origin master
```

---

## 实现完成检查清单

- [ ] 配置模块更新完成
- [ ] 关键词提取模块完成并测试通过
- [ ] Markdown 输出模块完成并测试通过
- [ ] CLI 集成完成
- [ ] .gitignore 更新
- [ ] 文档更新
- [ ] 所有测试通过
- [ ] 推送到 GitHub
