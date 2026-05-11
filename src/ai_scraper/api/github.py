"""GitHub API client."""

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


class GitHubAPIError(Exception):
    """GitHub API error."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"GitHub API error {status}: {message}")


class GitHubClient:
    """Asynchronous GitHub API client."""

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub Personal Access Token (optional).
            cache_dir: Directory for cache files (optional).
            cache_ttl: Cache time-to-live in seconds.
        """
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None

        # Rate limiter: 60/hour without token, 5000/hour with token
        rate = 5000 if token else 60
        self.rate_limiter = RateLimiter(requests_per_hour=rate)

        # Request cache
        self.cache: Optional[RequestCache] = None
        if cache_dir:
            self.cache = RequestCache(cache_dir=cache_dir, ttl=cache_ttl)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make an API request.

        Args:
            endpoint: API endpoint (without base URL).
            params: Query parameters.

        Returns:
            JSON response data.

        Raises:
            GitHubAPIError: On API errors.
        """
        url = f"{self.BASE_URL}{endpoint}"

        # Check cache first
        if self.cache:
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

        async with session.get(url, params=params) as response:
            if response.status == 401:
                raise GitHubAPIError(401, "Unauthorized - check your token")
            elif response.status == 403:
                # Rate limited
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                raise GitHubAPIError(403, f"Rate limited, resets at {reset_time}")
            elif response.status == 503:
                raise GitHubAPIError(503, "Service unavailable")
            elif response.status >= 400:
                text = await response.text()
                raise GitHubAPIError(response.status, text)

            data = await response.json()

            # Cache successful response
            if self.cache:
                self.cache.set(url, params, data)
                logger.debug(f"Cached response for {endpoint}")

            return data

    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        page: int = 1,
        per_page: int = 100,
    ) -> list[Repository]:
        """Search repositories.

        Args:
            query: Search query.
            sort: Sort field (stars, forks, updated).
            order: Sort order (asc, desc).
            page: Page number.
            per_page: Results per page (max 100).

        Returns:
            List of repositories.
        """
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100),
        }

        data = await self._request("/search/repositories", params)
        items = data.get("items", [])

        return [self._parse_repository(item) for item in items]

    async def search_repositories_concurrent(
        self,
        query: str,
        max_pages: int = 5,
        per_page: int = 100,
        sort: str = "stars",
        order: str = "desc",
        max_concurrent: int = 5,
    ) -> list[Repository]:
        """Search repositories concurrently across multiple pages.

        Args:
            query: Search query.
            max_pages: Maximum number of pages to fetch.
            per_page: Results per page (max 100).
            sort: Sort field (stars, forks, updated).
            order: Sort order (asc, desc).
            max_concurrent: Maximum concurrent requests.

        Returns:
            List of repositories from all pages.
        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_page(page: int) -> list[Repository]:
            async with semaphore:
                params = {
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "page": page,
                    "per_page": min(per_page, 100),
                }
                data = await self._request("/search/repositories", params)
                items = data.get("items", [])
                return [self._parse_repository(item) for item in items]

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

    async def get_repository(self, owner: str, repo: str) -> Repository:
        """Get a single repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository data.
        """
        data = await self._request(f"/repos/{owner}/{repo}")
        return self._parse_repository(data)

    async def get_contributors(self, owner: str, repo: str) -> int:
        """Get contributor count for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Number of contributors.
        """
        try:
            # GitHub doesn't provide count directly, so we fetch first page
            data = await self._request(
                f"/repos/{owner}/{repo}/contributors",
                params={"per_page": 1, "anon": "true"}
            )

            # Check Link header for total count
            session = await self._get_session()
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"

            async with session.get(url, params={"per_page": 1}) as response:
                link_header = response.headers.get("Link", "")
                # Parse last page number from Link header
                if 'rel="last"' in link_header:
                    # Extract page number from last link
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))

                # Fallback: return length of current page
                return len(data)
        except GitHubAPIError:
            return 0

    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit information.
        """
        data = await self._request("/rate_limit")

        resources = data.get("resources", {})
        search = resources.get("search", {})
        core = resources.get("core", {})

        return RateLimitInfo(
            search_limit=search.get("limit", 0),
            search_remaining=search.get("remaining", 0),
            search_reset=search.get("reset", 0),
            core_limit=core.get("limit", 0),
            core_remaining=core.get("remaining", 0),
            core_reset=core.get("reset", 0),
        )

    def _parse_repository(self, data: dict) -> Repository:
        """Parse repository data from API response.

        Args:
            data: API response data.

        Returns:
            Repository object.
        """
        return Repository(
            id=data["id"],
            name=data["full_name"],
            full_name=data["full_name"],
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
            pushed_at=self._parse_datetime(data.get("pushed_at")),
            url=data.get("html_url", ""),
            open_issues=data.get("open_issues_count"),
            forks=data.get("forks_count"),
        )

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
