# GitHub AI Scraper

A CLI tool for scraping AI-related high-star repositories from GitHub.

## Features

- Search and filter AI-related repositories by keywords and topics
- **Dynamic keyword extraction** - Automatically learns new keywords from scraped repos
- **Markdown/HTML report generation** - Generates readable reports
- **Incremental scraping** - Fetch only updated repos with `--since` flag
- **Progress bar display** - Visual progress during scraping
- **Interactive CLI mode** - Menu-driven interface for easy use
- Local SQLite storage with trend analysis
- Configurable filtering and scraping options
- Rate limiting with GitHub API token support
- Export to CSV/JSON/HTML formats
- **REST API server** - Access data via HTTP endpoints
- **Scheduled scraping** - Cron-based periodic scraping
- **Webhook notifications** - Notify external services on events
- **Plugin system** - Extend functionality with custom plugins

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Set your GitHub token (optional, increases rate limit)
export GITHUB_TOKEN=your_token_here

# Scrape AI repositories
ai-scraper scrape

# Scrape with progress bar
ai-scraper scrape --progress

# Incremental scraping (repos updated in last 7 days)
ai-scraper scrape --incremental
ai-scraper scrape --since 7d

# Interactive mode
ai-scraper interactive

# List scraped repositories
ai-scraper list

# Show trending repositories
ai-scraper trending

# Export data
ai-scraper db export --format html --output index.html

# Start REST API server
ai-scraper serve --port 8080

# Schedule periodic scraping (daily at 9am)
ai-scraper schedule --cron "0 9 * * *"
```

## Configuration

Create `ai-scraper.yaml` to customize:

```yaml
github:
  token: ${GITHUB_TOKEN}
  cache_ttl: 3600

filter:
  min_stars: 100
  keywords:
    - ai
    - machine-learning
  topics:
    - ai
    - deep-learning

scrape:
  max_results: 500
  concurrency: 5

database:
  path: ./data/ai_scraper.db

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
| `ai-scraper scrape --incremental` | Incremental scraping (only updated repos) |
| `ai-scraper scrape --since 7d` | Fetch repos updated in last 7 days |
| `ai-scraper scrape --progress` | Show progress bar during scraping |
| `ai-scraper interactive` | Start interactive menu mode |
| `ai-scraper list` | List scraped repositories |
| `ai-scraper trending` | Show trending repositories by star growth |
| `ai-scraper serve` | Start REST API server |
| `ai-scraper schedule` | Schedule periodic scraping |
| `ai-scraper keywords list` | List all keywords |
| `ai-scraper keywords extract` | Extract keywords from database |
| `ai-scraper keywords clear` | Clear keywords |
| `ai-scraper config init` | Initialize config file |
| `ai-scraper config show` | Show current config |
| `ai-scraper db stats` | Show database statistics |
| `ai-scraper db export` | Export data to CSV/JSON/HTML |

## REST API Endpoints

When running `ai-scraper serve`:

| Endpoint | Description |
|----------|-------------|
| `GET /api/repos` | List repositories with filters |
| `GET /api/repos/{id}` | Get specific repository |
| `GET /api/stats` | Get database statistics |
| `GET /api/trending` | Get trending repositories |
| `GET /api/search?q=...` | Search repositories |

## Project Structure

```
github-ai-scraper/
├── src/ai_scraper/
│   ├── cli.py              # CLI entry point
│   ├── config.py           # Configuration management
│   ├── interactive.py      # Interactive menu mode
│   ├── classifier.py       # Repository classification
│   ├── dedup.py            # Deduplication utilities
│   ├── scheduler.py        # Task scheduling
│   ├── webhooks.py         # Webhook notifications
│   ├── plugins.py          # Plugin system
│   ├── logging_config.py   # Logging configuration
│   ├── api_server.py       # REST API server
│   ├── api/
│   │   ├── github.py       # GitHub API client
│   │   └── rate_limiter.py # Token bucket rate limiter
│   ├── models/
│   │   └── repository.py   # Data models (Pydantic)
│   ├── filters/
│   │   └── ai_filter.py    # AI relevance filter
│   ├── output/
│   │   ├── markdown.py     # Markdown exporter
│   │   └ html.py           # HTML exporter
│   └── storage/
│       └── database.py     # SQLite storage
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