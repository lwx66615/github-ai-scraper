"""Tests for enhanced deduplication."""

import pytest
from datetime import datetime
from ai_scraper.dedup import DeduplicationChecker
from ai_scraper.models.repository import Repository


def test_detect_fork_repository():
    """Test detection of fork repositories."""
    checker = DeduplicationChecker()

    repo = Repository(
        id=1,
        name="fork/original-repo",
        full_name="fork/original-repo",
        description="Forked repository",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/fork/original-repo",
    )

    # Simulate fork detection
    info = checker.check(repo, is_fork=True)
    assert info.is_fork is True
    assert info.duplicate_type == "fork"


def test_detect_mirror_repository():
    """Test detection of mirror repositories."""
    checker = DeduplicationChecker()

    repo = Repository(
        id=1,
        name="user/repo-mirror",
        full_name="user/repo-mirror",
        description="Mirror repository",
        stars=50,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/user/repo-mirror",
    )

    info = checker.check(repo)
    assert info.is_mirror is True
    assert info.duplicate_type == "mirror"


def test_detect_content_similarity():
    """Test detection of content-similar repositories."""
    checker = DeduplicationChecker()

    repos = [
        Repository(
            id=1,
            name="user1/awesome-ai",
            full_name="user1/awesome-ai",
            description="A curated list of AI resources and tools",
            stars=1000,
            language="Python",
            topics=["ai", "awesome-list"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/user1/awesome-ai",
        ),
        Repository(
            id=2,
            name="user2/awesome-ai-list",
            full_name="user2/awesome-ai-list",
            description="A curated list of AI resources and tools",
            stars=500,
            language="Python",
            topics=["ai", "awesome-list"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/user2/awesome-ai-list",
        ),
    ]

    similar = checker.find_similar_content(repos, threshold=0.5)
    assert len(similar) > 0


def test_no_similarity_different_content():
    """Test that different content is not marked as similar."""
    checker = DeduplicationChecker()

    repos = [
        Repository(
            id=1,
            name="user/ai-tool",
            full_name="user/ai-tool",
            description="Machine learning framework for deep learning",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/user/ai-tool",
        ),
        Repository(
            id=2,
            name="user/web-app",
            full_name="user/web-app",
            description="A simple web application framework",
            stars=50,
            language="JavaScript",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/user/web-app",
        ),
    ]

    similar = checker.find_similar_content(repos, threshold=0.8)
    assert len(similar) == 0


def test_extract_original_name():
    """Test extracting original name from mirror."""
    checker = DeduplicationChecker()

    original = checker._extract_original_name("repo-mirror")
    assert original == "repo"

    original = checker._extract_original_name("project.mirror")
    assert original == "project"


def test_normal_repository():
    """Test that normal repositories are not marked as duplicates."""
    checker = DeduplicationChecker()

    repo = Repository(
        id=1,
        name="user/normal-repo",
        full_name="user/normal-repo",
        description="Normal repository",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/user/normal-repo",
    )

    info = checker.check(repo)
    assert info.duplicate_type == "none"
    assert not info.is_fork
    assert not info.is_mirror
