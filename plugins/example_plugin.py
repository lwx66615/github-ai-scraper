"""Example plugin demonstrating the plugin system."""

from ai_scraper.plugins import BasePlugin, PluginInfo
from ai_scraper.models.repository import Repository


class ExamplePlugin(BasePlugin):
    """Example plugin that adds tags to repositories."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="example-plugin",
            version="1.0.0",
            description="Example plugin that demonstrates plugin capabilities",
            author="AI Scraper Team",
        )

    def on_repo_found(self, repo: Repository) -> Repository:
        """Add 'verified' tag to high-star repositories."""
        if repo.stars >= 1000:
            if "verified" not in repo.topics:
                repo.topics.append("verified")
        return repo

    def on_scrape_complete(self, repos: list[Repository], stats: dict) -> None:
        """Log summary when scraping completes."""
        verified_count = sum(1 for r in repos if "verified" in r.topics)
        print(f"[Example Plugin] Verified {verified_count} high-star repositories")

    def on_export(self, data, format: str):
        """Add metadata to exports."""
        if hasattr(data, "__dict__"):
            data.plugin_processed = True
        return data
