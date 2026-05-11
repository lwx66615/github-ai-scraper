"""Configuration file watcher for hot reload."""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ConfigWatcher:
    """Watch configuration file for changes."""

    def __init__(
        self,
        config_path: Path,
        on_change: Callable[[Path], None],
        poll_interval: float = 1.0,
    ):
        """Initialize config watcher.

        Args:
            config_path: Path to configuration file.
            on_change: Callback when file changes.
            poll_interval: Polling interval in seconds.
        """
        self.config_path = Path(config_path)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: Optional[float] = None

    def start(self) -> None:
        """Start watching for changes."""
        if self._running:
            return

        self._running = True
        self._last_mtime = self._get_mtime()

        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

        logger.info(f"Started watching {self.config_path}")

    def stop(self) -> None:
        """Stop watching for changes."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        logger.info("Stopped config watcher")

    def _get_mtime(self) -> Optional[float]:
        """Get file modification time."""
        try:
            return self.config_path.stat().st_mtime
        except FileNotFoundError:
            return None

    def _watch_loop(self) -> None:
        """Main watch loop."""
        while self._running:
            try:
                current_mtime = self._get_mtime()

                if current_mtime is not None and current_mtime != self._last_mtime:
                    logger.info(f"Config file changed: {self.config_path}")
                    self._last_mtime = current_mtime
                    try:
                        self.on_change(self.config_path)
                    except Exception as e:
                        logger.error(f"Error in on_change callback: {e}")

                time.sleep(self.poll_interval)

            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                time.sleep(self.poll_interval)
