# AI Scraper Plugins

This directory contains example plugins for AI Scraper.

## Creating a Plugin

1. Create a Python file in this directory
2. Import `BasePlugin` and `PluginInfo` from `ai_scraper.plugins`
3. Create a class that inherits from `BasePlugin`
4. Implement the `info` property
5. Override any hook methods you need

## Available Hooks

| Hook | Description |
|------|-------------|
| `on_scrape_start(config)` | Called when scraping starts |
| `on_repo_found(repo)` | Called for each repository found. Return modified repo or None to filter |
| `on_scrape_complete(repos, stats)` | Called when scraping completes |
| `on_export(data, format)` | Called before export. Return modified data |

## Example

```python
from ai_scraper.plugins import BasePlugin, PluginInfo

class MyPlugin(BasePlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin",
        )

    def on_repo_found(self, repo):
        # Filter out repos with fewer than 100 stars
        if repo.stars < 100:
            return None
        return repo
```

## Loading Plugins

```bash
# Load a specific plugin
ai-scraper scrape --plugin plugins/my_plugin.py

# Load all plugins from directory
ai-scraper scrape --plugin-dir plugins/
```
