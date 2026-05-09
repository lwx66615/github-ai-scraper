"""Tests for CLI."""

from click.testing import CliRunner

from ai_scraper.cli import cli


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
