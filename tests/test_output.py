"""Tests for Markdown output module."""

from datetime import datetime
from pathlib import Path
import tempfile

from ai_scraper.models import Repository
from ai_scraper.output import MarkdownExporter
from ai_scraper.output.translator import translate_description


def test_translate_preserves_proper_nouns():
    """Proper nouns and technical terms should not be partially translated."""
    result = translate_description("Your own personal AI assistant. Any OS. Any Platform.")

    assert "个人 AI 助手" in result or "AI 助手" in result
    assert "代理ic" not in result


def test_translate_handles_technical_terms():
    """Technical terms should be translated naturally."""
    result = translate_description("A production-ready platform for LLM applications.")

    assert "生产就绪" in result
    assert "大语言模型" in result or "LLM" in result


def test_translate_avoids_awkward_partial_translation():
    """Awkward partial translations should be avoided."""
    result = translate_description("The agent that grows with you")

    assert len(result) > 0
    assert "代理ic" not in result
    assert "开发ment" not in result


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

            assert "# 🤖 AI 开源项目精选" in content
            assert "更新时间" in content
            assert "项目数量" in content

    def test_export_includes_table_headers(self):
        """Export should include table headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "统计概览" in content
            assert "语言分布" in content
            assert "Stars" in content
            assert "标签" in content

    def test_export_includes_repository_data(self):
        """Export should include repository data in table."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir)
            repos = [create_test_repo(name="explosion/spaCy", stars=33557, description="Industrial-strength NLP")]

            result_path = exporter.export_repositories(repos)
            content = result_path.read_text(encoding="utf-8")

            assert "explosion/spaCy" in content
            assert "33.6K" in content
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

            assert "| " in content and " | 3 | " in content
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
            result = exporter._clean_description(long_text, max_len=50)

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
            assert result == "暂无描述"

    def test_custom_filename(self):
        """Should support custom filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            exporter = MarkdownExporter(output_dir, filename="custom.md")
            repos = [create_test_repo()]

            result_path = exporter.export_repositories(repos)

            assert result_path.name == "custom.md"
