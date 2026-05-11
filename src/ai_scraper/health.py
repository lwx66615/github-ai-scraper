"""Repository health assessment."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class HealthScore:
    """Repository health score breakdown."""

    overall: float
    activity: float
    popularity: float
    maintenance: float
    community: float
    grade: str


class HealthAssessor:
    """Assess repository health based on multiple factors."""

    def assess(self, repo: Repository) -> HealthScore:
        """Assess repository health.

        Args:
            repo: Repository to assess.

        Returns:
            Health score breakdown.
        """
        activity = self._score_activity(repo)
        popularity = self._score_popularity(repo)
        maintenance = self._score_maintenance(repo)
        community = self._score_community(repo)

        # Weighted overall score
        overall = (
            activity * 0.3 +
            popularity * 0.25 +
            maintenance * 0.25 +
            community * 0.2
        )

        grade = self.get_grade(overall)

        return HealthScore(
            overall=overall,
            activity=activity,
            popularity=popularity,
            maintenance=maintenance,
            community=community,
            grade=grade,
        )

    def _score_activity(self, repo: Repository) -> float:
        """Score repository activity (0-100)."""
        if not repo.pushed_at:
            return 0

        days_since_push = (datetime.now() - repo.pushed_at).days

        if days_since_push <= 7:
            return 100
        elif days_since_push <= 30:
            return 80
        elif days_since_push <= 90:
            return 60
        elif days_since_push <= 180:
            return 40
        elif days_since_push <= 365:
            return 20
        else:
            return 0

    def _score_popularity(self, repo: Repository) -> float:
        """Score repository popularity (0-100)."""
        stars = repo.stars

        if stars >= 10000:
            return 100
        elif stars >= 5000:
            return 85
        elif stars >= 1000:
            return 70
        elif stars >= 500:
            return 55
        elif stars >= 100:
            return 40
        elif stars >= 50:
            return 25
        else:
            return 10

    def _score_maintenance(self, repo: Repository) -> float:
        """Score repository maintenance (0-100)."""
        if not repo.open_issues:
            return 50  # Unknown

        # Lower open issues ratio is better
        if repo.stars > 0:
            issue_ratio = repo.open_issues / repo.stars
            if issue_ratio < 0.01:
                return 100
            elif issue_ratio < 0.05:
                return 80
            elif issue_ratio < 0.1:
                return 60
            elif issue_ratio < 0.2:
                return 40
            else:
                return 20

        return 50

    def _score_community(self, repo: Repository) -> float:
        """Score community engagement (0-100)."""
        forks = repo.forks or 0

        if forks >= 1000:
            return 100
        elif forks >= 500:
            return 85
        elif forks >= 100:
            return 70
        elif forks >= 50:
            return 55
        elif forks >= 10:
            return 40
        elif forks >= 5:
            return 25
        else:
            return 10

    def get_grade(self, score: float) -> str:
        """Convert score to letter grade.

        Args:
            score: Score (0-100).

        Returns:
            Letter grade (A-F).
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
