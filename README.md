# GitHub AI Scraper

A CLI tool for scraping AI-related high-star repositories from GitHub.

## Features

- Search and filter AI-related repositories by keywords and topics
- **Dynamic keyword extraction** - Automatically learns new keywords from scraped repos
- **Markdown report generation** - Generates readable reports in `output/repositories.md`
- Local SQLite storage with trend analysis
- Configurable filtering and scraping options
- Rate limiting with GitHub API token support
- Export to CSV/JSON formats

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

# List scraped repositories
ai-scraper list

# Show trending repositories
ai-scraper trending

# Export data
ai-scraper db export --format csv --output repos.csv
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
```

## Commands

| Command | Description |
|---------|-------------|
| `ai-scraper scrape` | Scrape AI repositories from GitHub |
| `ai-scraper list` | List scraped repositories |
| `ai-scraper trending` | Show trending repositories by star growth |
| `ai-scraper keywords list` | List all keywords |
| `ai-scraper keywords extract` | Extract keywords from database |
| `ai-scraper keywords clear` | Clear keywords |
| `ai-scraper config init` | Initialize config file |
| `ai-scraper config show` | Show current config |
| `ai-scraper db stats` | Show database statistics |
| `ai-scraper db export` | Export data to CSV/JSON |

## Project Structure

```
github-ai-scraper/
├── src/ai_scraper/
│   ├── cli.py           # CLI entry point
│   ├── config.py        # Configuration management
│   ├── api/
│   │   ├── github.py    # GitHub API client
│   │   └── rate_limiter.py  # Token bucket rate limiter
│   ├── models/
│   │   └── repository.py    # Data models
│   ├── filters/
│   │   └── ai_filter.py     # AI relevance filter
│   └── storage/
│       └── database.py      # SQLite storage
├── cmd/scheduler/       # Go scheduler (optional)
├── tests/               # Test suite
└── ai-scraper.yaml      # Default configuration
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Build Go scheduler (requires Go 1.21+)
cd cmd/scheduler && go build
```

## API Rate Limits

- Without token: 60 requests/hour
- With token: 5000 requests/hour

Set `GITHUB_TOKEN` environment variable for higher limits.

## License

MIT
