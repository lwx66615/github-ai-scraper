# GitHub/GitLab AI Scraper

English | [简体中文](README_CN.md)

A CLI tool for scraping AI-related high-star repositories from GitHub and GitLab.

## Features

- **Multi-platform support** - Scrape from GitHub or GitLab (including self-hosted instances)
- Search and filter AI-related repositories by keywords and topics
- **Dynamic keyword extraction** - Automatically learns new keywords from scraped repos
- **Markdown/HTML/Excel/RSS report generation** - Multiple export formats with Chinese translation
- **Incremental scraping** - Fetch only updated repos with `--since` flag
- **Resume support** - Continue interrupted scrapes with progress tracking
- **Progress bar display** - Visual progress during scraping
- **Interactive CLI mode** - Menu-driven interface for easy use
- **Concurrent scraping** - Parallel requests for faster results
- **Multi-language search** - Support for Chinese and English keywords
- Local SQLite storage with trend analysis
- Configurable filtering and scraping options
- Rate limiting with GitHub/GitLab API token support
- Export to CSV/JSON/HTML/Excel/RSS/Markdown formats
- **REST API server** - Access data via HTTP endpoints with optional authentication
- **Scheduled scraping** - Cron-based periodic scraping
- **Webhook notifications** - Notify external services on events
- **Plugin system** - Extend functionality with custom plugins
- **Repository health assessment** - Activity, popularity, maintenance scores
- **Intelligent classification** - LLM, CV, NLP, MLOps, AI Infrastructure categories
- **Deduplication** - Fork and mirror detection, content similarity
- **Secure token storage** - Encrypted storage for sensitive tokens
- **Database backup** - Automatic backup and restore functionality
- **Error recovery** - Retry logic with exponential backoff

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Set your GitHub token (optional, increases rate limit)
export GITHUB_TOKEN=your_token_here

# Scrape AI repositories from GitHub (default)
ai-scraper scrape

# Scrape from GitLab
ai-scraper scrape --platform gitlab

# Scrape from self-hosted GitLab
ai-scraper scrape --platform gitlab --gitlab-url https://your-gitlab.com/api/v4

# Scrape with progress bar
ai-scraper scrape --progress

# Concurrent scraping (faster)
ai-scraper scrape --concurrent

# Incremental scraping (repos updated in last 7 days)
ai-scraper scrape --incremental
ai-scraper scrape --since 7d

# Resume interrupted scrape
ai-scraper scrape --resume

# Interactive mode
ai-scraper interactive

# List scraped repositories
ai-scraper list

# Show trending repositories
ai-scraper trending

# Export data
ai-scraper db export --format html --output index.html
ai-scraper db export --format xlsx --output repos.xlsx
ai-scraper db export --format rss --output feed.xml
ai-scraper db export --format markdown --output repositories.md

# Start REST API server (with authentication)
ai-scraper serve --port 8080 --auth

# Schedule periodic scraping (daily at 9am)
ai-scraper schedule --cron "0 9 * * *"

# Backup database
ai-scraper db backup
ai-scraper db restore backup_file.db.gz
```

## Configuration

Create `ai-scraper.yaml` to customize:

```yaml
github:
  token: ${GITHUB_TOKEN}
  cache_ttl: 3600

gitlab:
  token: ${GITLAB_TOKEN}  # Optional, for GitLab scraping
  base_url: https://gitlab.com/api/v4  # Or your self-hosted GitLab URL
  cache_ttl: 3600

filter:
  min_stars: 100
  keywords:
    - ai
    - machine-learning
    - 人工智能  # Chinese keyword support
  topics:
    - ai
    - deep-learning

scrape:
  max_results: 500
  concurrency: 5
  concurrent_requests: 5

database:
  path: ./data/ai_scraper.db
  backup_dir: ./backups
  max_backups: 10

api:
  auth_enabled: true
  api_keys:
    - as_your_api_key_here

webhooks:
  enabled: false
  endpoints:
    - url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
      events: [scrape_complete, trending_found]
