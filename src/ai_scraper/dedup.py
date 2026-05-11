"""Repository deduplication utilities."""

from dataclasses import dataclass
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class DuplicationInfo:
    """Information about repository duplication."""
    is_fork: bool
    is_mirror: bool
    is_similar: bool
    original_repo: Optional[str]
    duplicate_type: str  # "fork", "mirror", "similar", "none"
    similarity_score: float = 0.0


class DeduplicationChecker:
    """Check for repository duplicates."""

    # Common mirror patterns
    MIRROR_PATTERNS = [
        "-mirror",
        "-mirror.git",
        ".mirror",
        "mirror-",
    ]

    def check(self, repo: Repository, is_fork: bool = False) -> DuplicationInfo:
        """Check if repository is a duplicate.

        Args:
            repo: Repository to check.
            is_fork: Whether the repo is a fork (from API data).

        Returns:
            Duplication information.
        """
        # Check mirror patterns in name
        name_lower = repo.name.lower()
        is_mirror = any(pattern in name_lower for pattern in self.MIRROR_PATTERNS)

        # Extract original repo name if mirror
        original = None
        duplicate_type = "none"

        if is_fork:
            duplicate_type = "fork"
            original = self._extract_original_from_fork(repo.name)
        elif is_mirror:
            duplicate_type = "mirror"
            original = self._extract_original_name(repo.name)

        return DuplicationInfo(
            is_fork=is_fork,
            is_mirror=is_mirror,
            is_similar=False,
            original_repo=original,
            duplicate_type=duplicate_type,
        )

    def _extract_original_name(self, mirror_name: str) -> str:
        """Extract original repository name from mirror name."""
        name = mirror_name
        for pattern in self.MIRROR_PATTERNS:
            name = name.replace(pattern, "")
        return name.strip("-_")

    def _extract_original_from_fork(self, fork_name: str) -> str:
        """Extract original repo name from fork."""
        # Fork name is usually user/original-repo
        # We'd need API data to know the actual original
        return fork_name

    def find_similar_content(
        self,
        repos: list[Repository],
        threshold: float = 0.8,
    ) -> list[tuple[Repository, Repository, float]]:
        """Find repositories with similar content.

        Args:
            repos: List of repositories.
            threshold: Similarity threshold (0-1).

        Returns:
            List of (repo1, repo2, similarity) tuples.
        """
        similar_pairs = []

        for i, repo1 in enumerate(repos):
            for repo2 in repos[i + 1:]:
                similarity = self._calculate_similarity(repo1, repo2)
                if similarity >= threshold:
                    similar_pairs.append((repo1, repo2, similarity))

        return similar_pairs

    def _calculate_similarity(self, repo1: Repository, repo2: Repository) -> float:
        """Calculate similarity between two repositories."""
        # Compare descriptions
        desc1 = (repo1.description or "").lower()
        desc2 = (repo2.description or "").lower()

        # Simple Jaccard similarity on words
        words1 = set(desc1.split())
        words2 = set(desc2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

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