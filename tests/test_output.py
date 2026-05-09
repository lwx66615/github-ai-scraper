"""Tests for Markdown output module."""

from datetime import datetime
from pathlib import Path
import tempfile

from ai_scraper.models import Repository
from ai_scraper.output import MarkdownExporter


def create_test_repo(
    name: str = "test/repo",
    stars: int = 100,
    language: str = "Python",
    description: str = "Test repository",
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
        url=f"https://github.com/{name}",
    )


class TestMarkdownExporter:
    """Tests for MarkdownExporter class."""

    def test_export_creates_output_directory(self):
        """Export should create the output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nonexistent" / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert output_dir.exists()
            assert result_path.parent == output_dir

    def test_export_creates_md_file(self):
        """Export should create a .md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert result_path.exists()
            assert result_path.suffix == ".md"
            assert result_path.name == "repositories.md"

    def test_export_includes_headers(self):
        """Export should include document headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "# AI Repositories" in content
            assert "**更新时间:**" in content
            assert "**总计:**" in content

    def test_export_includes_table_headers(self):
        """Export should include table headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "| Name |" in content
            assert "| Stars |" in content
            assert "| Language |" in content
            assert "| Description |" in content
            assert "| URL |" in content

    def test_export_includes_repository_data(self):
        """Export should include repository data in table."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo(name="explosion/spaCy", stars=33557, description="Industrial-strength NLP")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "explosion/spaCy" in content
            assert "33,557" in content
            assert "Python" in content
            assert "Industrial-strength NLP" in content
            assert "https://github.com/explosion/spaCy" in content

    def test_export_handles_multiple_repos(self):
        """Export should handle multiple repositories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [
                create_test_repo(name="repo1/test", stars=100),
                create_test_repo(name="repo2/test", stars=200),
                create_test_repo(name="repo3/test", stars=300),
            ]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "**总计:** 3 个仓库" in content
            assert "repo1/test" in content
            assert "repo2/test" in content
            assert "repo3/test" in content

    def test_clean_description_removes_newlines(self):
        """Clean description should remove newlines and extra spaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)

            result = exporter._clean_description("Line 1\nLine 2  Line 3")
            assert result == "Line 1 Line 2 Line 3"

    def test_clean_description_truncates_long_text(self):
        """Clean description should truncate to 50 chars with ellipsis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)

            long_text = "This is a very long description that should be truncated because it exceeds the limit"
            result = exporter._clean_description(long_text)

            assert len(result) == 53  # 50 chars + "..."
            assert result.endswith("...")

    def test_clean_description_escapes_pipes(self):
        """Clean description should escape pipe characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)

            result = exporter._clean_description("Text with | pipe")
            assert result == r"Text with \| pipe"

    def test_clean_description_handles_none(self):
        """Clean description should handle None values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)

            result = exporter._clean_description(None)
            assert result == ""

    def test_custom_filename(self):
        """Should support custom filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir, filename="custom.md")
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert result_path.name == "custom.md"
