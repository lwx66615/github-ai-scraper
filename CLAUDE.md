# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Requirement

**任何情况下，都使用中文进行交流和回复。** 无论用户使用何种语言提问，都必须使用中文回答。

## Project Overview

GitHub/GitLab AI Scraper is a CLI tool for scraping AI-related high-star repositories from GitHub and GitLab. It supports multi-platform scraping, dynamic keyword extraction, multiple export formats, and a REST API server.

## Common Commands

### Development Setup
```bash
pip install -e ".[dev]"   # Install with dev dependencies
```

### Testing
```bash
pytest tests/ -v          # Run all tests
pytest tests/test_models.py -v  # Run single test file
pytest -k "repository" -v      # Run tests matching pattern
```

### CLI Usage
```bash
ai-scraper scrape                    # Scrape from GitHub (default)
ai-scraper scrape --platform gitlab  # Scrape from GitLab
ai-scraper scrape --gitlab-url https://your-gitlab.com/api/v4  # Self-hosted GitLab
ai-scraper scrape --incremental      # Only updated repos
ai-scraper scrape --since 7d         # Repos updated in last 7 days
ai-scraper scrape --progress         # Show progress bar
ai-scraper list                      # List scraped repos
ai-scraper trending                  # Show trending repos
ai-scraper serve --port 8080         # Start REST API server
ai-scraper keywords list             # List keywords
ai-scraper db export --format markdown --output repositories.md
ai-scraper db clean --invalid        # Remove invalid repos
ai-scraper db clean --vacuum         # Optimize database
ai-scraper config show               # Show current config
```

### Environment Variables
```bash
export GITHUB_TOKEN=your_token  # Increases rate limit to 5000/hour
export GITLAB_TOKEN=your_token  # For GitLab scraping
```

## Architecture

### Core Data Flow
1. **API Clients** (`src/ai_scraper/api/`) - Async HTTP clients for GitHub/GitLab with rate limiting and caching
2. **Filter** (`src/ai_scraper/filters/ai_filter.py`) - Determines if repos are AI-related and scores relevance
3. **Classifier** (`src/ai_scraper/classifier.py`) - Categorizes repos into AI subdomains (LLM, CV, NLP, MLOps, etc.)
4. **Database** (`src/ai_scraper/storage/database.py`) - SQLite storage with snapshot-based trend tracking
5. **Output** (`src/ai_scraper/output/`) - Exporters for Markdown, HTML, Excel, RSS formats

### Key Components

**Repository Model** (`src/ai_scraper/models/repository.py`)
- Pydantic models: `Repository`, `RepoSnapshot`, `FilterConfig`, `ScrapeConfig`
- URL pattern supports both GitHub and GitLab: `^https?://[\w\.-]+/[\w\-\.]+/[\w\-\.]+`

**API Clients** (`src/ai_scraper/api/`)
- `GitHubClient` and `GitLabClient` share similar async patterns
- Both use `RateLimiter` (token bucket) and optional `RequestCache`
- Connection pooling via `aiohttp.TCPConnector`

**Keyword Extraction** (`src/ai_scraper/keywords/extractor.py`)
- Extracts keywords from repo topics, descriptions, and names
- Filters stopwords, requires min 2 chars, excludes pure digits
- Merges with existing keywords respecting `max_keywords` limit

**Configuration** (`src/ai_scraper/config.py`)
- YAML-based config loaded from `ai-scraper.yaml`
- Environment variable substitution: `${GITHUB_TOKEN}` syntax
- Separate configs for GitHub, GitLab, filter, scrape, database, keywords, output, webhooks

### CLI Structure (`src/ai_scraper/cli.py`)
- Uses Click with grouped commands: `scrape`, `list`, `trending`, `serve`, `schedule`, `interactive`
- Sub-groups: `config`, `db`, `keywords`
- Progress bar via Rich library
- Windows UTF-8 handling with `clean_text()` function

## Platform Support

Both GitHub and GitLab are supported with platform-specific clients:
- GitHub: `GitHubClient` with search query syntax `stars:>100 topic:ai pushed:>YYYY-MM-DD`
- GitLab: `GitLabClient` with simpler search, configurable `base_url` for self-hosted instances

## Export Formats

Located in `src/ai_scraper/output/`:
- `markdown.py` - Markdown with Chinese translation, category grouping, language icons
- `html.py` - HTML with responsive styling
- `excel.py` - Excel workbook format
- `rss.py` - RSS feed format
- `translator.py` - Description translation support

## Database Schema

SQLite tables in `data/ai_scraper.db`:
- `repositories` - Main repo data with relevance scores, timestamps
- `snapshots` - Star count snapshots for trend analysis

Indexes on: stars, last_updated_at, language, created_at, relevance_score, snapshot_at