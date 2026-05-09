"""Markdown exporter for generating reports."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_scraper.models import Repository


class MarkdownExporter:
    """Export repositories to Markdown format."""

    def __init__(self, output_dir: Path, filename: str = "repositories.md"):
        """Initialize the exporter.

        Args:
            output_dir: Directory for output files.
            filename: Name of the output file.
        """
        self.output_dir = Path(output_dir)
        self.filename = filename

    def export_repositories(self, repos: list[Repository]) -> Path:
        """Export repositories to a Markdown file.

        Args:
            repos: List of repositories to export.

        Returns:
            Path to the created file.
        """
        # Create output directory if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate content
        content = self._generate_content(repos)

        # Write file
        output_path = self.output_dir / self.filename
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def _generate_content(self, repos: list[Repository]) -> str:
        """Generate the full Markdown content."""
        lines = []

        # Header
        lines.append("# AI Repositories")
        lines.append("")

        # Metadata
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"**更新时间:** {now}")
        lines.append(f"**总计:** {len(repos)} 个仓库")
        lines.append("")

        # Table
        lines.append(self._format_table(repos))

        return "\n".join(lines)

    def _format_table(self, repos: list[Repository]) -> str:
        """Format repositories as a Markdown table.

        Args:
            repos: List of repositories.

        Returns:
            Markdown table string.
        """
        lines = []

        # Table header
        lines.append("| Name | Stars | Language | Description | URL |")
        lines.append("|------|-------|----------|-------------|-----|")

        # Table rows
        for repo in repos:
            name = repo.full_name
            stars = f"{repo.stars:,}"
            language = repo.language or ""
            description = self._clean_description(repo.description)
            url = f"[GitHub]({repo.url})"

            lines.append(f"| {name} | {stars} | {language} | {description} | {url} |")

        return "\n".join(lines)

    def _clean_description(self, description: Optional[str]) -> str:
        """Clean description for table cell.

        - Remove newlines and extra spaces
        - Truncate to 50 chars (add "..." if truncated)
        - Escape pipe characters

        Args:
            description: Original description.

        Returns:
            Cleaned description.
        """
        if description is None:
            return ""

        # Remove newlines and collapse spaces
        cleaned = " ".join(description.split())

        # Escape pipe characters
        cleaned = cleaned.replace("|", r"\|")

        # Truncate to 50 chars
        if len(cleaned) > 50:
            cleaned = cleaned[:50] + "..."

        return cleaned
