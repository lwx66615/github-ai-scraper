"""REST API server for ai-scraper."""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from ai_scraper.config import load_config
from ai_scraper.storage.async_database import AsyncDatabase


# Global database instance
db: Optional[AsyncDatabase] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global db
    config = load_config()
    db = AsyncDatabase(Path(config.database.path))
    if Path(config.database.path).exists():
        await db.init_db()
    yield
    if db:
        await db.close()


app = FastAPI(
    title="GitHub AI Scraper API",
    description="REST API for accessing scraped AI repositories",
    version="0.1.0",
    lifespan=lifespan,
)


class RepositoryResponse(BaseModel):
    """Repository API response model."""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    language: Optional[str]
    topics: list[str]
    url: str


class StatsResponse(BaseModel):
    """Statistics API response model."""
    repository_count: int
    snapshot_count: int
    total_stars: int


@app.get("/api/repos", response_model=list[RepositoryResponse])
async def list_repositories(
    limit: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="stars", pattern="^(stars|updated|relevance)$"),
    language: Optional[str] = None,
    min_stars: Optional[int] = None,
):
    """List repositories with optional filters."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    repos = await db.get_all_repositories(limit=limit, sort_by=sort)

    if language:
        repos = [r for r in repos if r.language and r.language.lower() == language.lower()]
    if min_stars:
        repos = [r for r in repos if r.stars >= min_stars]

    return [
        RepositoryResponse(
            id=r.id,
            name=r.name,
            full_name=r.full_name,
            description=r.description,
            stars=r.stars,
            language=r.language,
            topics=r.topics,
            url=r.url,
        )
        for r in repos
    ]


@app.get("/api/repos/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: int):
    """Get a specific repository by ID."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    # Use direct query instead of full scan
    repo = await db.get_repository_by_id(repo_id)

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryResponse(
        id=repo.id,
        name=repo.name,
        full_name=repo.full_name,
        description=repo.description,
        stars=repo.stars,
        language=repo.language,
        topics=repo.topics,
        url=repo.url,
    )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get database statistics."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    stats = await db.get_stats()
    return StatsResponse(**stats)


@app.get("/api/trending")
async def get_trending(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get trending repositories."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    trends = await db.get_trending(days=days, limit=limit)
    return [
        {
            "repo_id": t.repo_id,
            "repo_name": t.repo_name,
            "initial_stars": t.initial_stars,
            "current_stars": t.current_stars,
            "growth_rate": round(t.growth_rate * 100, 2),
        }
        for t in trends
    ]


@app.get("/api/search")
async def search_repositories(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Search repositories by name or description."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    repos = await db.search_local(query=q, limit=limit)
    return [
        RepositoryResponse(
            id=r.id,
            name=r.name,
            full_name=r.full_name,
            description=r.description,
            stars=r.stars,
            language=r.language,
            topics=r.topics,
            url=r.url,
        )
        for r in repos
    ]


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
