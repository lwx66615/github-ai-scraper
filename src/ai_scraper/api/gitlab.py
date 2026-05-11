"""GitLab API client."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp

from ai_scraper.api.rate_limiter import RateLimitInfo, RateLimiter
from ai_scraper.cache import RequestCache
from ai_scraper.models.repository import Repository

logger = logging.getLogger(__name__)


class GitLabAPIError(Exception):
    """GitLab API error."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"GitLab API error {status}: {message}")


class GitLabClient:
    """Asynchronous GitLab API client.

    Supports both gitlab.com and self-hosted GitLab instances.
    """

    DEFAULT_BASE_URL = "https://gitlab.com/api/v4"

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        connection_pool_size: int = 10,
    ):
        """Initialize GitLab client.

        Args:
            token: GitLab Personal Access Token (optional).
            base_url: GitLab API base URL (default: gitlab.com).
                      For self-hosted: "https://your-gitlab.com/api/v4"
            cache_dir: Directory for cache files (optional).
            cache_ttl: Cache time-to-live in seconds.
            connection_pool_size: Maximum number of connections in pool.
        """
        self.token = token
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.connection_pool_size = connection_pool_size

        # Rate limiter: GitLab has higher limits
        # Authenticated: 2000 requests per minute
        # Unauthenticated: 100 requests per minute
        rate = 2000 if token else 100
        self.rate_limiter = RateLimiter(requests_per_hour=rate * 60)

        # Request cache
        self.cache: Optional[RequestCache] = None
        if cache_dir:
            self.cache = RequestCache(cache_dir=cache_dir, ttl=cache_ttl)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with connection pooling."""
        if self.session is None or self.session.closed:
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["PRIVATE-TOKEN"] = self.token

            # Configure connection pool
            connector = aiohttp.TCPConnector(
                limit=self.connection_pool_size,
                limit_per_host=self.connection_pool_size,
                enable_cleanup_closed=True,
            )

            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self.session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        method: str = "GET",
    ) -> dict | list:
        """Make an API request.

        Args:
            endpoint: API endpoint (without base URL).
            params: Query parameters.
            method: HTTP method.

        Returns:
            JSON response data.

        Raises:
            GitLabAPIError: On API errors.
        """
        url = f"{self.base_url}{endpoint}"

        # Check cache first (only for GET requests)
        if method == "GET" and self.cache:
            cached = self.cache.get(url, params)
            if cached is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached

        # Wait for rate limiter
        while not self.rate_limiter.try_acquire():
            wait_time = self.rate_limiter.wait_time()
            logger.debug(f"Rate limited, waiting {wait_time:.1f}s")
            await asyncio.sleep(min(wait_time, 1.0))

        session = await self._get_session()

        async with session.request(method, url, params=params) as response:
            if response.status == 401:
                raise GitLabAPIError(401, "Unauthorized - check your token")
            elif response.status == 403:
                raise GitLabAPIError(403, "Forbidden - check your permissions")
            elif response.status == 404:
                raise GitLabAPIError(404, "Resource not found")
            elif response.status == 429:
                # Rate limited
                retry_after = response.headers.get("Retry-After", "60")
                raise GitLabAPIError(429, f"Rate limited, retry after {retry_after}s")
            elif response.status >= 400:
                text = await response.text()
                raise GitLabAPIError(response.status, text)

            data = await response.json()

            # Cache successful GET response
            if method == "GET" and self.cache:
                self.cache.set(url, params, data)
                logger.debug(f"Cached response for {endpoint}")

            return data

    async def search_projects(
        self,
        query: str,
        sort: str = "star_count",
        order: str = "desc",
        page: int = 1,
        per_page: int = 100,
        min_stars: int = 0,
        topics: Optional[list[str]] = None,
    ) -> list[Repository]:
        """Search projects.

        Args:
            query: Search query.
            sort: Sort field (star_count, name, created_at, updated_at).
            order: Sort order (asc, desc).
            page: Page number (1-indexed).
            per_page: Results per page (max 100).
            min_stars: Minimum star count filter.
            topics: List of topics to filter by.

        Returns:
            List of repositories.
        """
        params = {
            "search": query,
            "order_by": sort,
            "sort": order,
            "page": page,
            "per_page": min(per_page, 100),
            "star_count": f">={min_stars}" if min_stars > 0 else None,
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Add topic filters
        if topics:
            params["topic"] = ",".join(topics)

        data = await self._request("/projects", params)

        if isinstance(data, list):
            return [self._parse_project(item) for item in data]
        return []

    async def search_projects_concurrent(
        self,
        query: str,
        max_pages: int = 5,
        per_page: int = 100,
        sort: str = "star_count",
        order: str = "desc",
        max_concurrent: int = 5,
        min_stars: int = 0,
        topics: Optional[list[str]] = None,
    ) -> list[Repository]:
        """Search projects concurrently across multiple pages.

        Args:
            query: Search query.
            max_pages: Maximum number of pages to fetch.
            per_page: Results per page (max 100).
            sort: Sort field.
            order: Sort order (asc, desc).
            max_concurrent: Maximum concurrent requests.
            min_stars: Minimum star count filter.
            topics: List of topics to filter by.

        Returns:
            List of repositories from all pages.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_page(page: int) -> list[Repository]:
            async with semaphore:
                params = {
                    "search": query,
                    "order_by": sort,
                    "sort": order,
                    "page": page,
                    "per_page": min(per_page, 100),
                }

                if min_stars > 0:
                    params["star_count"] = f">={min_stars}"

                if topics:
                    params["topic"] = ",".join(topics)

                try:
                    data = await self._request("/projects", params)
                    if isinstance(data, list):
                        return [self._parse_project(item) for item in data]
                    return []
                except GitLabAPIError as e:
                    logger.warning(f"Page {page} fetch failed: {e}")
                    return []

        # Create tasks for all pages
        tasks = [fetch_page(page) for page in range(1, max_pages + 1)]

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results, skipping exceptions
        all_repos = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Page fetch failed: {result}")
                continue
            all_repos.extend(result)

        return all_repos

    async def get_project(self, project_id: int | str) -> Repository:
        """Get a single project.

        Args:
            project_id: Project ID or URL-encoded path (e.g., "group/project").

        Returns:
            Repository data.
        """
        data = await self._request(f"/projects/{project_id}")
        return self._parse_project(data)

    async def get_project_languages(self, project_id: int | str) -> dict[str, float]:
        """Get languages used in a project.

        Args:
            project_id: Project ID.

        Returns:
            Dictionary of language -> percentage.
        """
        data = await self._request(f"/projects/{project_id}/languages")
        return data if isinstance(data, dict) else {}

    async def get_trending_projects(
        self,
        since: str = "weekly",
        page: int = 1,
        per_page: int = 100,
    ) -> list[Repository]:
        """Get trending projects.

        Args:
            since: Time period (daily, weekly, monthly).
            page: Page number.
            per_page: Results per page.

        Returns:
            List of trending repositories.
        """
        params = {
            "order_by": "star_count",
            "sort": "desc",
            "page": page,
            "per_page": min(per_page, 100),
        }

        # GitLab doesn't have a direct trending endpoint,
        # so we get recently updated popular projects
        data = await self._request("/projects", params)

        if isinstance(data, list):
            return [self._parse_project(item) for item in data]
        return []

    async def get_group_projects(
        self,
        group_id: int | str,
        include_subgroups: bool = True,
        page: int = 1,
        per_page: int = 100,
    ) -> list[Repository]:
        """Get projects in a group.

        Args:
            group_id: Group ID or path.
            include_subgroups: Include projects from subgroups.
            page: Page number.
            per_page: Results per page.

        Returns:
            List of repositories in the group.
        """
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "include_subgroups": str(include_subgroups).lower(),
        }

        data = await self._request(f"/groups/{group_id}/projects", params)

        if isinstance(data, list):
            return [self._parse_project(item) for item in data]
        return []

    def _parse_project(self, data: dict) -> Repository:
        """Parse project data from API response.

        Args:
            data: API response data.

        Returns:
            Repository object.
        """
        # GitLab uses different field names than GitHub
        return Repository(
            id=data["id"],
            name=data.get("path_with_namespace", data.get("name", "")),
            full_name=data.get("path_with_namespace", data.get("name", "")),
            description=data.get("description"),
            stars=data.get("star_count", 0),
            language=self._get_primary_language(data),
            topics=data.get("topics", []) or data.get("tag_list", []),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("last_activity_at")),
            pushed_at=self._parse_datetime(data.get("last_activity_at")),
            url=data.get("web_url", ""),
            open_issues=data.get("open_issues_count"),
            forks=data.get("forks_count"),
        )

    def _get_primary_language(self, data: dict) -> Optional[str]:
        """Get primary language from project data.

        Args:
            data: Project data.

        Returns:
            Primary language name or None.
        """
        # GitLab may provide languages in different places
        languages = data.get("languages", {})
        if languages:
            # Return the language with highest percentage
            return max(languages.keys(), key=lambda k: languages[k]) if languages else None

        # Fallback to repository_language if available
        return data.get("repository_language")

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string.

        Args:
            value: ISO datetime string.

        Returns:
            datetime object or None.
        """
        if not value:
            return None

        # Handle ISO format with Z suffix
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        try:
            return datetime.fromisoformat(value.replace("+00:00", ""))
        except ValueError:
            return None
