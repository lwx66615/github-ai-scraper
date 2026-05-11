"""Tests for example plugin."""

import pytest
from pathlib import Path
from datetime import datetime
from ai_scraper.plugin_system import PluginManager
from ai_scraper.models.repository import Repository


def test_load_example_plugin():
    """Test loading the example plugin."""
    manager = PluginManager()
    plugin_path = Path("plugins/example_plugin.py")

    if not plugin_path.exists():
        pytest.skip("Example plugin not found")

    name = manager.load_plugin(plugin_path)
    assert name is not None
    assert name == "example-plugin"


def test_example_plugin_modifies_repo():
    """Test that example plugin can modify repositories."""
    manager = PluginManager()
    plugin_path = Path("plugins/example_plugin.py")

    if not plugin_path.exists():
        pytest.skip("Example plugin not found")

    manager.load_plugin(plugin_path)

    repo = Repository(
        id=1,
        name="test/repo",
        full_name="test/repo",
        description="Test",
        stars=1000,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/repo",
    )

    result = manager.trigger("on_repo_found", repo)

    # Plugin should add verified tag for high-star repos
    assert result is not None
    assert "verified" in result.topics


def test_example_plugin_skips_low_star_repo():
    """Test that example plugin doesn't modify low-star repos."""
    manager = PluginManager()
    plugin_path = Path("plugins/example_plugin.py")

    if not plugin_path.exists():
        pytest.skip("Example plugin not found")

    manager.load_plugin(plugin_path)

    repo = Repository(
        id=1,
        name="test/repo",
        full_name="test/repo",
        description="Test",
        stars=100,  # Low stars
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/repo",
    )

    result = manager.trigger("on_repo_found", repo)

    # Plugin should not add verified tag for low-star repos
    assert result is not None
    assert "verified" not in result.topics


def test_example_plugin_info():
    """Test example plugin info."""
    manager = PluginManager()
    plugin_path = Path("plugins/example_plugin.py")

    if not plugin_path.exists():
        pytest.skip("Example plugin not found")

    manager.load_plugin(plugin_path)

    plugin = manager.get_plugin("example-plugin")
    assert plugin is not None
    assert plugin.info.name == "example-plugin"
    assert plugin.info.version == "1.0.0"