"""Tests for deduplication checker."""

from datetime import datetime

from ai_scraper.dedup import DeduplicationChecker, DuplicationInfo
from ai_scraper.models.repository import Repository


def make_repo(name: str, full_name: str = None) -> Repository:
    """Helper to create test repository."""
    return Repository(
        id=1,
        name=name,
        full_name=full_name or name,
        description="Test repo",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url=f"https://github.com/{name}",
    )


def test_check_returns_mirror_for_mirror_repo():
    """Test check returns correct info for mirror repos."""
    checker = DeduplicationChecker()

    repo = make_repo("awesome-project-mirror")
    info = checker.check(repo)

    assert info.is_mirror is True
    assert info.is_fork is False
    assert info.original_repo == "awesome-project"
    assert info.duplicate_type == "mirror"


def test_check_returns_mirror_for_git_mirror_repo():
    """Test check handles -mirror.git suffix."""
    checker = DeduplicationChecker()

    repo = make_repo("project-mirror.git")
    info = checker.check(repo)

    assert info.is_mirror is True
    assert info.original_repo == "project.git"


def test_check_returns_mirror_for_dot_mirror_repo():
    """Test check handles .mirror suffix."""
    checker = DeduplicationChecker()

    repo = make_repo("project.mirror")
    info = checker.check(repo)

    assert info.is_mirror is True
    assert info.original_repo == "project"


def test_check_returns_none_for_normal_repo():
    """Test check returns none for normal repos."""
    checker = DeduplicationChecker()

    repo = make_repo("awesome-project")
    info = checker.check(repo)

    assert info.is_mirror is False
    assert info.is_fork is False
    assert info.original_repo is None
    assert info.duplicate_type == "none"


def test_check_case_insensitive():
    """Test mirror detection is case insensitive."""
    checker = DeduplicationChecker()

    repo = make_repo("Project-MIRROR")
    info = checker.check(repo)

    assert info.is_mirror is True


def test_find_duplicates_finds_groups():
    """Test find_duplicates finds duplicate groups."""
    checker = DeduplicationChecker()

    repos = [
        make_repo("project-a"),
        make_repo("project-a-mirror"),
        make_repo("project-b"),
        make_repo("project-b-mirror"),
        make_repo("project-c"),
    ]

    duplicates = checker.find_duplicates(repos)

    assert len(duplicates) == 2
    assert "project-a" in duplicates
    assert "project-b" in duplicates
    assert len(duplicates["project-a"]) == 2
    assert len(duplicates["project-b"]) == 2


def test_find_duplicates_empty_for_no_duplicates():
    """Test find_duplicates returns empty for no duplicates."""
    checker = DeduplicationChecker()

    repos = [
        make_repo("project-a"),
        make_repo("project-b"),
        make_repo("project-c"),
    ]

    duplicates = checker.find_duplicates(repos)

    assert len(duplicates) == 0


def test_normalize_name_removes_mirror_suffix():
    """Test _normalize_name removes mirror suffix."""
    checker = DeduplicationChecker()

    assert checker._normalize_name("project-mirror") == "project"
    assert checker._normalize_name("project-mirror.git") == "project.git"
    assert checker._normalize_name("project.mirror") == "project"


def test_normalize_name_removes_fork_suffix():
    """Test _normalize_name removes fork suffix."""
    checker = DeduplicationChecker()

    assert checker._normalize_name("project-fork") == "project"


def test_normalize_name_removes_org_prefix():
    """Test _normalize_name removes organization prefix."""
    checker = DeduplicationChecker()

    assert checker._normalize_name("org/project") == "project"
    assert checker._normalize_name("org/project-mirror") == "project"


def test_normalize_name_lowercase():
    """Test _normalize_name converts to lowercase."""
    checker = DeduplicationChecker()

    assert checker._normalize_name("Project-A") == "project-a"
    assert checker._normalize_name("PROJECT-B") == "project-b"


def test_normalize_name_strips_dashes_and_underscores():
    """Test _normalize_name strips leading/trailing dashes and underscores."""
    checker = DeduplicationChecker()

    assert checker._normalize_name("-project-") == "project"
    assert checker._normalize_name("_project_") == "project"


def test_extract_original_name():
    """Test _extract_original_name extracts original name."""
    checker = DeduplicationChecker()

    assert checker._extract_original_name("project-mirror") == "project"
    assert checker._extract_original_name("project.mirror") == "project"
    assert checker._extract_original_name("mirror-project") == "project"


def test_find_duplicates_groups_by_normalized_name():
    """Test find_duplicates groups repos with same normalized name."""
    checker = DeduplicationChecker()

    repos = [
        make_repo("Project-A"),
        make_repo("project-a-mirror"),
        make_repo("PROJECT-A-FORK"),
    ]

    duplicates = checker.find_duplicates(repos)

    assert len(duplicates) == 1
    assert "project-a" in duplicates
    assert len(duplicates["project-a"]) == 3