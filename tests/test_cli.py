"""Tests for CLI."""

from datetime import datetime, timedelta

from click.testing import CliRunner

from ai_scraper.cli import cli, parse_since_param


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "GitHub AI" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_config_show():
    """Test config show command."""
    runner = CliRunner()

    result = runner.invoke(cli, ["config", "show"])

    assert result.exit_code == 0
    assert "Min Stars" in result.output


def test_db_stats_no_database():
    """Test db stats command when no database exists."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["db", "stats"])

        assert result.exit_code == 0
        assert "No database found" in result.output


def test_list_no_database():
    """Test list command when no database exists."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No database found" in result.output


def test_trending_no_database():
    """Test trending command when no database exists."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["trending"])

        assert result.exit_code == 0
        assert "No database found" in result.output


class TestParseSinceParam:
    """Tests for parse_since_param helper function."""

    def test_parse_none_returns_none(self):
        """Test that None input returns None."""
        result = parse_since_param(None)
        assert result is None

    def test_parse_yyyy_mm_dd_format(self):
        """Test parsing YYYY-MM-DD format."""
        result = parse_since_param("2024-05-01")

        assert result is not None
        assert result.year == 2024
        assert result.month == 5
        assert result.day == 1

    def test_parse_relative_days(self):
        """Test parsing relative days format (e.g., '7d')."""
        result = parse_since_param("7d")

        assert result is not None
        expected = datetime.now() - timedelta(days=7)
        # Allow 1 minute tolerance for test execution time
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_parse_relative_weeks(self):
        """Test parsing relative weeks format (e.g., '1w')."""
        result = parse_since_param("1w")

        assert result is not None
        expected = datetime.now() - timedelta(weeks=1)
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_parse_relative_months(self):
        """Test parsing relative months format (e.g., '1m')."""
        result = parse_since_param("1m")

        assert result is not None
        expected = datetime.now() - timedelta(days=30)
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_parse_relative_years(self):
        """Test parsing relative years format (e.g., '1y')."""
        result = parse_since_param("1y")

        assert result is not None
        expected = datetime.now() - timedelta(days=365)
        diff = abs((result - expected).total_seconds())
        assert diff < 60

    def test_parse_case_insensitive(self):
        """Test that relative format is case-insensitive."""
        result_lower = parse_since_param("1d")
        result_upper = parse_since_param("1D")

        assert result_lower is not None
        assert result_upper is not None
        # Both should give approximately the same result
        diff = abs((result_lower - result_upper).total_seconds())
        assert diff < 1

    def test_parse_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        import pytest
        with pytest.raises(ValueError) as exc_info:
            parse_since_param("invalid")
        assert "Invalid --since format" in str(exc_info.value)

    def test_parse_multiple_digits(self):
        """Test parsing with multiple digits (e.g., '30d')."""
        result = parse_since_param("30d")

        assert result is not None
        expected = datetime.now() - timedelta(days=30)
        diff = abs((result - expected).total_seconds())
        assert diff < 60