```

## Commands

| Command | Description |
|---------|-------------|
| `ai-scraper scrape` | Scrape AI repositories from GitHub |
| `ai-scraper scrape --platform gitlab` | Scrape from GitLab |
| `ai-scraper scrape --platform gitlab --gitlab-url URL` | Scrape from self-hosted GitLab |
| `ai-scraper scrape --concurrent` | Concurrent scraping for faster results |
| `ai-scraper scrape --incremental` | Incremental scraping (only updated repos) |
| `ai-scraper scrape --since 7d` | Fetch repos updated in last 7 days |
| `ai-scraper scrape --resume` | Resume interrupted scrape |
| `ai-scraper scrape --progress` | Show progress bar during scraping |
| `ai-scraper interactive` | Start interactive menu mode |
| `ai-scraper list` | List scraped repositories |
| `ai-scraper trending` | Show trending repositories by star growth |
| `ai-scraper serve` | Start REST API server |
| `ai-scraper serve --auth` | Start API server with authentication |
| `ai-scraper schedule` | Schedule periodic scraping |
| `ai-scraper keywords list` | List all keywords |
| `ai-scraper keywords extract` | Extract keywords from database |
| `ai-scraper keywords clear` | Clear keywords |
| `ai-scraper config init` | Initialize config file |
| `ai-scraper config show` | Show current config |
| `ai-scraper db stats` | Show database statistics |
| `ai-scraper db export` | Export data to CSV/JSON/HTML/Excel/RSS |
| `ai-scraper db clean --invalid` | Remove repositories with invalid data |
| `ai-scraper db clean --vacuum` | Optimize database size |
| `ai-scraper db backup` | Create database backup |
| `ai-scraper db restore` | Restore from backup |
| `ai-scraper db backups` | List available backups |

## REST API Endpoints

When running `ai-scraper serve`:

| Endpoint | Description |
|----------|-------------|
| `GET /api/repos` | List repositories with filters |
| `GET /api/repos/{id}` | Get specific repository |
| `GET /api/stats` | Get database statistics |
| `GET /api/trending` | Get trending repositories |
| `GET /api/search?q=...` | Search repositories |

Authentication: Pass `X-API-Key` header when `--auth` is enabled.

## Project Structure

```
github-ai-scraper/
├── src/ai_scraper/
│   ├── cli.py              # CLI entry point
│   ├── config.py           # Configuration management
│   ├── interactive.py      # Interactive menu mode
│   ├── classifier.py       # Repository classification
│   ├── dedup.py            # Deduplication utilities
│   ├── health.py           # Health assessment
│   ├── scheduler.py        # Task scheduling
│   ├── webhooks.py         # Webhook notifications
│   ├── plugins.py          # Plugin system
│   ├── logging_config.py   # Logging configuration
│   ├── api_server.py       # REST API server
│   ├── auth.py             # API authentication
│   ├── retry.py            # Error recovery
│   ├── i18n.py             # Multi-language support
│   ├── scrape_progress.py  # Resume support
│   ├── backup.py           # Database backup
│   ├── config_watcher.py   # Config hot reload
│   ├── secure_storage.py   # Token encryption
│   ├── api/
│   │   ├── github.py       # GitHub API client
│   │   └── rate_limiter.py # Token bucket rate limiter
│   ├── models/
│   │   └── repository.py   # Data models (Pydantic)
│   ├── filters/
│   │   └── ai_filter.py    # AI relevance filter
│   ├── output/
│   │   ├── markdown.py     # Markdown exporter
│   │   ├── html.py         # HTML exporter
│   │   ├── excel.py        # Excel exporter
│   │   └── rss.py          # RSS exporter
│   └── storage/
│       ├── database.py     # SQLite storage (sync)
│       └── async_database.py # SQLite storage (async)
├── plugins/                # Example plugins
├── tests/                  # Test suite
├── Dockerfile              # Docker support
├── docker-compose.yml      # Docker compose
├── .github/workflows/      # CI/CD workflows
└── ai-scraper.yaml         # Default configuration
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t ai-scraper .
```

## API Rate Limits

- Without token: 60 requests/hour
- With token: 5000 requests/hour

Set `GITHUB_TOKEN` environment variable for higher limits.

## License

MIT