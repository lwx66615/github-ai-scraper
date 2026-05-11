"""Repository data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Repository(BaseModel):
    """GitHub repository information."""

    id: int = Field(gt=0, description="GitHub repository ID")
    name: str = Field(min_length=1, max_length=200)
    full_name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    stars: int = Field(ge=0, description="Star count")
    language: Optional[str] = Field(None, max_length=50)
    topics: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    url: str = Field(pattern=r"^https://github\.com/")
    open_issues: Optional[int] = Field(None, ge=0)
    forks: Optional[int] = Field(None, ge=0)
    contributors: Optional[int] = Field(None, ge=0)

    @field_validator("name", "full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name fields."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, v: list[str]) -> list[str]:
        """Clean and lowercase topics."""
        return [t.strip().lower() for t in v if t.strip()]


class RepoSnapshot(BaseModel):
    """Repository snapshot for trend analysis."""

    repo_id: int = Field(gt=0)
    stars: int = Field(ge=0)
    snapshot_at: datetime


class FilterConfig(BaseModel):
    """Filter configuration for scraping."""

    keywords: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    min_stars: int = Field(default=100, ge=0)

    @field_validator("keywords", "topics", "languages", "exclude_keywords")
    @classmethod
    def clean_string_list(cls, v: list[str]) -> list[str]:
        """Clean string lists by stripping whitespace and removing empty strings."""
        return [s.strip() for s in v if s.strip()]


class ScrapeConfig(BaseModel):
    """Scrape configuration."""

    data_fields: list[str] = Field(default_factory=list)
    max_results: int = Field(default=100, gt=0)
    concurrency: int = Field(default=5, gt=0, le=100)
    cache_ttl: int = Field(default=3600, ge=0)