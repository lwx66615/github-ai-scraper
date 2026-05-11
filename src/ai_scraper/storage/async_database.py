"""Async SQLite database storage."""

import json
import aiosqlite
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


class AsyncDatabase:
    """Async SQLite database for storing repository data."""

    def __init__(self, db_path: Path):
        """Initialize database.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[aiosqlite.Connection] = None

    async def init_db(self) -> None:
        """Initialize database tables."""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row

        await self.conn.executescript("""
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
            );

            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id INTEGER,
                stars INTEGER,
                snapshot_at TIMESTAMP,
                FOREIGN KEY (repo_id) REFERENCES repositories(id)
            );

            CREATE INDEX IF NOT EXISTS idx_stars ON repositories(stars DESC);
            CREATE INDEX IF NOT EXISTS idx_updated ON repositories(last_updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_repo_id ON snapshots(repo_id);
            CREATE INDEX IF NOT EXISTS idx_language ON repositories(language);
            CREATE INDEX IF NOT EXISTS idx_created_at ON repositories(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_relevance ON repositories(relevance_score DESC);
            CREATE INDEX IF NOT EXISTS idx_snapshot_at ON snapshots(snapshot_at DESC);
        """)
        await self.conn.commit()

    async def save_repository(self, repo: Repository, relevance_score: float = 0.0) -> None:
        """Save or update a repository."""
        now = datetime.now().isoformat()

        await self.conn.execute("""
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
        await self.conn.commit()

    async def get_repository_by_id(self, repo_id: int) -> Optional[Repository]:
        """Get a specific repository by ID."""
        cursor = await self.conn.execute(
            "SELECT * FROM repositories WHERE id = ?", (repo_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return self._row_to_repo(row)

    async def get_all_repositories(self, limit: int = 100, sort_by: str = "stars") -> list[Repository]:
        """Get all repositories."""
        valid_sort_fields = ["stars", "updated_at", "relevance_score"]
        sort_field = sort_by if sort_by in valid_sort_fields else "stars"

        cursor = await self.conn.execute(f"""
            SELECT * FROM repositories
            ORDER BY {sort_field} DESC
            LIMIT ?
        """, (limit,))

        rows = await cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    async def get_stats(self) -> dict:
        """Get database statistics."""
        cursor = await self.conn.execute("SELECT COUNT(*) as count FROM repositories")
        row = await cursor.fetchone()
        repo_count = row["count"]

        cursor = await self.conn.execute("SELECT COUNT(*) as count FROM snapshots")
        row = await cursor.fetchone()
        snapshot_count = row["count"]

        cursor = await self.conn.execute("SELECT SUM(stars) as total FROM repositories")
        row = await cursor.fetchone()
        total_stars = row["total"] or 0

        return {
            "repository_count": repo_count,
            "snapshot_count": snapshot_count,
            "total_stars": total_stars,
        }

    async def get_last_scrape_time(self) -> Optional[datetime]:
        """Get the timestamp of the most recent repository update."""
        cursor = await self.conn.execute(
            "SELECT MAX(last_updated_at) as max_time FROM repositories"
        )
        row = await cursor.fetchone()

        if row["max_time"] is None:
            return None

        return datetime.fromisoformat(row["max_time"])

    async def search_local(self, query: str, limit: int = 20) -> list[Repository]:
        """Search repositories locally."""
        cursor = await self.conn.execute("""
            SELECT * FROM repositories
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY stars DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        rows = await cursor.fetchall()
        return [self._row_to_repo(row) for row in rows]

    async def get_trending(self, days: int = 7, limit: int = 10) -> list[TrendResult]:
        """Get trending repositories by star growth."""
        cursor = await self.conn.execute("""
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
        async for row in cursor:
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

    async def close(self) -> None:
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None

    def _row_to_repo(self, row: aiosqlite.Row) -> Repository:
        """Convert database row to Repository object."""
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
