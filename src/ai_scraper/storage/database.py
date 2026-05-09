"""SQLite database storage."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class TrendResult:
    """Trend analysis result."""

    repo_id: int
    repo_name: str
    initial_stars: int
    current_stars: int
    growth_rate: float


class Database:
    """SQLite database for storing repository data."""

    def __init__(self, db_path: Path):
        """Initialize database.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None

    def init_db(self) -> None:
        """Initialize database tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create repositories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                full_name TEXT,
                description TEXT,
                stars INTEGER,
                language TEXT,
                topics TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                pushed_at TIMESTAMP,
                url TEXT,
                open_issues INTEGER,
                forks INTEGER,
                contributors INTEGER,
                relevance_score REAL,
                first_seen_at TIMESTAMP,
                last_updated_at TIMESTAMP
            )
        """)

        # Create snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id INTEGER,
                stars INTEGER,
                snapshot_at TIMESTAMP,
                FOREIGN KEY (repo_id) REFERENCES repositories(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stars ON repositories(stars DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_updated ON repositories(last_updated_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_id ON snapshots(repo_id)")

        self.conn.commit()

    def save_repository(self, repo: Repository, relevance_score: float = 0.0) -> None:
        """Save or update a repository.

        Args:
            repo: Repository to save.
            relevance_score: AI relevance score.
        """
        cursor = self.conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO repositories (
                id, name, full_name, description, stars, language, topics,
                created_at, updated_at, pushed_at, url, open_issues, forks,
                contributors, relevance_score, first_seen_at, last_updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                full_name = excluded.full_name,
                description = excluded.description,
                stars = excluded.stars,
                language = excluded.language,
                topics = excluded.topics,
                updated_at = excluded.updated_at,
                pushed_at = excluded.pushed_at,
                open_issues = excluded.open_issues,
                forks = excluded.forks,
                contributors = excluded.contributors,
                relevance_score = excluded.relevance_score,
                last_updated_at = excluded.last_updated_at
        """, (
            repo.id, repo.name, repo.full_name, repo.description, repo.stars,
            repo.language, json.dumps(repo.topics), repo.created_at.isoformat(),
            repo.updated_at.isoformat(), repo.pushed_at.isoformat(), repo.url,
            repo.open_issues, repo.forks, repo.contributors, relevance_score,
            now, now
        ))

        self.conn.commit()

    def save_snapshot(self, repo_id: int, stars: int, snapshot_at: datetime) -> None:
        """Save a repository snapshot.

        Args:
            repo_id: Repository ID.
            stars: Star count at snapshot time.
            snapshot_at: Snapshot timestamp.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO snapshots (repo_id, stars, snapshot_at)
            VALUES (?, ?, ?)
        """, (repo_id, stars, snapshot_at.isoformat()))

        self.conn.commit()

    def get_snapshots(self, repo_id: int) -> list[dict]:
        """Get snapshots for a repository.

        Args:
            repo_id: Repository ID.

        Returns:
            List of snapshot records.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT stars, snapshot_at FROM snapshots
            WHERE repo_id = ?
            ORDER BY snapshot_at DESC
        """, (repo_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_all_repositories(self, limit: int = 100, sort_by: str = "stars") -> list[Repository]:
        """Get all repositories.

        Args:
            limit: Maximum number of repositories to return.
            sort_by: Field to sort by.

        Returns:
            List of repositories.
        """
        cursor = self.conn.cursor()

        valid_sort_fields = ["stars", "updated_at", "relevance_score"]
        sort_field = sort_by if sort_by in valid_sort_fields else "stars"

        cursor.execute(f"""
            SELECT * FROM repositories
            ORDER BY {sort_field} DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    def get_trending(self, days: int = 7, limit: int = 10) -> list[TrendResult]:
        """Get trending repositories by star growth.

        Args:
            days: Number of days to analyze.
            limit: Maximum number of results.

        Returns:
            List of trending repositories.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                r.id as repo_id,
                r.name as repo_name,
                s1.stars as initial_stars,
                r.stars as current_stars
            FROM repositories r
            JOIN snapshots s1 ON r.id = s1.repo_id
            WHERE s1.snapshot_at >= datetime('now', ?)
            GROUP BY r.id
            HAVING current_stars > initial_stars
            ORDER BY (CAST(current_stars AS FLOAT) / initial_stars - 1) DESC
            LIMIT ?
        """, (f'-{days} days', limit))

        results = []
        for row in cursor.fetchall():
            initial = row["initial_stars"]
            current = row["current_stars"]
            growth = (current - initial) / initial if initial > 0 else 0.0

            results.append(TrendResult(
                repo_id=row["repo_id"],
                repo_name=row["repo_name"],
                initial_stars=initial,
                current_stars=current,
                growth_rate=growth,
            ))

        return results

    def search_local(self, query: str, limit: int = 20) -> list[Repository]:
        """Search repositories locally.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            List of matching repositories.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM repositories
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY stars DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        rows = cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    def get_stats(self) -> dict:
        """Get database statistics.

        Returns:
            Dictionary with statistics.
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM repositories")
        repo_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM snapshots")
        snapshot_count = cursor.fetchone()["count"]

        cursor.execute("SELECT SUM(stars) as total FROM repositories")
        total_stars = cursor.fetchone()["total"] or 0

        return {
            "repository_count": repo_count,
            "snapshot_count": snapshot_count,
            "total_stars": total_stars,
        }

    def clean_old_snapshots(self, days: int = 30) -> int:
        """Clean snapshots older than specified days.

        Args:
            days: Number of days to keep.

        Returns:
            Number of deleted snapshots.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            DELETE FROM snapshots
            WHERE snapshot_at < datetime('now', ?)
        """, (f'-{days} days',))

        deleted = cursor.rowcount
        self.conn.commit()

        return deleted

    def _row_to_repo(self, row: sqlite3.Row) -> Repository:
        """Convert database row to Repository object.

        Args:
            row: Database row.

        Returns:
            Repository object.
        """
        return Repository(
            id=row["id"],
            name=row["name"],
            full_name=row["full_name"],
            description=row["description"],
            stars=row["stars"],
            language=row["language"],
            topics=json.loads(row["topics"]) if row["topics"] else [],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            pushed_at=datetime.fromisoformat(row["pushed_at"]) if row["pushed_at"] else None,
            url=row["url"],
            open_issues=row["open_issues"],
            forks=row["forks"],
            contributors=row["contributors"],
        )

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
