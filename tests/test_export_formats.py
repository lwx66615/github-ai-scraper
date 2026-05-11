"""Tests for export formats."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime
from ai_scraper.models.repository import Repository
from ai_scraper.output.excel import ExcelExporter
from ai_scraper.output.rss import RSSExporter


def test_excel_export():
    """Test Excel export format."""
    repos = [
        Repository(
            id=1,
            name="test/repo1",
            full_name="test/repo1",
            description="Test repo 1",
            stars=1000,
            language="Python",
            topics=["ai", "ml"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo1",
        ),
        Repository(
            id=2,
            name="test/repo2",
            full_name="test/repo2",
            description="Test repo 2",
            stars=500,
            language="Go",
            topics=["llm"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo2",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = ExcelExporter(Path(tmpdir))
        output_path = exporter.export_repositories(repos)

        assert output_path.exists()
        assert output_path.suffix == ".xlsx"
        assert output_path.stat().st_size > 0


def test_rss_export():
    """Test RSS export format."""
    repos = [
        Repository(
            id=1,
            name="test/repo1",
            full_name="test/repo1",
            description="Test repo 1",
            stars=1000,
            language="Python",
            topics=["ai"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo1",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = RSSExporter(Path(tmpdir))
        output_path = exporter.export_repositories(repos)

        assert output_path.exists()
        assert output_path.suffix == ".xml"

        content = output_path.read_text(encoding="utf-8")
        assert "<?xml version=" in content
        assert "<rss" in content
        assert "test/repo1" in content


def test_rss_export_structure():
    """Test RSS export has correct structure."""
    repos = [
        Repository(
            id=1,
            name="test/repo1",
            full_name="test/repo1",
            description="Test description",
            stars=500,
            language="Python",
            topics=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pushed_at=datetime.now(),
            url="https://github.com/test/repo1",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = RSSExporter(Path(tmpdir))
        output_path = exporter.export_repositories(repos)

        content = output_path.read_text(encoding="utf-8")

        # Check RSS structure
        assert "<channel>" in content
        assert "<item>" in content
        assert "<title>test/repo1</title>" in content
        assert "<stars>500</stars>" in content


def test_excel_export_empty_repos():
    """Test Excel export with empty repository list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = ExcelExporter(Path(tmpdir))
        output_path = exporter.export_repositories([])

        assert output_path.exists()


def test_rss_export_empty_repos():
    """Test RSS export with empty repository list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = RSSExporter(Path(tmpdir))
        output_path = exporter.export_repositories([])

        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert "<?xml version=" in content
        assert "<rss" in content
