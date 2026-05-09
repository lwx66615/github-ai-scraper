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
