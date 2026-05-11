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
class KeywordsConfig:
    """Keywords configuration."""

    file: str = "./keywords.txt"
    max_keywords: int = 100


@dataclass
class OutputConfig:
    """Output configuration."""

    dir: str = "./output"
    filename: str = "repositories.md"


@dataclass
class WebhookEndpointConfig:
    """Webhook endpoint configuration."""

    url: str = ""
    events: list[str] = field(default_factory=list)


@dataclass
class WebhooksConfig:
    """Webhooks configuration."""

    enabled: bool = False
    endpoints: list[WebhookEndpointConfig] = field(default_factory=list)


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
    webhooks: WebhooksConfig = field(default_factory=WebhooksConfig)


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

    keywords_dict = processed_config.get("keywords", {})
    keywords_config = KeywordsConfig(
        file=keywords_dict.get("file", "./keywords.txt"),
        max_keywords=keywords_dict.get("max_keywords", 100),
    )

    output_dict = processed_config.get("output", {})
    output_config = OutputConfig(
        dir=output_dict.get("dir", "./output"),
        filename=output_dict.get("filename", "repositories.md"),
    )

    webhooks_dict = processed_config.get("webhooks", {})
    endpoints_list = webhooks_dict.get("endpoints", [])
    endpoints = [
        WebhookEndpointConfig(
            url=endpoint.get("url", ""),
            events=endpoint.get("events", []),
        )
        for endpoint in endpoints_list
    ]
    webhooks_config = WebhooksConfig(
        enabled=webhooks_dict.get("enabled", False),
        endpoints=endpoints,
    )

    return Config(
        github=github,
        filter=filter_config,
        scrape=scrape_config,
        database=database_config,
        scheduler=scheduler_config,
        keywords=keywords_config,
        output=output_config,
        webhooks=webhooks_config,
    )