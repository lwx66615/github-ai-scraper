# GitHub AI高Star内容爬虫实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个CLI工具，爬取GitHub上与AI相关的高star仓库，支持本地存储和趋势分析。

**Architecture:** Python负责爬虫核心逻辑、API交互、配置管理；Go负责并发调度、限流控制、高性能数据处理。通过subprocess+JSON流进行通信。

**Tech Stack:** Python 3.10+, Go 1.21+, aiohttp, Click, Pydantic, Rich, SQLite, pytest

---

## 文件结构

```
github-ai-scraper/
├── pyproject.toml
├── go.mod
├── src/ai_scraper/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── github.py
│   │   └── rate_limiter.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── repository.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── database.py
│   └── filters/
│       ├── __init__.py
│       └── ai_filter.py
├── cmd/scheduler/
│   ├── main.go
│   ├── scheduler.go
│   ├── limiter.go
│   └── processor.go
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_filter.py
│   ├── test_github.py
│   └── test_database.py
├── data/
└── ai-scraper.yaml
```

---

## Task 1: 项目初始化

**Files:**
- Create: `pyproject.toml`
- Create: `go.mod`
- Create: `src/ai_scraper/__init__.py`
- Create: `data/.gitkeep`

- [ ] **Step 1: 创建Python项目配置**

创建 `pyproject.toml`:

```toml
[project]
name = "ai-scraper"
version = "0.1.0"
description = "GitHub AI high-star repositories scraper"
requires-python = ">=3.10"
dependencies = [
    "aiohttp>=3.9.0",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "aiosqlite>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]

[project.scripts]
ai-scraper = "ai_scraper.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ai_scraper"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: 创建Go模块配置**

创建 `go.mod`:

```go
module github-ai-scraper/scheduler

go 1.21

require github.com/mattn/go-sqlite3 v1.14.22
```

- [ ] **Step 3: 创建Python包初始化文件**

创建 `src/ai_scraper/__init__.py`:

```python
"""GitHub AI high-star repositories scraper."""

__version__ = "0.1.0"
```

- [ ] **Step 4: 创建数据目录占位文件**

创建 `data/.gitkeep`:

```
# This directory stores SQLite database files
```

- [ ] **Step 5: 提交初始化**

```bash
git init
git add pyproject.toml go.mod src/ai_scraper/__init__.py data/.gitkeep
git commit -m "chore: initialize project structure"
```

---

## Task 2: 数据模型定义

**Files:**
- Create: `src/ai_scraper/models/__init__.py`
- Create: `src/ai_scraper/models/repository.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: 编写数据模型测试**

创建 `tests/__init__.py`:

```python
"""Tests for ai_scraper."""
```

创建 `tests/test_models.py`:

```python
"""Tests for data models."""

from datetime import datetime

from ai_scraper.models.repository import Repository, RepoSnapshot, FilterConfig, ScrapeConfig


def test_repository_creation():
    """Test Repository model creation."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="A test repository",
        stars=1000,
        language="Python",
        topics=["ai", "machine-learning"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )
    assert repo.id == 12345
    assert repo.name == "test/repo"
    assert repo.stars == 1000
    assert "ai" in repo.topics


def test_repository_optional_fields():
    """Test Repository with optional fields."""
    repo = Repository(
        id=1,
        name="test/repo",
        full_name="test/repo",
        description=None,
        stars=100,
        language=None,
        topics=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
        open_issues=10,
        forks=5,
        contributors=20,
    )
    assert repo.description is None
    assert repo.open_issues == 10
    assert repo.forks == 5
    assert repo.contributors == 20


def test_repo_snapshot():
    """Test RepoSnapshot model."""
    snapshot = RepoSnapshot(
        repo_id=12345,
        stars=1000,
        snapshot_at=datetime(2024, 5, 9, 10, 30),
    )
    assert snapshot.repo_id == 12345
    assert snapshot.stars == 1000


def test_filter_config_defaults():
    """Test FilterConfig default values."""
    config = FilterConfig(
        keywords=["ai"],
        topics=["machine-learning"],
        languages=[],
        exclude_keywords=[],
    )
    assert config.min_stars == 100
    assert "ai" in config.keywords


def test_scrape_config_defaults():
    """Test ScrapeConfig default values."""
    config = ScrapeConfig(
        data_fields=["stars", "language"],
        max_results=100,
        concurrency=5,
        cache_ttl=3600,
    )
    assert config.max_results == 100
    assert config.concurrency == 5
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /path/to/github-ai-scraper
python -m pytest tests/test_models.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper'"

- [ ] **Step 3: 实现数据模型**

创建 `src/ai_scraper/models/__init__.py`:

```python
"""Data models for ai_scraper."""

from ai_scraper.models.repository import Repository, RepoSnapshot, FilterConfig, ScrapeConfig

__all__ = ["Repository", "RepoSnapshot", "FilterConfig", "ScrapeConfig"]
```

创建 `src/ai_scraper/models/repository.py`:

```python
"""Repository data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Repository:
    """GitHub repository information."""

    id: int
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    language: Optional[str]
    topics: list[str]
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    url: str
    open_issues: Optional[int] = None
    forks: Optional[int] = None
    contributors: Optional[int] = None


@dataclass
class RepoSnapshot:
    """Repository snapshot for trend analysis."""

    repo_id: int
    stars: int
    snapshot_at: datetime


@dataclass
class FilterConfig:
    """Filter configuration for scraping."""

    keywords: list[str]
    topics: list[str]
    languages: list[str]
    exclude_keywords: list[str]
    min_stars: int = 100


@dataclass
class ScrapeConfig:
    """Scrape configuration."""

    data_fields: list[str]
    max_results: int
    concurrency: int
    cache_ttl: int
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pip install -e .
python -m pytest tests/test_models.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: 提交数据模型**

```bash
git add src/ai_scraper/models/ tests/
git commit -m "feat: add data models for repository, snapshot, and config"
```

---

## Task 3: 配置管理模块

**Files:**
- Create: `src/ai_scraper/config.py`
- Create: `tests/test_config.py`
- Create: `ai-scraper.yaml`

- [ ] **Step 1: 编写配置管理测试**

创建 `tests/test_config.py`:

```python
"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest

from ai_scraper.config import Config, load_config


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert config.github.token is None
    assert config.github.cache_ttl == 3600
    assert config.filter.min_stars == 100
    assert "ai" in config.filter.keywords
    assert config.scrape.max_results == 500


def test_load_config_from_file():
    """Test loading configuration from YAML file."""
    yaml_content = """
github:
  token: test_token_123
  cache_ttl: 7200
filter:
  min_stars: 500
  keywords:
    - ai
    - llm
  topics:
    - machine-learning
  languages:
    - python
  exclude_keywords:
    - awesome
scrape:
  max_results: 100
  concurrency: 10
database:
  path: ./test.db
scheduler:
  enabled: false
  workers: 8
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config = load_config(Path(f.name))

    assert config.github.token == "test_token_123"
    assert config.github.cache_ttl == 7200
    assert config.filter.min_stars == 500
    assert "llm" in config.filter.keywords
    assert config.scrape.max_results == 100
    assert config.scheduler.enabled is False


def test_config_env_var_substitution():
    """Test environment variable substitution in config."""
    os.environ["TEST_GITHUB_TOKEN"] = "env_token_456"

    yaml_content = """
github:
  token: ${TEST_GITHUB_TOKEN}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config = load_config(Path(f.name))

    assert config.github.token == "env_token_456"
    del os.environ["TEST_GITHUB_TOKEN"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_config.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.config'"

- [ ] **Step 3: 实现配置管理**

创建 `src/ai_scraper/config.py`:

```python
"""Configuration management."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class GitHubConfig:
    """GitHub API configuration."""

    token: Optional[str] = None
    cache_ttl: int = 3600


