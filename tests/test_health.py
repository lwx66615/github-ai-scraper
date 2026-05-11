"""Tests for repository health assessment."""

import pytest
from datetime import datetime, timedelta
from ai_scraper.health import HealthAssessor, HealthScore
from ai_scraper.models.repository import Repository


def test_health_score_calculation():
    """Test health score calculation."""
    assessor = HealthAssessor()

    repo = Repository(
        id=1,
        name="test/healthy-repo",
        full_name="test/healthy-repo",
        description="A healthy repository",
        stars=5000,
        language="Python",
        topics=["ai"],
        created_at=datetime.now() - timedelta(days=365),
        updated_at=datetime.now() - timedelta(days=1),
        pushed_at=datetime.now() - timedelta(days=1),
        url="https://github.com/test/healthy-repo",
        open_issues=10,
        forks=200,
    )

    score = assessor.assess(repo)

    assert 0 <= score.overall <= 100
    assert score.activity > 0
    assert score.popularity > 0
    assert score.maintenance > 0
    assert score.community > 0


def test_inactive_repo_low_score():
    """Test that inactive repos get low scores."""
    assessor = HealthAssessor()

    repo = Repository(
        id=1,
        name="test/inactive-repo",
        full_name="test/inactive-repo",
        description="An inactive repository",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now() - timedelta(days=365),
        updated_at=datetime.now() - timedelta(days=180),
        pushed_at=datetime.now() - timedelta(days=180),
        url="https://github.com/test/inactive-repo",
        open_issues=50,
        forks=5,
    )

    score = assessor.assess(repo)

    assert score.activity < 30
    assert score.overall < 50


def test_health_grade():
    """Test health grade assignment."""
    assessor = HealthAssessor()

    # High score should get A
    grade = assessor.get_grade(90)
    assert grade == "A"

    # Medium score should get C
    grade = assessor.get_grade(70)
    assert grade == "C"

    # Low score should get F
    grade = assessor.get_grade(20)
    assert grade == "F"


def test_activity_score():
    """Test activity score based on last push."""
    assessor = HealthAssessor()

    # Recent push
    repo = Repository(
        id=1,
        name="test/repo",
        full_name="test/repo",
        description="Test",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now() - timedelta(days=5),
        url="https://github.com/test/repo",
    )
    score = assessor.assess(repo)
    assert score.activity == 100

    # Old push
    repo = Repository(
        id=2,
        name="test/repo2",
        full_name="test/repo2",
        description="Test",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now() - timedelta(days=400),
        url="https://github.com/test/repo2",
    )
    score = assessor.assess(repo)
    assert score.activity == 0


def test_popularity_score():
    """Test popularity score based on stars."""
    assessor = HealthAssessor()

    # High stars
    repo = Repository(
        id=1,
        name="test/popular",
        full_name="test/popular",
        description="Test",
        stars=15000,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/popular",
    )
    score = assessor.assess(repo)
    assert score.popularity == 100

    # Low stars
    repo = Repository(
        id=2,
        name="test/unpopular",
        full_name="test/unpopular",
        description="Test",
        stars=10,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/unpopular",
    )
    score = assessor.assess(repo)
    assert score.popularity == 10


def test_community_score():
    """Test community score based on forks."""
    assessor = HealthAssessor()

    # Many forks
    repo = Repository(
        id=1,
        name="test/community",
        full_name="test/community",
        description="Test",
        stars=1000,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/community",
        forks=1500,
    )
    score = assessor.assess(repo)
    assert score.community == 100

    # Few forks
    repo = Repository(
        id=2,
        name="test/solo",
        full_name="test/solo",
        description="Test",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/solo",
        forks=2,
    )
    score = assessor.assess(repo)
    assert score.community == 10
