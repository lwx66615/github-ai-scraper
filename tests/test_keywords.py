"""Tests for keyword extraction module."""

import tempfile
from pathlib import Path

import pytest

from ai_scraper.keywords import KeywordExtractor
from ai_scraper.models import Repository
from datetime import datetime


@pytest.fixture
def temp_keywords_file():
    """Create a temporary file for keywords."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("machine-learning\ndeep-learning\nneural-network\n")
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_repos():
    """Create sample repositories for testing."""
    return [
        Repository(
            id=1,
            name="awesome-ml-framework",
            full_name="user/awesome-ml-framework",
            description="A powerful machine learning framework for deep neural networks",
            stars=1000,
            language="Python",
            topics=["machine-learning", "deep-learning", "neural-networks", "ai"],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/awesome-ml-framework",
        ),
        Repository(
            id=2,
            name="pytorch-transformers",
            full_name="org/pytorch-transformers",
            description="State-of-the-art Natural Language Processing with transformers",
            stars=5000,
            language="Python",
            topics=["nlp", "transformers", "huggingface", "pytorch"],
            created_at=datetime(2019, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/org/pytorch-transformers",
        ),
        Repository(
            id=3,
            name="simple_api",
            full_name="user/simple_api",
            description="The API for testing basic functionality",
            stars=100,
            language="Python",
            topics=["api", "rest"],
            created_at=datetime(2021, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/simple_api",
        ),
    ]


class TestLoadKeywords:
    """Tests for loading keywords."""

    def test_load_from_nonexistent_file_returns_empty_set(self):
        """Loading from non-existent file should return empty set."""
        extractor = KeywordExtractor(Path("/nonexistent/path/keywords.txt"))
        keywords = extractor.load_keywords()
        assert keywords == set()

    def test_load_from_existing_file(self, temp_keywords_file):
        """Loading from existing file should return keywords."""
        extractor = KeywordExtractor(temp_keywords_file)
        keywords = extractor.load_keywords()
        assert "machine-learning" in keywords
        assert "deep-learning" in keywords
        assert "neural-network" in keywords


class TestSaveKeywords:
    """Tests for saving keywords."""

    def test_save_and_load_keywords(self, temp_keywords_file):
        """Saving keywords should persist them to file."""
        extractor = KeywordExtractor(temp_keywords_file)
        keywords = {"new-keyword", "another-keyword", "third-keyword"}
        extractor.save_keywords(keywords)

        # Reload and verify
        loaded = extractor.load_keywords()
        assert loaded == keywords

    def test_save_overwrites_existing(self, temp_keywords_file):
        """Saving should overwrite existing file content."""
        extractor = KeywordExtractor(temp_keywords_file)
        new_keywords = {"completely-new"}
        extractor.save_keywords(new_keywords)

        loaded = extractor.load_keywords()
        assert loaded == new_keywords
        # Old keywords should be gone
        assert "machine-learning" not in loaded


class TestExtractFromTopics:
    """Tests for extracting keywords from topics."""

    def test_extract_from_topics(self):
        """Topics should be extracted directly (lowercase)."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description=None,
            stars=100,
            language="Python",
            topics=["Machine-Learning", "AI", "Deep-Learning"],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        topics = extractor._extract_from_topics(repo)
        assert "machine-learning" in topics
        assert "ai" in topics
        assert "deep-learning" in topics

    def test_extract_from_empty_topics(self):
        """Empty topics should return empty set."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        topics = extractor._extract_from_topics(repo)
        assert topics == set()


class TestExtractFromDescription:
    """Tests for extracting keywords from description."""

    def test_extract_from_description(self):
        """Description should be split and filtered."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description="A machine learning framework for neural networks",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_description(repo)
        assert "machine" in keywords
        assert "learning" in keywords
        assert "framework" in keywords
        assert "neural" in keywords
        assert "networks" in keywords
        # Stopwords should be filtered
        assert "a" not in keywords
        assert "for" not in keywords

    def test_extract_from_description_filters_stopwords(self):
        """Stopwords should be filtered from description."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description="the and or but is are was were be been being",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_description(repo)
        assert keywords == set()

    def test_extract_from_description_min_length(self):
        """Keywords should have minimum 2 characters."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description="a b c ab cd ef",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_description(repo)
        # Only words with 2+ chars should be included
        assert "ab" in keywords
        assert "cd" in keywords
        assert "ef" in keywords
        assert "a" not in keywords
        assert "b" not in keywords
        assert "c" not in keywords

    def test_extract_from_description_no_pure_digits(self):
        """Pure digit strings should be filtered."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description="python3 gpt4 12345 2023 model",
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_description(repo)
        # Alphanumeric should be included
        assert "python3" in keywords
        assert "gpt4" in keywords
        assert "model" in keywords
        # Pure digits should be filtered
        assert "12345" not in keywords
        assert "2023" not in keywords

    def test_extract_from_none_description(self):
        """None description should return empty set."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="test",
            full_name="user/test",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_description(repo)
        assert keywords == set()