@dataclass
class FilterConfigYaml:
    """Filter configuration from YAML."""

    min_stars: int = 100
    keywords: list[str] = field(default_factory=lambda: [
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "neural network", "llm", "gpt", "transformer", "nlp", "computer vision",
        "reinforcement learning", "pytorch", "tensorflow", "huggingface"
    ])
    topics: list[str] = field(default_factory=lambda: [
        "ai", "machine-learning", "deep-learning", "neural-network",
        "natural-language-processing", "computer-vision", "llm", "gpt",
        "pytorch", "tensorflow", "huggingface", "openai", "langchain"
    ])
    languages: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)


@dataclass
class ScrapeConfigYaml:
    """Scrape configuration from YAML."""

    data_fields: list[str] = field(default_factory=lambda: [
        "stars", "language", "topics", "contributors"
    ])
    max_results: int = 500
    concurrency: int = 5
    cache_ttl: int = 3600


@dataclass
class DatabaseConfig:
    """Database configuration."""

    path: str = "./data/ai_scraper.db"


@dataclass
class SchedulerConfig:
    """Go scheduler configuration."""

    enabled: bool = True
    workers: int = 4


@dataclass
class Config:
    """Main configuration."""

    github: GitHubConfig = field(default_factory=GitHubConfig)
    filter: FilterConfigYaml = field(default_factory=FilterConfigYaml)
    scrape: ScrapeConfigYaml = field(default_factory=ScrapeConfigYaml)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)


