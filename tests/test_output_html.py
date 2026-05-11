"""Tests for HTML output module."""

from datetime import datetime
from pathlib import Path
import tempfile

from ai_scraper.models import Repository
from ai_scraper.output.html import HTMLExporter


def create_test_repo(
    name: str = "test/repo",
    stars: int = 100,
    language: str = "Python",
    description: str = "Test repository",
    url: str = None,
) -> Repository:
    """Create a test repository."""
    return Repository(
        id=1,
        name=name.split("/")[-1],
        full_name=name,
        description=description,
        stars=stars,
        language=language,
        topics=["ai", "machine-learning"],
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2024, 1, 1),
        pushed_at=datetime(2024, 1, 1),
        url=url if url else f"https://github.com/{name}",
    )


class TestHTMLExporter:
    """Tests for HTMLExporter class."""

    def test_export_creates_output_directory(self):
        """Export should create the output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nonexistent" / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert output_dir.exists()
            assert result_path.parent == output_dir

    def test_export_creates_html_file(self):
        """Export should create an .html file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert result_path.exists()
            assert result_path.suffix == ".html"
            assert result_path.name == "index.html"

    def test_export_includes_html_structure(self):
        """Export should include proper HTML structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<!DOCTYPE html>" in content
            assert "<html" in content
            assert "<head>" in content
            assert "<body>" in content
            assert "</html>" in content

    def test_export_includes_title_and_header(self):
        """Export should include title and header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<title>AI Repositories</title>" in content
            assert "<h1>AI Repositories</h1>" in content

    def test_export_includes_metadata(self):
        """Export should include update time and total count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "Updated:" in content
            assert "Total: 1 repositories" in content

    def test_export_includes_stats_section(self):
        """Export should include statistics section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [
                create_test_repo(name="repo1/test", stars=100),
                create_test_repo(name="repo2/test", stars=200),
            ]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "Repositories" in content
            assert "Total Stars" in content
            assert "2" in content  # repo count
            assert "300" in content  # total stars

    def test_export_includes_table_headers(self):
        """Export should include table headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<th>Name</th>" in content
            assert "<th>Stars</th>" in content
            assert "<th>Language</th>" in content
            assert "<th>Description</th>" in content

    def test_export_includes_repository_data(self):
        """Export should include repository data in table."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name="explosion/spaCy", stars=33557, description="Industrial-strength NLP")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "explosion/spaCy" in content
            assert "33,557" in content
            assert "Python" in content
            assert "Industrial-strength NLP" in content
            assert "https://github.com/explosion/spaCy" in content

    def test_export_links_open_in_new_tab(self):
        """Export links should open in new tab."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name="test/repo")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert 'target="_blank"' in content
            assert 'href="https://github.com/test/repo"' in content

    def test_export_links_have_noopener_noreferrer(self):
        """Export links should have rel="noopener noreferrer" for security."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name="test/repo")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert 'rel="noopener noreferrer"' in content

    def test_export_handles_multiple_repos(self):
        """Export should handle multiple repositories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [
                create_test_repo(name="repo1/test", stars=100),
                create_test_repo(name="repo2/test", stars=200),
                create_test_repo(name="repo3/test", stars=300),
            ]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "repo1/test" in content
            assert "repo2/test" in content
            assert "repo3/test" in content
            assert "Total: 3 repositories" in content

    def test_export_handles_empty_repos_list(self):
        """Export should handle empty repository list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = []

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<!DOCTYPE html>" in content
            assert "Total: 0 repositories" in content

    def test_clean_description_escapes_html(self):
        """Clean description should escape HTML characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            result = exporter._clean_description("Text with <script>alert('xss')</script>")
            assert result == "Text with &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"

    def test_clean_description_truncates_long_text(self):
        """Clean description should truncate to 100 chars with ellipsis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            long_text = "This is a very long description that should be truncated because it exceeds the limit of one hundred characters"
            result = exporter._clean_description(long_text)

            assert len(result) == 100
            assert result.endswith("...")
            assert result.startswith("This is a very long")

    def test_clean_description_handles_none(self):
        """Clean description should handle None values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            result = exporter._clean_description(None)
            assert result == ""

    def test_custom_filename(self):
        """Should support custom filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir, filename="custom.html")
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert result_path.name == "custom.html"

    def test_custom_title(self):
        """Should support custom title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos, title="Custom Title")
            content = result_path.read_text(encoding="utf-8")

            assert "<title>Custom Title</title>" in content
            assert "<h1>Custom Title</h1>" in content

    def test_export_includes_responsive_css(self):
        """Export should include responsive CSS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "@media (max-width: 768px)" in content
            assert "<style>" in content

    def test_export_handles_missing_language(self):
        """Export should handle repositories without language."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(language=None)]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "-" in content  # Displayed as dash for missing language


class TestXSSProtection:
    """Tests for XSS vulnerability protection."""

    def test_script_tag_in_name_is_escaped(self):
        """Script tags in repository name should be escaped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name="<script>alert('xss')</script>/repo")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            # The script tag should be escaped, not interpreted as HTML
            assert "<script>" not in content
            assert "&lt;script&gt;" in content
            assert "&#x27;xss&#x27;" in content  # Single quotes are also escaped

    def test_script_tag_in_description_is_escaped(self):
        """Script tags in description should be escaped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(description="<script>alert('xss')</script>")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<script>" not in content
            assert "&lt;script&gt;" in content

    def test_javascript_url_is_sanitized(self):
        """javascript: URLs should be sanitized to #."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(url="javascript:alert('xss')")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "javascript:" not in content
            assert 'href="#"' in content

    def test_data_url_is_sanitized(self):
        """data: URLs should be sanitized to #."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(url="data:text/html,<script>alert('xss')</script>")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "data:text/html" not in content
            assert 'href="#"' in content

    def test_ampersand_is_escaped(self):
        """Ampersand characters should be escaped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name="test/repo", description="A & B & C")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "&amp;" in content

    def test_quotes_are_escaped_in_attributes(self):
        """Quotes should be escaped in HTML attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(name='test/"onclick="alert(1)"')]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            # Quotes should be escaped
            assert "&quot;" in content
            assert 'onclick="alert(1)"' not in content

    def test_special_chars_in_language_are_escaped(self):
        """Special characters in language should be escaped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo(language="<script>Python</script>")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "<script>" not in content
            assert "&lt;script&gt;" in content

    def test_safe_url_escapes_quotes(self):
        """Safe URL should escape quotes to prevent attribute injection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            result = exporter._safe_url('https://example.com?foo=1&bar="test"')

            assert "&quot;" in result
            assert '"test"' not in result

    def test_safe_url_allows_http(self):
        """Safe URL should allow http:// URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            result = exporter._safe_url("http://example.com")

            assert result == "http://example.com"

    def test_safe_url_allows_https(self):
        """Safe URL should allow https:// URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)

            result = exporter._safe_url("https://example.com")

            assert result == "https://example.com"

    def test_title_with_html_is_escaped(self):
        """HTML in custom title should be escaped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = HTMLExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos, title="<script>alert('xss')</script>")
            content = result_path.read_text(encoding="utf-8")

            assert "<script>" not in content
            assert "&lt;script&gt;" in content