class TestExtractFromName:
    """Tests for extracting keywords from repository name."""

    def test_extract_from_name_with_hyphens(self):
        """Name with hyphens should be split."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="machine-learning-framework",
            full_name="user/machine-learning-framework",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "machine" in keywords
        assert "learning" in keywords
        assert "framework" in keywords

    def test_extract_from_name_with_underscores(self):
        """Name with underscores should be split."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="deep_neural_network",
            full_name="user/deep_neural_network",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "deep" in keywords
        assert "neural" in keywords
        assert "network" in keywords

    def test_extract_from_name_mixed_separators(self):
        """Name with mixed separators should be split."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="ai-ml_framework",
            full_name="user/ai-ml_framework",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "ai" in keywords
        assert "ml" in keywords
        assert "framework" in keywords

    def test_extract_from_name_filters_stopwords(self):
        """Stopwords should be filtered from name."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="the-best-ai-and-ml",
            full_name="user/the-best-ai-and-ml",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "ai" in keywords
        assert "ml" in keywords
        assert "best" in keywords
        # Stopwords should be filtered
        assert "the" not in keywords
        assert "and" not in keywords

    def test_extract_from_name_min_length(self):
        """Name parts should have minimum 2 characters."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="a-b-c-de-fg",
            full_name="user/a-b-c-de-fg",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "de" in keywords
        assert "fg" in keywords
        assert "a" not in keywords
        assert "b" not in keywords
        assert "c" not in keywords

    def test_extract_from_name_no_pure_digits(self):
        """Pure digits should be filtered from name."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        repo = Repository(
            id=1,
            name="gpt4-model-2023",
            full_name="user/gpt4-model-2023",
            description=None,
            stars=100,
            language="Python",
            topics=[],
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2023, 1, 1),
            pushed_at=datetime(2023, 1, 1),
            url="https://github.com/user/test",
        )
        keywords = extractor._extract_from_name(repo)
        assert "gpt4" in keywords
        assert "model" in keywords
        # Pure digits filtered
        assert "2023" not in keywords


class TestExtractFromRepos:
    """Tests for extracting keywords from multiple repositories."""

    def test_extract_from_repos(self, sample_repos):
        """Should extract keywords from all repos."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        keywords = extractor.extract_from_repos(sample_repos)
        # From topics
        assert "machine-learning" in keywords
        assert "deep-learning" in keywords
        assert "neural-networks" in keywords
        assert "ai" in keywords
        assert "nlp" in keywords
        assert "transformers" in keywords
        # From names
        assert "awesome" in keywords
        assert "framework" in keywords
        assert "pytorch" in keywords
        # From descriptions
        assert "powerful" in keywords
        assert "state" in keywords

    def test_extract_from_empty_list(self):
        """Empty repo list should return empty set."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"))
        keywords = extractor.extract_from_repos([])
        assert keywords == set()


class TestMergeKeywords:
    """Tests for merging keywords."""

    def test_merge_within_limit(self):
        """Merging within limit should combine all keywords."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"), max_keywords=10)
        existing = {"a", "b", "c"}
        new = {"d", "e", "f"}
        merged = extractor.merge_keywords(existing, new)
        assert merged == {"a", "b", "c", "d", "e", "f"}

    def test_merge_exceeds_limit(self):
        """Merging exceeding limit should respect max_keywords."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"), max_keywords=5)
        existing = {"a", "b", "c"}
        new = {"d", "e", "f", "g", "h"}
        merged = extractor.merge_keywords(existing, new)
        assert len(merged) <= 5

    def test_merge_preserves_existing(self):
        """Merging should preserve existing keywords when possible."""
        extractor = KeywordExtractor(Path("/tmp/test.txt"), max_keywords=5)
        existing = {"important-keyword", "another"}
        new = {"new1", "new2", "new3"}
        merged = extractor.merge_keywords(existing, new)
        # Existing keywords should be prioritized
        assert "important-keyword" in merged or "another" in merged


class TestGetKeywordsForSearch:
    """Tests for getting keywords as list for search."""

    def test_get_keywords_as_list(self, temp_keywords_file):
        """Should return keywords as a list."""
        extractor = KeywordExtractor(temp_keywords_file)
        keywords_list = extractor.get_keywords_for_search()
        assert isinstance(keywords_list, list)
        assert "machine-learning" in keywords_list
        assert "deep-learning" in keywords_list

    def test_get_keywords_returns_sorted_list(self, temp_keywords_file):
        """Should return sorted list for reproducibility."""
        extractor = KeywordExtractor(temp_keywords_file)
        keywords_list = extractor.get_keywords_for_search()
        assert keywords_list == sorted(keywords_list)

    def test_get_keywords_empty_file(self):
        """Empty or non-existent file should return empty list."""
        extractor = KeywordExtractor(Path("/nonexistent/path/keywords.txt"))
        keywords_list = extractor.get_keywords_for_search()
        assert keywords_list == []
