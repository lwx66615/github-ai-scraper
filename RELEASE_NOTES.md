# Release Notes for v0.1.0

## GitHub/GitLab AI Scraper

A CLI tool for discovering and scraping AI-related high-star repositories from GitHub and GitLab.

### Key Features

- **Ready to Use** - Install with `pip install ai-scraper` and start scraping immediately
- **AI-Focused** - Intelligent filtering and classification for AI repositories (LLM, CV, NLP, MLOps, etc.)
- **Automation Ready** - Scheduled scraping, webhook notifications, and trend analysis

### Highlights

- Multi-platform support: GitHub and GitLab (including self-hosted)
- Dynamic keyword extraction from scraped repositories
- Multiple export formats: Markdown, HTML, Excel, RSS
- Interactive CLI mode for easy navigation
- REST API server with optional authentication
- Repository health assessment and deduplication

### Installation

```bash
pip install ai-scraper
```

### Quick Start

```bash
# Set your GitHub token (optional, increases rate limit)
export GITHUB_TOKEN=your_token_here

# Scrape AI repositories
ai-scraper scrape

# Show trending repositories
ai-scraper trending

# Export to Markdown
ai-scraper db export --format markdown --output repos.md
```

### What's Next

- More AI classification categories
- Enhanced trend analysis
- Web UI interface

---

**Full Changelog**: https://github.com/lwx66615/github-ai-scraper/commits/v0.1.0
