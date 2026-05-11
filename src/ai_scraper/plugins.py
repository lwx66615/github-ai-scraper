"""Plugin system for ai-scraper."""

import importlib.util
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ai_scraper.models.repository import Repository


@dataclass
class PluginInfo:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: Optional[str] = None


class BasePlugin(ABC):
    """Base class for plugins."""

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Get plugin information."""
        pass

    def on_scrape_start(self, config: dict) -> None:
        """Called when scraping starts."""
        pass

    def on_repo_found(self, repo: Repository) -> Optional[Repository]:
        """Called when a repository is found. Can modify or filter.

        Args:
            repo: Found repository.

        Returns:
            Modified repository or None to filter out.
        """
        return repo

    def on_scrape_complete(self, repos: list[Repository], stats: dict) -> None:
        """Called when scraping completes."""
        pass

    def on_export(self, data: Any, format: str) -> Any:
        """Called before export. Can modify data.

        Args:
            data: Data to export.
            format: Export format.

        Returns:
            Modified data.
        """
        return data


class PluginManager:
    """Manage loaded plugins."""

    def __init__(self):
        self.plugins: dict[str, BasePlugin] = {}

    def load_plugin(self, plugin_path: Path) -> Optional[str]:
        """Load a plugin from a Python file.

        Args:
            plugin_path: Path to plugin file.

        Returns:
            Plugin name if loaded successfully.
        """
        try:
            spec = importlib.util.spec_from_file_location("custom_plugin", plugin_path)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin = attr()
                    self.plugins[plugin.info.name] = plugin
                    return plugin.info.name

            return None
        except Exception as e:
            print(f"Failed to load plugin: {e}")
            return None

    def load_plugins_from_dir(self, plugin_dir: Path) -> list[str]:
        """Load all plugins from a directory.

        Args:
            plugin_dir: Directory containing plugin files.

        Returns:
            List of loaded plugin names.
        """
        loaded = []
        for plugin_file in plugin_dir.glob("*.py"):
            name = self.load_plugin(plugin_file)
            if name:
                loaded.append(name)
        return loaded

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(name)

    def trigger(self, event: str, *args, **kwargs) -> Any:
        """Trigger an event on all plugins.

        Args:
            event: Event name (e.g., "on_repo_found").
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Modified result from plugin chain.
        """
        result = args[0] if args else None

        for plugin in self.plugins.values():
            handler = getattr(plugin, event, None)
            if handler:
                try:
                    if result is not None:
                        result = handler(result, **kwargs)
                    else:
                        handler(*args, **kwargs)
                except Exception as e:
                    print(f"Plugin {plugin.info.name} error in {event}: {e}")

        return result


# Global plugin manager
plugin_manager = PluginManager()
