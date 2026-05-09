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
