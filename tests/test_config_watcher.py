"""Tests for configuration watcher."""

import pytest
from pathlib import Path
import tempfile
import time
from ai_scraper.config_watcher import ConfigWatcher


def test_config_watcher_detects_changes():
    """Test that config watcher detects file changes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text("github:\n  token: old_token\n")

        changes_detected = []

        def on_change(path):
            changes_detected.append(path)

        watcher = ConfigWatcher(config_path, on_change)
        watcher.start()

        # Modify the file
        time.sleep(0.5)
        config_path.write_text("github:\n  token: new_token\n")

        # Wait for detection
        time.sleep(2)

        watcher.stop()

        assert len(changes_detected) > 0


def test_config_watcher_stop():
    """Test that watcher can be stopped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text("test: value\n")

        watcher = ConfigWatcher(config_path, lambda p: None)
        watcher.start()

        # Should be running
        assert watcher._running

        watcher.stop()

        # Should be stopped
        assert not watcher._running


def test_config_watcher_nonexistent_file():
    """Test watcher with nonexistent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "nonexistent.yaml"

        changes_detected = []

        def on_change(path):
            changes_detected.append(path)

        watcher = ConfigWatcher(config_path, on_change)
        watcher.start()

        time.sleep(1)

        watcher.stop()

        # Should not have detected changes
        assert len(changes_detected) == 0


def test_config_watcher_multiple_changes():
    """Test watcher detects multiple changes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text("version: 1\n")

        changes_detected = []

        def on_change(path):
            changes_detected.append(path)

        watcher = ConfigWatcher(config_path, on_change)
        watcher.start()

        # Make multiple changes
        time.sleep(0.5)
        config_path.write_text("version: 2\n")
        time.sleep(1.5)
        config_path.write_text("version: 3\n")
        time.sleep(1.5)

        watcher.stop()

        # Should detect at least one change
        assert len(changes_detected) >= 1