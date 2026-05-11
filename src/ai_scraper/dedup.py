"""Repository deduplication utilities."""

from dataclasses import dataclass
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class DuplicationInfo:
    """Information about repository duplication."""
    is_fork: bool
    is_mirror: bool
    original_repo: Optional[str]
    duplicate_type: str  # "fork", "mirror", "none"


class DeduplicationChecker:
    """Check for repository duplicates."""

    # Common mirror patterns
    MIRROR_PATTERNS = [
        "-mirror",
        "-mirror.git",
        ".mirror",
        "mirror-",
    ]

    def check(self, repo: Repository) -> DuplicationInfo:
        """Check if repository is a duplicate.

        Args:
            repo: Repository to check.

        Returns:
            Duplication information.
        """
        # Check mirror patterns in name
        name_lower = repo.name.lower()
        is_mirror = any(pattern in name_lower for pattern in self.MIRROR_PATTERNS)

        # Extract original repo name if mirror
        original = None
        if is_mirror:
            original = self._extract_original_name(repo.name)

        return DuplicationInfo(
            is_fork=False,  # Would need API data
            is_mirror=is_mirror,
            original_repo=original,
            duplicate_type="mirror" if is_mirror else "none",
        )

    def _extract_original_name(self, mirror_name: str) -> str:
        """Extract original repository name from mirror name."""
        name = mirror_name
        for pattern in self.MIRROR_PATTERNS:
            name = name.replace(pattern, "")
        return name.strip("-_")

    def find_duplicates(self, repos: list[Repository]) -> dict[str, list[Repository]]:
        """Find groups of duplicate repositories.

        Args:
            repos: List of repositories.

        Returns:
            Dictionary mapping normalized names to duplicate groups.
        """
        groups: dict[str, list[Repository]] = {}

        for repo in repos:
            normalized = self._normalize_name(repo.name)
            if normalized not in groups:
                groups[normalized] = []
            groups[normalized].append(repo)

        # Return only groups with duplicates
        return {k: v for k, v in groups.items() if len(v) > 1}

    def _normalize_name(self, name: str) -> str:
        """Normalize repository name for comparison."""
        name = name.lower()
        # Remove common suffixes
        for suffix in ["-mirror", "-mirror.git", ".mirror", "-fork"]:
            name = name.replace(suffix, "")
        # Remove organization prefix
        if "/" in name:
            name = name.split("/")[-1]
        return name.strip("-_")