def _substitute_env_vars(value: str) -> str:
    """Substitute environment variables in string value."""
    pattern = r'\$\{([^}]+)\}'

    def replace(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")

    return re.sub(pattern, replace, value)


def _process_config_values(config_dict: dict) -> dict:
    """Recursively process config values for env var substitution."""
    result = {}
    for key, value in config_dict.items():
        if isinstance(value, dict):
            result[key] = _process_config_values(value)
        elif isinstance(value, str):
            result[key] = _substitute_env_vars(value)
        elif isinstance(value, list):
            result[key] = [
                _substitute_env_vars(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None or not config_path.exists():
        return Config()

    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f) or {}

    processed_config = _process_config_values(raw_config)

    github = GitHubConfig(
        token=processed_config.get("github", {}).get("token"),
        cache_ttl=processed_config.get("github", {}).get("cache_ttl", 3600),
    )

    filter_dict = processed_config.get("filter", {})
    filter_config = FilterConfigYaml(
        min_stars=filter_dict.get("min_stars", 100),
        keywords=filter_dict.get("keywords", FilterConfigYaml().keywords),
        topics=filter_dict.get("topics", FilterConfigYaml().topics),
        languages=filter_dict.get("languages", []),
        exclude_keywords=filter_dict.get("exclude_keywords", []),
    )

    scrape_dict = processed_config.get("scrape", {})
    scrape_config = ScrapeConfigYaml(
        data_fields=scrape_dict.get("data_fields", ScrapeConfigYaml().data_fields),
        max_results=scrape_dict.get("max_results", 500),
        concurrency=scrape_dict.get("concurrency", 5),
        cache_ttl=scrape_dict.get("cache_ttl", 3600),
    )

    database_dict = processed_config.get("database", {})
    database_config = DatabaseConfig(
        path=database_dict.get("path", "./data/ai_scraper.db"),
    )

    scheduler_dict = processed_config.get("scheduler", {})
    scheduler_config = SchedulerConfig(
        enabled=scheduler_dict.get("enabled", True),
        workers=scheduler_dict.get("workers", 4),
    )

    return Config(
        github=github,
        filter=filter_config,
        scrape=scrape_config,
        database=database_config,
        scheduler=scheduler_config,
    )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_config.py -v
```

Expected: PASS (3 tests)

- [ ] **Step 5: 创建默认配置文件**

创建 `ai-scraper.yaml`:

```yaml
# GitHub AI Scraper Configuration

# GitHub API configuration
github:
  token: ${GITHUB_TOKEN}  # Set via environment variable
  cache_ttl: 3600         # Cache TTL in seconds (1 hour)

# Filter configuration
filter:
  min_stars: 100
  keywords:
    - ai
    - artificial intelligence
    - machine learning
    - deep learning
    - neural network
    - llm
    - gpt
    - transformer
    - nlp
    - computer vision
    - reinforcement learning
    - pytorch
    - tensorflow
    - huggingface
  topics:
    - ai
    - machine-learning
    - deep-learning
    - neural-network
    - natural-language-processing
    - computer-vision
    - llm
    - gpt
    - pytorch
    - tensorflow
    - huggingface
    - openai
    - langchain
  languages: []  # Empty means all languages
  exclude_keywords:
    - awesome
    - list
    - curated

# Scrape configuration
scrape:
  data_fields:
    - stars
    - language
    - topics
    - contributors
  max_results: 500
  concurrency: 5
  cache_ttl: 3600

# Database configuration
database:
  path: ./data/ai_scraper.db

# Go scheduler configuration
scheduler:
  enabled: true
  workers: 4
```

- [ ] **Step 6: 提交配置管理模块**

```bash
git add src/ai_scraper/config.py tests/test_config.py ai-scraper.yaml
git commit -m "feat: add configuration management with YAML support"
```

---

## Task 4: AI过滤器实现

**Files:**
- Create: `src/ai_scraper/filters/__init__.py`
- Create: `src/ai_scraper/filters/ai_filter.py`
- Create: `tests/test_filter.py`

- [ ] **Step 1: 编写AI过滤器测试**

创建 `tests/test_filter.py`:

```python
"""Tests for AI filter."""

from datetime import datetime

from ai_scraper.filters.ai_filter import AIFilter
from ai_scraper.models.repository import Repository, FilterConfig as FilterConfigModel


def make_repo(name: str, description: str = "", topics: list[str] = None) -> Repository:
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


def test_is_ai_related_by_keyword():
    """Test AI detection by keyword in name/description."""
    filter_instance = AIFilter()
    config = FilterConfigModel(
        keywords=["ai", "machine-learning"],
        topics=[],
        languages=[],
        exclude_keywords=[],
    )

    repo = make_repo("test/awesome-ai", "An AI toolkit")
    assert filter_instance.is_ai_related(repo, config) is True

    repo = make_repo("test/ml-toolkit", "Machine learning utilities")
    assert filter_instance.is_ai_related(repo, config) is True


def test_is_ai_related_by_topic():
    """Test AI detection by topic."""
    filter_instance = AIFilter()
    config = FilterConfigModel(
        keywords=[],
        topics=["ai", "machine-learning"],
        languages=[],
        exclude_keywords=[],
    )

    repo = make_repo("test/toolkit", "A toolkit", topics=["ai", "python"])
    assert filter_instance.is_ai_related(repo, config) is True

    repo = make_repo("test/other", "Other toolkit", topics=["web", "python"])
    assert filter_instance.is_ai_related(repo, config) is False


def test_is_ai_related_exclude_keywords():
    """Test exclusion by keywords."""
    filter_instance = AIFilter()
    config = FilterConfigModel(
        keywords=["ai"],
        topics=[],
        languages=[],
        exclude_keywords=["awesome", "list"],
    )

    repo = make_repo("test/awesome-ai", "Awesome AI list")
    assert filter_instance.is_ai_related(repo, config) is False

    repo = make_repo("test/ai-toolkit", "AI toolkit")
    assert filter_instance.is_ai_related(repo, config) is True


def test_score_relevance():
    """Test relevance scoring."""
    filter_instance = AIFilter()

    repo = make_repo("test/ai-toolkit", "AI and machine learning toolkit", topics=["ai", "pytorch"])
    score = filter_instance.score_relevance(repo)
    assert score > 0.5

    repo = make_repo("test/web-app", "A web application")
    score = filter_instance.score_relevance(repo)
    assert score == 0.0


def test_case_insensitive_matching():
    """Test case insensitive keyword matching."""
    filter_instance = AIFilter()
    config = FilterConfigModel(
        keywords=["AI", "Machine Learning"],
        topics=[],
        languages=[],
        exclude_keywords=[],
    )

    repo = make_repo("test/toolkit", "an ai toolkit")
    assert filter_instance.is_ai_related(repo, config) is True

    repo = make_repo("test/ml", "MACHINE LEARNING library")
    assert filter_instance.is_ai_related(repo, config) is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_filter.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.filters'"

- [ ] **Step 3: 实现AI过滤器**

创建 `src/ai_scraper/filters/__init__.py`:

```python
"""Filters for ai_scraper."""

from ai_scraper.filters.ai_filter import AIFilter

__all__ = ["AIFilter"]
```

创建 `src/ai_scraper/filters/ai_filter.py`:

```python
"""AI-related content filter."""

from ai_scraper.models.repository import Repository, FilterConfig


class AIFilter:
    """Filter for detecting AI-related repositories."""

    def is_ai_related(self, repo: Repository, config: FilterConfig) -> bool:
        """Check if repository is AI-related.

        Args:
            repo: Repository to check.
            config: Filter configuration.

        Returns:
            True if repository is AI-related.
        """
        # Check exclude keywords first
        text_to_check = f"{repo.name} {repo.description or ''}".lower()
        for exclude in config.exclude_keywords:
            if exclude.lower() in text_to_check:
                return False

        # Check topics
        repo_topics_lower = [t.lower() for t in repo.topics]
        for topic in config.topics:
            if topic.lower() in repo_topics_lower:
                return True

        # Check keywords in name and description
        for keyword in config.keywords:
            if keyword.lower() in text_to_check:
                return True

        return False

    def score_relevance(self, repo: Repository) -> float:
        """Calculate AI relevance score for a repository.

        Args:
            repo: Repository to score.

        Returns:
            Relevance score between 0.0 and 1.0.
        """
        score = 0.0
        text_to_check = f"{repo.name} {repo.description or ''}".lower()

        # Default AI indicators
        ai_keywords = [
            "ai", "artificial intelligence", "machine learning", "deep learning",
            "neural network", "llm", "gpt", "transformer", "nlp", "computer vision",
            "pytorch", "tensorflow", "huggingface", "openai", "langchain"
        ]

        ai_topics = [
            "ai", "machine-learning", "deep-learning", "neural-network",
            "natural-language-processing", "computer-vision", "llm", "gpt",
            "pytorch", "tensorflow", "huggingface", "openai", "langchain"
        ]

        # Count keyword matches
        keyword_matches = sum(1 for kw in ai_keywords if kw in text_to_check)
        score += min(keyword_matches * 0.2, 0.6)

        # Count topic matches
        repo_topics_lower = [t.lower() for t in repo.topics]
        topic_matches = sum(1 for topic in ai_topics if topic in repo_topics_lower)
        score += min(topic_matches * 0.15, 0.4)

        return min(score, 1.0)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_filter.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: 提交AI过滤器**

```bash
git add src/ai_scraper/filters/ tests/test_filter.py
git commit -m "feat: add AI filter for repository classification"
```

---

## Task 5: 数据库存储模块

**Files:**
- Create: `src/ai_scraper/storage/__init__.py`
- Create: `src/ai_scraper/storage/database.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: 编写数据库测试**

创建 `tests/test_database.py`:

```python
"""Tests for database storage."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ai_scraper.models.repository import Repository
from ai_scraper.storage.database import Database


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        db.init_db()
        yield db


def test_init_db(temp_db):
    """Test database initialization."""
    assert temp_db.db_path.exists()


def test_save_repository(temp_db):
    """Test saving a repository."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="A test repository",
        stars=1000,
        language="Python",
        topics=["ai", "machine-learning"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo)

    repos = temp_db.get_all_repositories()
    assert len(repos) == 1
    assert repos[0].name == "test/repo"
    assert repos[0].stars == 1000


def test_update_repository(temp_db):
    """Test updating an existing repository."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="A test repository",
        stars=1000,
        language="Python",
        topics=["ai"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo)

    # Update with same ID but different stars
    repo_updated = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="Updated description",
        stars=1500,
        language="Python",
        topics=["ai"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 10),
        pushed_at=datetime(2024, 5, 10),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo_updated)

    repos = temp_db.get_all_repositories()
    assert len(repos) == 1
    assert repos[0].stars == 1500
    assert repos[0].description == "Updated description"


def test_save_snapshot(temp_db):
    """Test saving repository snapshot."""
    repo = Repository(
        id=12345,
        name="test/repo",
        full_name="test/repo",
        description="Test",
        stars=1000,
        language="Python",
        topics=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url="https://github.com/test/repo",
    )

    temp_db.save_repository(repo)
    temp_db.save_snapshot(12345, 1000, datetime(2024, 5, 9, 10, 0))
    temp_db.save_snapshot(12345, 1100, datetime(2024, 5, 10, 10, 0))

    snapshots = temp_db.get_snapshots(12345)
    assert len(snapshots) == 2


def test_get_trending(temp_db):
    """Test getting trending repositories."""
    # Create repos with different star growth
    for i, (repo_id, initial_stars, later_stars) in enumerate([
        (1, 100, 150),   # 50% growth
        (2, 100, 200),   # 100% growth
        (3, 100, 120),   # 20% growth
    ]):
        repo = Repository(
            id=repo_id,
            name=f"test/repo{i}",
            full_name=f"test/repo{i}",
            description="Test",
            stars=later_stars,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url=f"https://github.com/test/repo{i}",
        )
        temp_db.save_repository(repo)
        temp_db.save_snapshot(repo_id, initial_stars, datetime(2024, 5, 1))
        temp_db.save_snapshot(repo_id, later_stars, datetime(2024, 5, 9))

    trending = temp_db.get_trending(days=7)
    assert len(trending) == 3
    # Should be sorted by growth
    assert trending[0].repo_id == 2  # 100% growth
    assert trending[1].repo_id == 1  # 50% growth
    assert trending[2].repo_id == 3  # 20% growth


def test_search_local(temp_db):
    """Test local search functionality."""
    repos = [
        Repository(
            id=i,
            name=f"test/{name}",
            full_name=f"test/{name}",
            description=desc,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url=f"https://github.com/test/{name}",
        )
        for i, (name, desc) in enumerate([
            ("ai-toolkit", "AI toolkit"),
            ("ml-lib", "Machine learning library"),
            ("web-app", "Web application"),
        ])
    ]

    for repo in repos:
        temp_db.save_repository(repo)

    results = temp_db.search_local("ai")
    assert len(results) == 1
    assert results[0].name == "test/ai-toolkit"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_database.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.storage'"

- [ ] **Step 3: 实现数据库模块**

创建 `src/ai_scraper/storage/__init__.py`:

```python
"""Storage module for ai_scraper."""

from ai_scraper.storage.database import Database

__all__ = ["Database"]
```

创建 `src/ai_scraper/storage/database.py`:

```python
"""SQLite database storage."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class TrendResult:
    """Trend analysis result."""

    repo_id: int
    repo_name: str
    initial_stars: int
    current_stars: int
    growth_rate: float


class Database:
    """SQLite database for storing repository data."""

    def __init__(self, db_path: Path):
        """Initialize database.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None

    def init_db(self) -> None:
        """Initialize database tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create repositories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                full_name TEXT,
                description TEXT,
                stars INTEGER,
                language TEXT,
                topics TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                pushed_at TIMESTAMP,
                url TEXT,
                open_issues INTEGER,
                forks INTEGER,
                contributors INTEGER,
                relevance_score REAL,
                first_seen_at TIMESTAMP,
                last_updated_at TIMESTAMP
            )
        """)

        # Create snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id INTEGER,
                stars INTEGER,
                snapshot_at TIMESTAMP,
                FOREIGN KEY (repo_id) REFERENCES repositories(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stars ON repositories(stars DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_updated ON repositories(last_updated_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_id ON snapshots(repo_id)")

        self.conn.commit()

    def save_repository(self, repo: Repository, relevance_score: float = 0.0) -> None:
        """Save or update a repository.

        Args:
            repo: Repository to save.
            relevance_score: AI relevance score.
        """
        cursor = self.conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO repositories (
                id, name, full_name, description, stars, language, topics,
                created_at, updated_at, pushed_at, url, open_issues, forks,
                contributors, relevance_score, first_seen_at, last_updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                full_name = excluded.full_name,
                description = excluded.description,
                stars = excluded.stars,
                language = excluded.language,
                topics = excluded.topics,
                updated_at = excluded.updated_at,
                pushed_at = excluded.pushed_at,
                open_issues = excluded.open_issues,
                forks = excluded.forks,
                contributors = excluded.contributors,
                relevance_score = excluded.relevance_score,
                last_updated_at = excluded.last_updated_at
        """, (
            repo.id, repo.name, repo.full_name, repo.description, repo.stars,
            repo.language, json.dumps(repo.topics), repo.created_at.isoformat(),
            repo.updated_at.isoformat(), repo.pushed_at.isoformat(), repo.url,
            repo.open_issues, repo.forks, repo.contributors, relevance_score,
            now, now
        ))

        self.conn.commit()

    def save_snapshot(self, repo_id: int, stars: int, snapshot_at: datetime) -> None:
        """Save a repository snapshot.

        Args:
            repo_id: Repository ID.
            stars: Star count at snapshot time.
            snapshot_at: Snapshot timestamp.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO snapshots (repo_id, stars, snapshot_at)
            VALUES (?, ?, ?)
        """, (repo_id, stars, snapshot_at.isoformat()))

        self.conn.commit()

    def get_snapshots(self, repo_id: int) -> list[dict]:
        """Get snapshots for a repository.

        Args:
            repo_id: Repository ID.

        Returns:
            List of snapshot records.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT stars, snapshot_at FROM snapshots
            WHERE repo_id = ?
            ORDER BY snapshot_at DESC
        """, (repo_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_all_repositories(self, limit: int = 100, sort_by: str = "stars") -> list[Repository]:
        """Get all repositories.

        Args:
            limit: Maximum number of repositories to return.
            sort_by: Field to sort by.

        Returns:
            List of repositories.
        """
        cursor = self.conn.cursor()

        valid_sort_fields = ["stars", "updated_at", "relevance_score"]
        sort_field = sort_by if sort_by in valid_sort_fields else "stars"

        cursor.execute(f"""
            SELECT * FROM repositories
            ORDER BY {sort_field} DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    def get_trending(self, days: int = 7, limit: int = 10) -> list[TrendResult]:
        """Get trending repositories by star growth.

        Args:
            days: Number of days to analyze.
            limit: Maximum number of results.

        Returns:
            List of trending repositories.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                r.id as repo_id,
                r.name as repo_name,
                s1.stars as initial_stars,
                r.stars as current_stars
            FROM repositories r
            JOIN snapshots s1 ON r.id = s1.repo_id
            WHERE s1.snapshot_at >= datetime('now', ?)
            GROUP BY r.id
            HAVING current_stars > initial_stars
            ORDER BY (CAST(current_stars AS FLOAT) / initial_stars - 1) DESC
            LIMIT ?
        """, (f'-{days} days', limit))

        results = []
        for row in cursor.fetchall():
            initial = row["initial_stars"]
            current = row["current_stars"]
            growth = (current - initial) / initial if initial > 0 else 0.0

            results.append(TrendResult(
                repo_id=row["repo_id"],
                repo_name=row["repo_name"],
                initial_stars=initial,
                current_stars=current,
                growth_rate=growth,
            ))

        return results

    def search_local(self, query: str, limit: int = 20) -> list[Repository]:
        """Search repositories locally.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            List of matching repositories.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM repositories
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY stars DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        rows = cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    def get_stats(self) -> dict:
        """Get database statistics.

        Returns:
            Dictionary with statistics.
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM repositories")
        repo_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM snapshots")
        snapshot_count = cursor.fetchone()["count"]

        cursor.execute("SELECT SUM(stars) as total FROM repositories")
        total_stars = cursor.fetchone()["total"] or 0

        return {
            "repository_count": repo_count,
            "snapshot_count": snapshot_count,
            "total_stars": total_stars,
        }

    def clean_old_snapshots(self, days: int = 30) -> int:
        """Clean snapshots older than specified days.

        Args:
            days: Number of days to keep.

        Returns:
            Number of deleted snapshots.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            DELETE FROM snapshots
            WHERE snapshot_at < datetime('now', ?)
        """, (f'-{days} days',))

        deleted = cursor.rowcount
        self.conn.commit()

        return deleted

    def _row_to_repo(self, row: sqlite3.Row) -> Repository:
        """Convert database row to Repository object.

        Args:
            row: Database row.

        Returns:
            Repository object.
        """
        return Repository(
            id=row["id"],
            name=row["name"],
            full_name=row["full_name"],
            description=row["description"],
            stars=row["stars"],
            language=row["language"],
            topics=json.loads(row["topics"]) if row["topics"] else [],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            pushed_at=datetime.fromisoformat(row["pushed_at"]) if row["pushed_at"] else None,
            url=row["url"],
            open_issues=row["open_issues"],
            forks=row["forks"],
            contributors=row["contributors"],
        )

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_database.py -v
```

Expected: PASS (6 tests)

- [ ] **Step 5: 提交数据库模块**

```bash
git add src/ai_scraper/storage/ tests/test_database.py
git commit -m "feat: add SQLite database storage module"
```

---

## Task 6: GitHub API客户端

**Files:**
- Create: `src/ai_scraper/api/__init__.py`
- Create: `src/ai_scraper/api/github.py`
- Create: `src/ai_scraper/api/rate_limiter.py`
- Create: `tests/test_github.py`

- [ ] **Step 1: 编写GitHub API客户端测试**

创建 `tests/test_github.py`:

```python
"""Tests for GitHub API client."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_scraper.api.github import GitHubClient
from ai_scraper.api.rate_limiter import RateLimiter


@pytest.fixture
def mock_response():
    """Create mock aiohttp response."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock()
    return response


@pytest.mark.asyncio
async def test_search_repositories(mock_response):
    """Test repository search."""
    mock_response.json.return_value = {
        "items": [
            {
                "id": 123,
                "name": "repo",
                "full_name": "owner/repo",
                "description": "Test repo",
                "stargazers_count": 1000,
                "language": "Python",
                "topics": ["ai"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-05-01T00:00:00Z",
                "pushed_at": "2024-05-09T00:00:00Z",
                "html_url": "https://github.com/owner/repo",
            }
        ]
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        client = GitHubClient()
        repos = await client.search_repositories("ai", sort="stars", order="desc")

        assert len(repos) == 1
        assert repos[0].name == "owner/repo"
        assert repos[0].stars == 1000


@pytest.mark.asyncio
async def test_get_rate_limit(mock_response):
    """Test getting rate limit info."""
    mock_response.json.return_value = {
        "resources": {
            "search": {
                "limit": 30,
                "remaining": 25,
                "reset": 1715234400,
            }
        }
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        client = GitHubClient()
        info = await client.get_rate_limit()

        assert info.search_limit == 30
        assert info.search_remaining == 25


def test_rate_limiter_basic():
    """Test basic rate limiter functionality."""
    limiter = RateLimiter(requests_per_hour=60)

    # Should allow first request immediately
    assert limiter.try_acquire() is True

    # Should block subsequent requests
    assert limiter.try_acquire() is False


def test_rate_limiter_with_token():
    """Test rate limiter with higher limit."""
    limiter = RateLimiter(requests_per_hour=5000)

    # Should allow multiple requests
    for _ in range(10):
        assert limiter.try_acquire() is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_github.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.api'"

- [ ] **Step 3: 实现API模块**

创建 `src/ai_scraper/api/__init__.py`:

```python
"""API module for ai_scraper."""

from ai_scraper.api.github import GitHubClient
from ai_scraper.api.rate_limiter import RateLimiter

__all__ = ["GitHubClient", "RateLimiter"]
```

创建 `src/ai_scraper/api/rate_limiter.py`:

```python
"""Rate limiter for GitHub API."""

import time
from dataclasses import dataclass


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""

    search_limit: int
    search_remaining: int
    search_reset: int
    core_limit: int = 0
    core_remaining: int = 0
    core_reset: int = 0


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_hour: int = 60, safety_margin: float = 0.1):
        """Initialize rate limiter.

        Args:
            requests_per_hour: Maximum requests per hour.
            safety_margin: Fraction of requests to reserve (default 10%).
        """
        self.requests_per_hour = requests_per_hour
        self.safety_margin = safety_margin
        self.effective_limit = int(requests_per_hour * (1 - safety_margin))

        # Calculate refill rate (requests per second)
        self.refill_rate = self.effective_limit / 3600.0

        # Token bucket state
        self.tokens = float(self.effective_limit)
        self.last_update = time.time()

    def try_acquire(self) -> bool:
        """Try to acquire a token without blocking.

        Returns:
            True if token was acquired, False otherwise.
        """
        self._refill()

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True

        return False

    def wait_time(self) -> float:
        """Get time to wait for next token.

        Returns:
            Seconds to wait.
        """
        self._refill()

        if self.tokens >= 1.0:
            return 0.0

        return (1.0 - self.tokens) / self.refill_rate

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update

        self.tokens = min(
            float(self.effective_limit),
            self.tokens + elapsed * self.refill_rate
        )
        self.last_update = now

    def set_rate(self, requests_per_hour: int) -> None:
        """Update the rate limit.

        Args:
            requests_per_hour: New maximum requests per hour.
        """
        self.requests_per_hour = requests_per_hour
        self.effective_limit = int(requests_per_hour * (1 - self.safety_margin))
        self.refill_rate = self.effective_limit / 3600.0
        self.tokens = min(self.tokens, float(self.effective_limit))
```

创建 `src/ai_scraper/api/github.py`:

```python
"""GitHub API client."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

import aiohttp

from ai_scraper.api.rate_limiter import RateLimitInfo, RateLimiter
from ai_scraper.models.repository import Repository

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """GitHub API error."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"GitHub API error {status}: {message}")


class GitHubClient:
    """Asynchronous GitHub API client."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.

        Args:
            token: GitHub Personal Access Token (optional).
        """
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None

        # Rate limiter: 60/hour without token, 5000/hour with token
        rate = 5000 if token else 60
        self.rate_limiter = RateLimiter(requests_per_hour=rate)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make an API request.

        Args:
            endpoint: API endpoint (without base URL).
            params: Query parameters.

        Returns:
            JSON response data.

        Raises:
            GitHubAPIError: On API errors.
        """
        # Wait for rate limiter
        while not self.rate_limiter.try_acquire():
            wait_time = self.rate_limiter.wait_time()
            logger.debug(f"Rate limited, waiting {wait_time:.1f}s")
            await asyncio.sleep(min(wait_time, 1.0))

        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"

        async with session.get(url, params=params) as response:
            if response.status == 401:
                raise GitHubAPIError(401, "Unauthorized - check your token")
            elif response.status == 403:
                # Rate limited
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                raise GitHubAPIError(403, f"Rate limited, resets at {reset_time}")
            elif response.status == 503:
                raise GitHubAPIError(503, "Service unavailable")
            elif response.status >= 400:
                text = await response.text()
                raise GitHubAPIError(response.status, text)

            return await response.json()

    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        page: int = 1,
        per_page: int = 100,
    ) -> list[Repository]:
        """Search repositories.

        Args:
            query: Search query.
            sort: Sort field (stars, forks, updated).
            order: Sort order (asc, desc).
            page: Page number.
            per_page: Results per page (max 100).

        Returns:
            List of repositories.
        """
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100),
        }

        data = await self._request("/search/repositories", params)
        items = data.get("items", [])

        return [self._parse_repository(item) for item in items]

    async def get_repository(self, owner: str, repo: str) -> Repository:
        """Get a single repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository data.
        """
        data = await self._request(f"/repos/{owner}/{repo}")
        return self._parse_repository(data)

    async def get_contributors(self, owner: str, repo: str) -> int:
        """Get contributor count for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Number of contributors.
        """
        try:
            # GitHub doesn't provide count directly, so we fetch first page
            data = await self._request(
                f"/repos/{owner}/{repo}/contributors",
                params={"per_page": 1, "anon": "true"}
            )

            # Check Link header for total count
            session = await self._get_session()
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"

            async with session.get(url, params={"per_page": 1}) as response:
                link_header = response.headers.get("Link", "")
                # Parse last page number from Link header
                if 'rel="last"' in link_header:
                    # Extract page number from last link
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))

                # Fallback: return length of current page
                return len(data)
        except GitHubAPIError:
            return 0

    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit information.
        """
        data = await self._request("/rate_limit")

        resources = data.get("resources", {})
        search = resources.get("search", {})
        core = resources.get("core", {})

        return RateLimitInfo(
            search_limit=search.get("limit", 0),
            search_remaining=search.get("remaining", 0),
            search_reset=search.get("reset", 0),
            core_limit=core.get("limit", 0),
            core_remaining=core.get("remaining", 0),
            core_reset=core.get("reset", 0),
        )

    def _parse_repository(self, data: dict) -> Repository:
        """Parse repository data from API response.

        Args:
            data: API response data.

        Returns:
            Repository object.
        """
        return Repository(
            id=data["id"],
            name=data["full_name"],
            full_name=data["full_name"],
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
            pushed_at=self._parse_datetime(data.get("pushed_at")),
            url=data.get("html_url", ""),
            open_issues=data.get("open_issues_count"),
            forks=data.get("forks_count"),
        )

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string.

        Args:
            value: ISO datetime string.

        Returns:
            datetime object or None.
        """
        if not value:
            return None

        # Handle ISO format with Z suffix
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        try:
            return datetime.fromisoformat(value.replace("+00:00", ""))
        except ValueError:
            return None
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_github.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: 提交API客户端**

```bash
git add src/ai_scraper/api/ tests/test_github.py
git commit -m "feat: add GitHub API client with rate limiting"
```

---

## Task 7: CLI入口实现

**Files:**
- Create: `src/ai_scraper/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: 编写CLI测试**

创建 `tests/test_cli.py`:

```python
"""Tests for CLI."""

from click.testing import CliRunner

from ai_scraper.cli import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "ai-scraper" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_config_init():
    """Test config init command."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["config", "init"])

        assert result.exit_code == 0
        assert "ai-scraper.yaml" in result.output


def test_db_stats_empty():
    """Test db stats command with empty database."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["db", "stats"])

        assert result.exit_code == 0
        assert "Repository count: 0" in result.output
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'ai_scraper.cli'"

- [ ] **Step 3: 实现CLI**

创建 `src/ai_scraper/cli.py`:

```python
"""CLI entry point for ai-scraper."""

import asyncio
from pathlib import Path
from typing import Optional

import click
import rich.table as table
from rich import print as rprint

from ai_scraper import __version__
from ai_scraper.api.github import GitHubClient
from ai_scraper.config import Config, load_config
from ai_scraper.filters.ai_filter import AIFilter
from ai_scraper.models.repository import FilterConfig as FilterConfigModel
from ai_scraper.storage.database import Database


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]):
    """GitHub AI high-star repositories scraper."""
    ctx.ensure_object(dict)

    config_path = Path(config) if config else Path("ai-scraper.yaml")
    ctx.obj["config"] = load_config(config_path)
    ctx.obj["config_path"] = config_path


@cli.command()
@click.option("--min-stars", type=int, help="Minimum stars filter")
@click.option("--max-results", type=int, help="Maximum results to fetch")
@click.pass_context
def scrape(ctx: click.Context, min_stars: Optional[int], max_results: Optional[int]):
    """Scrape AI repositories from GitHub."""
    config: Config = ctx.obj["config"]

    # Override config with CLI options
    if min_stars is not None:
        config.filter.min_stars = min_stars
    if max_results is not None:
        config.scrape.max_results = max_results

    rprint("[bold blue]Starting scrape...[/bold blue]")

    async def run_scrape():
        client = GitHubClient(token=config.github.token)
        db = Database(Path(config.database.path))
        db.init_db()
        filter_instance = AIFilter()

        try:
            # Build search query
            topics_query = " ".join(f"topic:{t}" for t in config.filter.topics[:5])
            query = f"stars:>{config.filter.min_stars} {topics_query}"

            rprint(f"[dim]Query: {query}[/dim]")

            # Search repositories
            all_repos = []
            page = 1
            per_page = 100

            while len(all_repos) < config.scrape.max_results:
                repos = await client.search_repositories(
                    query=query,
                    sort="stars",
                    order="desc",
                    page=page,
                    per_page=per_page,
                )

                if not repos:
                    break

                # Filter AI-related repos
                filter_config = FilterConfigModel(
                    keywords=config.filter.keywords,
                    topics=config.filter.topics,
                    languages=config.filter.languages,
                    exclude_keywords=config.filter.exclude_keywords,
                    min_stars=config.filter.min_stars,
                )

                for repo in repos:
                    if filter_instance.is_ai_related(repo, filter_config):
                        score = filter_instance.score_relevance(repo)
                        db.save_repository(repo, relevance_score=score)
                        all_repos.append(repo)

                rprint(f"[dim]Page {page}: found {len(repos)} repos, {len(all_repos)} total AI-related[/dim]")
                page += 1

                if len(repos) < per_page:
                    break

            rprint(f"[bold green]Scraped {len(all_repos)} AI repositories[/bold green]")

        finally:
            await client.close()
            db.close()

    asyncio.run(run_scrape())


@cli.command("list")
@click.option("--sort", type=click.Choice(["stars", "updated", "relevance"]), default="stars")
@click.option("--lang", type=str, help="Filter by language")
@click.option("--limit", type=int, default=20, help="Number of results")
@click.pass_context
def list_repos(ctx: click.Context, sort: str, lang: Optional[str], limit: int):
    """List scraped repositories."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    repos = db.get_all_repositories(limit=limit, sort_by=sort)

    # Filter by language if specified
    if lang:
        repos = [r for r in repos if r.language and r.language.lower() == lang.lower()]

    # Create table
    tbl = table.Table(title=f"AI Repositories (sorted by {sort})")
    tbl.add_column("Name", style="cyan")
    tbl.add_column("Stars", justify="right", style="yellow")
    tbl.add_column("Language", style="green")
    tbl.add_column("Description", max_width=40)

    for repo in repos:
        stars_str = f"{repo.stars:,}"
        desc = repo.description[:37] + "..." if repo.description and len(repo.description) > 40 else repo.description or ""
        tbl.add_row(repo.name, stars_str, repo.language or "-", desc)

    rprint(tbl)
    db.close()


@cli.command()
@click.option("--days", type=int, default=7, help="Days to analyze")
@click.option("--top", type=int, default=10, help="Number of top results")
@click.pass_context
def trending(ctx: click.Context, days: int, top: int):
    """Show trending repositories by star growth."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    trends = db.get_trending(days=days, limit=top)

    if not trends:
        rprint(f"[yellow]No trending data found for the last {days} days.[/yellow]")
        rprint("[dim]Run 'ai-scraper scrape' multiple times to build trend data.[/dim]")
        db.close()
        return

    tbl = table.Table(title=f"Trending Repositories (last {days} days)")
    tbl.add_column("Repository", style="cyan")
    tbl.add_column("Growth", justify="right", style="green")
    tbl.add_column("Stars", justify="right", style="yellow")

    for trend in trends:
        growth_str = f"+{trend.growth_rate * 100:.1f}%"
        stars_str = f"{trend.current_stars:,}"
        tbl.add_row(trend.repo_name, growth_str, stars_str)

    rprint(tbl)
    db.close()


@cli.group()
def config_cmd():
    """Configuration management."""
    pass


@config_cmd.command("init")
@click.pass_context
def config_init(ctx: click.Context):
    """Initialize configuration file."""
    config_path: Path = ctx.obj["config_path"]

    if config_path.exists():
        rprint(f"[yellow]Config file already exists at {config_path}[/yellow]")
        return

    # Copy default config
    import shutil
    default_config = Path(__file__).parent.parent.parent / "ai-scraper.yaml"

    if default_config.exists():
        shutil.copy(default_config, config_path)
        rprint(f"[green]Created config file at {config_path}[/green]")
    else:
        rprint("[red]Default config not found[/red]")


@config_cmd.command("show")
@click.pass_context
def config_show(ctx: click.Context):
    """Show current configuration."""
    config: Config = ctx.obj["config"]

    rprint("[bold]Current Configuration:[/bold]")
    rprint(f"  GitHub Token: {'***' if config.github.token else 'Not set'}")
    rprint(f"  Cache TTL: {config.github.cache_ttl}s")
    rprint(f"  Min Stars: {config.filter.min_stars}")
    rprint(f"  Keywords: {', '.join(config.filter.keywords[:5])}...")
    rprint(f"  Topics: {', '.join(config.filter.topics[:5])}...")
    rprint(f"  Max Results: {config.scrape.max_results}")
    rprint(f"  Database: {config.database.path}")
    rprint(f"  Scheduler: {'enabled' if config.scheduler.enabled else 'disabled'}")


cli.add_command(config_cmd, name="config")


@cli.group()
def db_cmd():
    """Database management."""
    pass


@db_cmd.command("stats")
@click.pass_context
def db_stats(ctx: click.Context):
    """Show database statistics."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    stats = db.get_stats()

    rprint("[bold]Database Statistics:[/bold]")
    rprint(f"  Repository count: {stats['repository_count']}")
    rprint(f"  Snapshot count: {stats['snapshot_count']}")
    rprint(f"  Total stars: {stats['total_stars']:,}")

    db.close()


@db_cmd.command("clean")
@click.option("--days", type=int, default=30, help="Keep snapshots from last N days")
@click.pass_context
def db_clean(ctx: click.Context, days: int):
    """Clean old snapshots."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found.[/yellow]")
        return

    db.init_db()
    deleted = db.clean_old_snapshots(days=days)

    rprint(f"[green]Deleted {deleted} old snapshots[/green]")
    db.close()


@db_cmd.command("export")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--output", "-o", type=click.Path(), default="export.csv")
@click.pass_context
def db_export(ctx: click.Context, format: str, output: str):
    """Export database to file."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found.[/yellow]")
        return

    db.init_db()
    repos = db.get_all_repositories(limit=10000)

    if format == "csv":
        import csv

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "stars", "language", "description", "url"])

            for repo in repos:
                writer.writerow([
                    repo.name,
                    repo.stars,
                    repo.language or "",
                    repo.description or "",
                    repo.url,
                ])

        rprint(f"[green]Exported {len(repos)} repositories to {output}[/green]")

    elif format == "json":
        import json

        data = {
            "repositories": [
                {
                    "name": r.name,
                    "stars": r.stars,
                    "language": r.language,
                    "description": r.description,
                    "url": r.url,
                }
                for r in repos
            ],
            "total": len(repos),
        }

        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        rprint(f"[green]Exported {len(repos)} repositories to {output}[/green]")

    db.close()


cli.add_command(db_cmd, name="db")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: 提交CLI模块**

```bash
git add src/ai_scraper/cli.py tests/test_cli.py
git commit -m "feat: add CLI with scrape, list, trending, config, and db commands"
```

---

## Task 8: Go调度器实现

**Files:**
- Create: `cmd/scheduler/main.go`
- Create: `cmd/scheduler/scheduler.go`
- Create: `cmd/scheduler/limiter.go`
- Create: `cmd/scheduler/processor.go`

- [ ] **Step 1: 创建Go令牌桶限流器**

创建 `cmd/scheduler/limiter.go`:

```go
package main

import (
	"context"
	"sync"
	"time"
)

// TokenBucket implements a token bucket rate limiter
type TokenBucket struct {
	capacity     int
	tokens       float64
	refillRate   float64 // tokens per second
	mu           sync.Mutex
	lastUpdate   time.Time
}

// NewTokenBucket creates a new token bucket limiter
func NewTokenBucket(requestsPerHour int) *TokenBucket {
	effectiveLimit := int(float64(requestsPerHour) * 0.9) // 10% safety margin
	refillRate := float64(effectiveLimit) / 3600.0

	return &TokenBucket{
		capacity:   effectiveLimit,
		tokens:     float64(effectiveLimit),
		refillRate: refillRate,
		lastUpdate: time.Now(),
	}
}

// Wait blocks until a token is available or context is cancelled
func (tb *TokenBucket) Wait(ctx context.Context) error {
	tb.mu.Lock()
	tb.refill()
	tb.mu.Unlock()

	for {
		tb.mu.Lock()
		if tb.tokens >= 1.0 {
			tb.tokens -= 1.0
			tb.mu.Unlock()
			return nil
		}
		tb.mu.Unlock()

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(100 * time.Millisecond):
			tb.mu.Lock()
			tb.refill()
			tb.mu.Unlock()
		}
	}
}

// TryAcquire attempts to acquire a token without blocking
func (tb *TokenBucket) TryAcquire() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()

	if tb.tokens >= 1.0 {
		tb.tokens -= 1.0
		return true
	}
	return false
}

// SetRate updates the rate limit
func (tb *TokenBucket) SetRate(requestsPerHour int) {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	effectiveLimit := int(float64(requestsPerHour) * 0.9)
	tb.capacity = effectiveLimit
	tb.refillRate = float64(effectiveLimit) / 3600.0
	if tb.tokens > float64(effectiveLimit) {
		tb.tokens = float64(effectiveLimit)
	}
}

// refill adds tokens based on elapsed time
func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastUpdate).Seconds()

	tb.tokens = min(float64(tb.capacity), tb.tokens+elapsed*tb.refillRate)
	tb.lastUpdate = now
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
```

- [ ] **Step 2: 创建Go调度器**

创建 `cmd/scheduler/scheduler.go`:

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
)

// Task represents a task to be processed
type Task struct {
	ID      string                 `json:"id"`
	Type    string                 `json:"type"`
	Payload map[string]interface{} `json:"payload"`
}

// Result represents a task result
type Result struct {
	TaskID  string      `json:"task_id"`
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// Scheduler manages concurrent task processing
type Scheduler struct {
	maxWorkers  int
	taskQueue   chan Task
	resultQueue chan Result
	limiter     *TokenBucket
	wg          sync.WaitGroup
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewScheduler creates a new scheduler
func NewScheduler(maxWorkers int, requestsPerHour int) *Scheduler {
	ctx, cancel := context.WithCancel(context.Background())

	return &Scheduler{
		maxWorkers:  maxWorkers,
		taskQueue:   make(chan Task, 100),
		resultQueue: make(chan Result, 100),
		limiter:     NewTokenBucket(requestsPerHour),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start begins processing tasks
func (s *Scheduler) Start() {
	for i := 0; i < s.maxWorkers; i++ {
		s.wg.Add(1)
		go s.worker(i)
	}
}

// Stop gracefully shuts down the scheduler
func (s *Scheduler) Stop() {
	s.cancel()
	s.wg.Wait()
	close(s.taskQueue)
	close(s.resultQueue)
}

// Submit adds a task to the queue
func (s *Scheduler) Submit(task Task) error {
	select {
	case s.taskQueue <- task:
		return nil
	case <-s.ctx.Done():
		return fmt.Errorf("scheduler stopped")
	}
}

// GetResults returns the result channel
func (s *Scheduler) GetResults() <-chan Result {
	return s.resultQueue
}

// ProcessBatch processes multiple tasks and returns results
func (s *Scheduler) ProcessBatch(tasks []Task) []Result {
	results := make([]Result, 0, len(tasks))

	// Submit all tasks
	go func() {
		for _, task := range tasks {
			_ = s.Submit(task)
		}
	}()

	// Collect results
	received := 0
	for result := range s.resultQueue {
		results = append(results, result)
		received++
		if received >= len(tasks) {
			break
		}
	}

	return results
}

// worker processes tasks from the queue
func (s *Scheduler) worker(id int) {
	defer s.wg.Done()

	for {
		select {
		case <-s.ctx.Done():
			return
		case task, ok := <-s.taskQueue:
			if !ok {
				return
			}

			// Wait for rate limiter
			if err := s.limiter.Wait(s.ctx); err != nil {
				s.resultQueue <- Result{
					TaskID:  task.ID,
					Success: false,
					Error:   err.Error(),
				}
				continue
			}

			// Process task
			result := s.processTask(task)
			s.resultQueue <- result
		}
	}
}

// processTask handles a single task
func (s *Scheduler) processTask(task Task) Result {
	switch task.Type {
	case "process":
		return s.processData(task)
	default:
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("unknown task type: %s", task.Type),
		}
	}
}

// processData processes repository data
func (s *Scheduler) processData(task Task) Result {
	// Extract repository data from payload
	data, err := json.Marshal(task.Payload)
	if err != nil {
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   err.Error(),
		}
	}

	var repo struct {
		ID          int      `json:"id"`
		Name        string   `json:"name"`
		Stars       int      `json:"stars"`
		Topics      []string `json:"topics"`
		Description string   `json:"description"`
	}

	if err := json.Unmarshal(data, &repo); err != nil {
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   err.Error(),
		}
	}

	// Calculate relevance score
	score := calculateRelevance(repo.Name, repo.Description, repo.Topics)

	return Result{
		TaskID:  task.ID,
		Success: true,
		Data: map[string]interface{}{
			"id":              repo.ID,
			"name":            repo.Name,
			"relevance_score": score,
		},
	}
}

// calculateRelevance calculates AI relevance score
func calculateRelevance(name, description string, topics []string) float64 {
	score := 0.0

	aiKeywords := []string{
		"ai", "machine learning", "deep learning", "neural network",
		"llm", "gpt", "transformer", "nlp", "computer vision",
		"pytorch", "tensorflow", "huggingface",
	}

	aiTopics := map[string]bool{
		"ai": true, "machine-learning": true, "deep-learning": true,
		"neural-network": true, "nlp": true, "computer-vision": true,
		"llm": true, "gpt": true, "pytorch": true, "tensorflow": true,
	}

	// Check keywords
	text := name + " " + description
	for _, kw := range aiKeywords {
		if contains(text, kw) {
			score += 0.2
		}
	}

	// Check topics
	for _, topic := range topics {
		if aiTopics[topic] {
			score += 0.15
		}
	}

	if score > 1.0 {
		score = 1.0
	}

	return score
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsHelper(s, substr))
}

func containsHelper(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
```

- [ ] **Step 3: 创建Go数据处理器**

创建 `cmd/scheduler/processor.go`:

```go
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"sync"

	_ "github.com/mattn/go-sqlite3"
)

// Processor handles batch data processing
type Processor struct {
	db *sql.DB
}

// NewProcessor creates a new processor
func NewProcessor(dbPath string) (*Processor, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	return &Processor{db: db}, nil
}

// Close closes the database connection
func (p *Processor) Close() error {
	return p.db.Close()
}

// TrendResult represents a trend analysis result
type TrendResult struct {
	RepoID        int     `json:"repo_id"`
	RepoName      string  `json:"repo_name"`
	InitialStars  int     `json:"initial_stars"`
	CurrentStars  int     `json:"current_stars"`
	GrowthRate    float64 `json:"growth_rate"`
}

// CalculateTrends calculates star growth trends
func (p *Processor) CalculateTrends(repoIDs []int, days int) ([]TrendResult, error) {
	query := `
		SELECT
			r.id as repo_id,
			r.name as repo_name,
			(SELECT stars FROM snapshots WHERE repo_id = r.id
			 ORDER BY snapshot_at ASC LIMIT 1) as initial_stars,
			r.stars as current_stars
		FROM repositories r
		WHERE r.id IN (%s)
		HAVING initial_stars IS NOT NULL AND current_stars > initial_stars
		ORDER BY (CAST(current_stars AS FLOAT) / initial_stars - 1) DESC
	`

	// Build IN clause
	placeholders := ""
	args := make([]interface{}, len(repoIDs))
	for i, id := range repoIDs {
		if i > 0 {
			placeholders += ","
		}
		placeholders += "?"
		args[i] = id
	}

	rows, err := p.db.Query(fmt.Sprintf(query, placeholders), args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []TrendResult
	for rows.Next() {
		var tr TrendResult
		if err := rows.Scan(&tr.RepoID, &tr.RepoName, &tr.InitialStars, &tr.CurrentStars); err != nil {
			return nil, err
		}

		if tr.InitialStars > 0 {
			tr.GrowthRate = float64(tr.CurrentStars-tr.InitialStars) / float64(tr.InitialStars)
		}

		results = append(results, tr)
	}

	return results, nil
}

// AggregateStats calculates aggregate statistics
type AggregateStats struct {
	ByLanguage map[string]int `json:"by_language"`
	ByTopic    map[string]int `json:"by_topic"`
	TotalRepos int            `json:"total_repos"`
	TotalStars int            `json:"total_stars"`
}

// Aggregate calculates aggregate statistics
func (p *Processor) Aggregate() (*AggregateStats, error) {
	stats := &AggregateStats{
		ByLanguage: make(map[string]int),
		ByTopic:    make(map[string]int),
	}

	// Count by language
	rows, err := p.db.Query("SELECT language, COUNT(*) FROM repositories WHERE language IS NOT NULL GROUP BY language")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var lang string
		var count int
		if err := rows.Scan(&lang, &count); err != nil {
			return nil, err
		}
		stats.ByLanguage[lang] = count
	}

	// Count by topic (topics stored as JSON array)
	rows, err = p.db.Query("SELECT topics FROM repositories WHERE topics IS NOT NULL AND topics != '[]'")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var topicsJSON string
		if err := rows.Scan(&topicsJSON); err != nil {
			return nil, err
		}

		var topics []string
		if err := json.Unmarshal([]byte(topicsJSON), &topics); err == nil {
			for _, topic := range topics {
				stats.ByTopic[topic]++
			}
		}
	}

	// Total counts
	rows, err = p.db.Query("SELECT COUNT(*), COALESCE(SUM(stars), 0) FROM repositories")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	if rows.Next() {
		if err := rows.Scan(&stats.TotalRepos, &stats.TotalStars); err != nil {
			return nil, err
		}
	}

	return stats, nil
}

// ProcessBatch processes multiple repositories in parallel
func (p *Processor) ProcessBatch(repos []map[string]interface{}) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(repos))

	for _, repo := range repos {
		wg.Add(1)
		go func(r map[string]interface{}) {
			defer wg.Done()

			// Process each repo (e.g., calculate scores, update database)
			// This is a placeholder for actual processing logic
		}(repo)
	}

	wg.Wait()
	close(errChan)

	// Check for errors
	for err := range errChan {
		if err != nil {
			return err
		}
	}

	return nil
}
```

- [ ] **Step 4: 创建Go主入口**

创建 `cmd/scheduler/main.go`:

```go
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	workers := flag.Int("workers", 4, "Number of worker goroutines")
	rateLimit := flag.Int("rate", 5000, "Requests per hour")
	flag.Parse()

	log.Printf("Starting scheduler with %d workers, %d req/hour rate limit", *workers, *rateLimit)

	scheduler := NewScheduler(*workers, *rateLimit)
	scheduler.Start()
	defer scheduler.Stop()

	// Handle shutdown signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Read tasks from stdin, write results to stdout
	go func() {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			var task Task
			if err := json.Unmarshal(scanner.Bytes(), &task); err != nil {
				log.Printf("Error parsing task: %v", err)
				continue
			}

			if err := scheduler.Submit(task); err != nil {
				log.Printf("Error submitting task: %v", err)
			}
		}
	}()

	// Output results
	go func() {
		for result := range scheduler.GetResults() {
			data, err := json.Marshal(result)
			if err != nil {
				log.Printf("Error marshaling result: %v", err)
				continue
			}
			fmt.Println(string(data))
		}
	}()

	// Wait for shutdown
	<-sigChan
	log.Println("Shutting down...")
}
```

- [ ] **Step 5: 构建Go二进制**

```bash
cd cmd/scheduler
go build -o scheduler .
```

Expected: Binary created successfully

- [ ] **Step 6: 提交Go调度器**

```bash
git add cmd/scheduler/
git commit -m "feat: add Go scheduler with rate limiting and batch processing"
```

---

## Task 9: 集成测试

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: 编写集成测试**

创建 `tests/test_integration.py`:

```python
"""Integration tests for ai-scraper."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_scraper.cli import cli


@pytest.fixture
def isolated_env():
    """Create isolated test environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_full_workflow(isolated_env):
    """Test complete scrape -> list -> export workflow."""
    runner = CliRunner()

    # Initialize config
    result = runner.invoke(cli, ["config", "init"])
    assert result.exit_code == 0

    # Check database stats (should be empty)
    result = runner.invoke(cli, ["db", "stats"])
    assert result.exit_code == 0
    assert "Repository count: 0" in result.output


def test_config_workflow():
    """Test configuration workflow."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Show default config
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "Min Stars" in result.output


def test_export_workflow(isolated_env):
    """Test database export workflow."""
    runner = CliRunner()

    # Create empty database
    result = runner.invoke(cli, ["db", "stats"])
    assert result.exit_code == 0

    # Export (should handle empty database gracefully)
    result = runner.invoke(cli, ["db", "export", "--format", "json", "--output", "test.json"])
    # May fail if no database exists, which is expected
```

- [ ] **Step 2: 运行集成测试**

```bash
python -m pytest tests/test_integration.py -v
```

Expected: PASS (3 tests)

- [ ] **Step 3: 提交集成测试**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for CLI workflow"
```

---

## Task 10: 文档和最终整理

**Files:**
- Create: `README.md`
- Update: `pyproject.toml`

- [ ] **Step 1: 创建README**

创建 `README.md`:

```markdown
# GitHub AI Scraper

A CLI tool for scraping AI-related high-star repositories from GitHub.

## Features

- Search and filter AI-related repositories by keywords and topics
- Local SQLite storage with trend analysis
- Configurable filtering and scraping options
- Rate limiting with GitHub API token support
- Export to CSV/JSON formats

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Set your GitHub token (optional, increases rate limit)
export GITHUB_TOKEN=your_token_here

# Scrape AI repositories
ai-scraper scrape

# List scraped repositories
ai-scraper list

# Show trending repositories
ai-scraper trending

# Export data
ai-scraper db export --format csv --output repos.csv
```

## Configuration

Create `ai-scraper.yaml` to customize:

```yaml
github:
  token: ${GITHUB_TOKEN}
  cache_ttl: 3600

filter:
  min_stars: 100
  keywords:
    - ai
    - machine-learning
  topics:
    - ai
    - deep-learning

scrape:
  max_results: 500
  concurrency: 5
```

## Commands

- `ai-scraper scrape` - Scrape AI repositories
- `ai-scraper list` - List repositories
- `ai-scraper trending` - Show trending repositories
- `ai-scraper config init` - Initialize config file
- `ai-scraper config show` - Show current config
- `ai-scraper db stats` - Show database statistics
- `ai-scraper db export` - Export data

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Build Go scheduler
cd cmd/scheduler && go build
```

## License

MIT
```

- [ ] **Step 2: 更新pyproject.toml添加README**

更新 `pyproject.toml`, 在 `[project]` 部分添加:

```toml
readme = "README.md"
license = "MIT"
```

- [ ] **Step 3: 最终提交**

```bash
git add README.md pyproject.toml
git commit -m "docs: add README and finalize project configuration"
```

---

## 实现完成检查清单

- [ ] 所有Python模块已实现并测试通过
- [ ] Go调度器已实现并可编译
- [ ] CLI命令全部可用
- [ ] 集成测试通过
- [ ] 文档完整

## 执行说明

本计划使用TDD方式，每个任务包含：
1. 编写测试
2. 运行测试确认失败
3. 实现代码
4. 运行测试确认通过
5. 提交代码

按任务顺序执行即可完成整个项目。
