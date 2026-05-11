"""Tests for Pydantic data validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from ai_scraper.models.repository import Repository, RepoSnapshot, FilterConfig, ScrapeConfig


class TestRepositoryValidation:
    """Tests for Repository model validation."""

    def test_valid_repository_passes_validation(self):
        """Test that a valid repository passes validation."""
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

    def test_negative_id_raises_error(self):
        """Test that negative id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Repository(
                id=-1,
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
        assert "gt=0" in str(exc_info.value) or "greater than 0" in str(exc_info.value)

    def test_zero_id_raises_error(self):
        """Test that zero id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Repository(
                id=0,
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
        assert "gt=0" in str(exc_info.value) or "greater than 0" in str(exc_info.value)

    def test_empty_name_raises_error(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
                id=12345,
                name="",
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

    def test_whitespace_only_name_raises_error(self):
        """Test that whitespace-only name raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
                id=12345,
                name="   ",
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

    def test_name_max_length(self):
        """Test that name exceeding max length raises error."""
        long_name = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            Repository(
                id=12345,
                name=long_name,
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
        assert "max_length" in str(exc_info.value) or "at most 200" in str(exc_info.value)

    def test_negative_stars_raises_error(self):
        """Test that negative stars raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Repository(
                id=12345,
                name="test/repo",
                full_name="test/repo",
                description="A test repository",
                stars=-1,
                language="Python",
                topics=["ai"],
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 5, 1),
                pushed_at=datetime(2024, 5, 9),
                url="https://github.com/test/repo",
            )
        assert "ge=0" in str(exc_info.value) or "greater than or equal to 0" in str(exc_info.value)

    def test_zero_stars_is_valid(self):
        """Test that zero stars is valid."""
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description="A test repository",
            stars=0,
            language="Python",
            topics=["ai"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )
        assert repo.stars == 0

    def test_invalid_url_pattern_raises_error(self):
        """Test that invalid URL pattern raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Repository(
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
                url="https://gitlab.com/test/repo",
            )
        assert "pattern" in str(exc_info.value) or "string should match" in str(exc_info.value).lower()

    def test_http_url_raises_error(self):
        """Test that non-https URL raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
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
                url="http://github.com/test/repo",
            )

    def test_topics_are_cleaned_and_lowercased(self):
        """Test that topics are stripped and lowercased."""
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description="A test repository",
            stars=1000,
            language="Python",
            topics=["  AI  ", "Machine-Learning", "  PYTHON  "],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )
        assert repo.topics == ["ai", "machine-learning", "python"]

    def test_empty_topics_are_removed(self):
        """Test that empty topics are removed."""
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description="A test repository",
            stars=1000,
            language="Python",
            topics=["ai", "", "  ", "ml"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )
        assert repo.topics == ["ai", "ml"]

    def test_description_max_length(self):
        """Test that description exceeding max length raises error."""
        long_desc = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            Repository(
                id=12345,
                name="test/repo",
                full_name="test/repo",
                description=long_desc,
                stars=1000,
                language="Python",
                topics=["ai"],
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 5, 1),
                pushed_at=datetime(2024, 5, 9),
                url="https://github.com/test/repo",
            )
        assert "max_length" in str(exc_info.value) or "at most 1000" in str(exc_info.value)

    def test_description_at_max_length(self):
        """Test that description at max length is valid."""
        max_desc = "a" * 1000
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="test/repo",
            description=max_desc,
            stars=1000,
            language="Python",
            topics=["ai"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )
        assert len(repo.description) == 1000

    def test_negative_open_issues_raises_error(self):
        """Test that negative open_issues raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
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
                open_issues=-1,
            )

    def test_negative_forks_raises_error(self):
        """Test that negative forks raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
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
                forks=-5,
            )

    def test_negative_contributors_raises_error(self):
        """Test that negative contributors raises validation error."""
        with pytest.raises(ValidationError):
            Repository(
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
                contributors=-1,
            )

    def test_name_is_stripped(self):
        """Test that name is stripped of whitespace."""
        repo = Repository(
            id=12345,
            name="  test/repo  ",
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
        assert repo.name == "test/repo"

    def test_full_name_is_stripped(self):
        """Test that full_name is stripped of whitespace."""
        repo = Repository(
            id=12345,
            name="test/repo",
            full_name="  owner/repo  ",
            description="A test repository",
            stars=1000,
            language="Python",
            topics=["ai"],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 5, 1),
            pushed_at=datetime(2024, 5, 9),
            url="https://github.com/test/repo",
        )
        assert repo.full_name == "owner/repo"

    def test_language_max_length(self):
        """Test that language exceeding max length raises error."""
        with pytest.raises(ValidationError):
            Repository(
                id=12345,
                name="test/repo",
                full_name="test/repo",
                description="A test repository",
                stars=1000,
                language="a" * 51,
                topics=["ai"],
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 5, 1),
                pushed_at=datetime(2024, 5, 9),
                url="https://github.com/test/repo",
            )


class TestRepoSnapshotValidation:
    """Tests for RepoSnapshot model validation."""

    def test_valid_snapshot(self):
        """Test that a valid snapshot passes validation."""
        snapshot = RepoSnapshot(
            repo_id=12345,
            stars=1000,
            snapshot_at=datetime(2024, 5, 9, 10, 30),
        )
        assert snapshot.repo_id == 12345
        assert snapshot.stars == 1000

    def test_negative_repo_id_raises_error(self):
        """Test that negative repo_id raises validation error."""
        with pytest.raises(ValidationError):
            RepoSnapshot(
                repo_id=-1,
                stars=1000,
                snapshot_at=datetime(2024, 5, 9, 10, 30),
            )

    def test_negative_stars_raises_error(self):
        """Test that negative stars raises validation error."""
        with pytest.raises(ValidationError):
            RepoSnapshot(
                repo_id=12345,
                stars=-1,
                snapshot_at=datetime(2024, 5, 9, 10, 30),
            )


class TestFilterConfigValidation:
    """Tests for FilterConfig model validation."""

    def test_valid_filter_config(self):
        """Test that a valid filter config passes validation."""
        config = FilterConfig(
            keywords=["ai", "ml"],
            topics=["machine-learning"],
            languages=["python"],
            exclude_keywords=["deprecated"],
        )
        assert config.min_stars == 100
        assert "ai" in config.keywords

    def test_negative_min_stars_raises_error(self):
        """Test that negative min_stars raises validation error."""
        with pytest.raises(ValidationError):
            FilterConfig(
                keywords=["ai"],
                topics=[],
                languages=[],
                exclude_keywords=[],
                min_stars=-1,
            )

    def test_zero_min_stars_is_valid(self):
        """Test that zero min_stars is valid."""
        config = FilterConfig(
            keywords=["ai"],
            topics=[],
            languages=[],
            exclude_keywords=[],
            min_stars=0,
        )
        assert config.min_stars == 0

    def test_keywords_are_cleaned(self):
        """Test that keywords are stripped of whitespace."""
        config = FilterConfig(
            keywords=["  ai  ", "ml", "  "],
            topics=[],
            languages=[],
            exclude_keywords=[],
        )
        assert config.keywords == ["ai", "ml"]


class TestScrapeConfigValidation:
    """Tests for ScrapeConfig model validation."""

    def test_valid_scrape_config(self):
        """Test that a valid scrape config passes validation."""
        config = ScrapeConfig(
            data_fields=["stars", "language"],
            max_results=100,
            concurrency=5,
            cache_ttl=3600,
        )
        assert config.max_results == 100
        assert config.concurrency == 5

    def test_zero_max_results_raises_error(self):
        """Test that zero max_results raises validation error."""
        with pytest.raises(ValidationError):
            ScrapeConfig(
                data_fields=["stars"],
                max_results=0,
                concurrency=5,
                cache_ttl=3600,
            )

    def test_negative_max_results_raises_error(self):
        """Test that negative max_results raises validation error."""
        with pytest.raises(ValidationError):
            ScrapeConfig(
                data_fields=["stars"],
                max_results=-1,
                concurrency=5,
                cache_ttl=3600,
            )

    def test_zero_concurrency_raises_error(self):
        """Test that zero concurrency raises validation error."""
        with pytest.raises(ValidationError):
            ScrapeConfig(
                data_fields=["stars"],
                max_results=100,
                concurrency=0,
                cache_ttl=3600,
            )

    def test_concurrency_over_100_raises_error(self):
        """Test that concurrency over 100 raises validation error."""
        with pytest.raises(ValidationError):
            ScrapeConfig(
                data_fields=["stars"],
                max_results=100,
                concurrency=101,
                cache_ttl=3600,
            )

    def test_negative_cache_ttl_raises_error(self):
        """Test that negative cache_ttl raises validation error."""
        with pytest.raises(ValidationError):
            ScrapeConfig(
                data_fields=["stars"],
                max_results=100,
                concurrency=5,
                cache_ttl=-1,
            )

    def test_zero_cache_ttl_is_valid(self):
        """Test that zero cache_ttl is valid."""
        config = ScrapeConfig(
            data_fields=["stars"],
            max_results=100,
            concurrency=5,
            cache_ttl=0,
        )
        assert config.cache_ttl == 0