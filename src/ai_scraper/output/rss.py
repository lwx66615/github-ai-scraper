"""RSS exporter for generating feed subscriptions."""

from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from ai_scraper.models import Repository


class RSSExporter:
    """Export repositories to RSS feed format."""

    def __init__(self, output_dir: Path, filename: str = "repositories.xml"):
        """Initialize the exporter.

        Args:
            output_dir: Directory for output files.
            filename: Name of the output file.
        """
        self.output_dir = Path(output_dir)
        self.filename = filename

    def export_repositories(
        self,
        repos: list[Repository],
        title: str = "AI Repositories Feed",
        description: str = "Latest AI repositories from GitHub",
    ) -> Path:
        """Export repositories to an RSS feed.

        Args:
            repos: List of repositories to export.
            title: Feed title.
            description: Feed description.

        Returns:
            Path to the created file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create RSS structure
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")

        # Channel info
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "link").text = "https://github.com/topics/ai"
        ET.SubElement(channel, "language").text = "en-us"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Add items
        for repo in repos:
            item = ET.SubElement(channel, "item")

            ET.SubElement(item, "title").text = repo.full_name
            ET.SubElement(item, "link").text = repo.url
            ET.SubElement(item, "description").text = repo.description or "No description"
            ET.SubElement(item, "pubDate").text = (
                repo.updated_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
                if repo.updated_at
                else ""
            )

            # Custom elements
            ET.SubElement(item, "stars").text = str(repo.stars)
            if repo.language:
                ET.SubElement(item, "language").text = repo.language

        # Write to file
        output_path = self.output_dir / self.filename

        # Pretty print
        ET.indent(rss, space="  ")
        tree = ET.ElementTree(rss)

        with open(output_path, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)

        return output_path
