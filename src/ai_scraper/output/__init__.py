"""Output module for generating reports."""

from ai_scraper.output.html import HTMLExporter
from ai_scraper.output.markdown import MarkdownExporter

__all__ = ["HTMLExporter", "MarkdownExporter"]
