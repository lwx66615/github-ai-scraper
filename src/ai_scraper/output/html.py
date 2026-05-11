"""HTML exporter for generating web reports."""

from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from typing import Optional

from ai_scraper.models import Repository


class HTMLExporter:
    """Export repositories to HTML format."""

    def __init__(self, output_dir: Path, filename: str = "index.html"):
        """Initialize the exporter.

        Args:
            output_dir: Directory for output files.
            filename: Name of the output file.
        """
        self.output_dir = Path(output_dir)
        self.filename = filename

    def export_repositories(self, repos: list[Repository], title: str = "AI Repositories") -> Path:
        """Export repositories to an HTML file.

        Args:
            repos: List of repositories to export.
            title: Page title.

        Returns:
            Path to the created file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        content = self._generate_html(repos, title)

        output_path = self.output_dir / self.filename
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def _generate_html(self, repos: list[Repository], title: str) -> str:
        """Generate full HTML content."""
        # Escape title to prevent XSS
        safe_title = html_escape(title)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f6f8fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #24292f; margin-bottom: 10px; }}
        .meta {{ color: #57606a; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
        .stat-box {{ background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #0969da; }}
        .stat-label {{ color: #57606a; font-size: 14px; }}
        table {{ width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #f6f8fa; padding: 12px 16px; text-align: left; font-weight: 600; color: #24292f; }}
        td {{ padding: 12px 16px; border-top: 1px solid #d0d7de; }}
        tr:hover {{ background: #f6f8fa; }}
        a {{ color: #0969da; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .stars {{ color: #e3b341; }}
        .language {{ background: #ddf4ff; color: #0969da; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
        .description {{ color: #57606a; }}
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            table {{ font-size: 14px; }}
            th, td {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{safe_title}</h1>
        <p class="meta">Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Total: {len(repos)} repositories</p>

        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(repos)}</div>
                <div class="stat-label">Repositories</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{sum(r.stars for r in repos):,}</div>
                <div class="stat-label">Total Stars</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Stars</th>
                    <th>Language</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
{self._generate_rows(repos)}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    def _generate_rows(self, repos: list[Repository]) -> str:
        """Generate table rows."""
        rows = []
        for repo in repos:
            # Escape all user-controlled data to prevent XSS
            safe_url = self._safe_url(repo.url)
            safe_name = html_escape(repo.full_name, quote=True)
            safe_language = html_escape(repo.language or "-", quote=True)
            safe_description = self._clean_description(repo.description)

            rows.append(f"""                <tr>
                    <td><a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_name}</a></td>
                    <td><span class="stars">★ {repo.stars:,}</span></td>
                    <td><span class="language">{safe_language}</span></td>
                    <td class="description">{safe_description}</td>
                </tr>""")
        return "\n".join(rows)

    def _safe_url(self, url: str) -> str:
        """Validate and escape URL to prevent XSS.

        Only allows http:// and https:// URLs.
        Returns '#' for invalid URLs.
        """
        safe_url = html_escape(url, quote=True)
        if safe_url.startswith(('http://', 'https://')):
            return safe_url
        return '#'

    def _clean_description(self, description: Optional[str]) -> str:
        """Clean description for HTML.

        Escapes HTML characters and truncates to 100 chars with ellipsis.
        """
        if not description:
            return ""
        escaped = html_escape(description, quote=True)
        if len(escaped) > 100:
            return escaped[:97] + "..."
        return escaped
