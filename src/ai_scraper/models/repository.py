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
