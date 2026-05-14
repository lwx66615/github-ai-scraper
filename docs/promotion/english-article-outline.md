# English Article Outline

## Title
Discover Trending AI Projects on GitHub with ai-scraper

## I. The Problem (150 words)
- Finding quality AI repositories is time-consuming
- GitHub trending is too broad, not AI-specific
- Hard to track projects over time
- No automated way to discover new projects

## II. What is ai-scraper? (100 words)
- A CLI tool for scraping AI-related repositories
- Supports both GitHub and GitLab
- Open source, MIT licensed
- Key stats: stars, activity, classification

## III. Key Features (400 words)

### Ready to Use
- Simple installation: `pip install ai-scraper`
- Interactive mode for beginners
- No complex setup required

### AI-Focused
- Intelligent filtering for AI repositories
- Auto-classification: LLM, CV, NLP, MLOps, AI Infrastructure
- Dynamic keyword extraction

### Automation Ready
- Scheduled scraping with cron
- Webhook notifications
- Trend analysis and star growth tracking

## IV. Quick Start (200 words)

```bash
# Install
pip install ai-scraper

# Basic usage
ai-scraper scrape              # Scrape AI repos
ai-scraper trending            # Show trending repos
ai-scraper list                # List all repos
```

## V. Advanced Usage (300 words)

### Incremental Scraping
```bash
ai-scraper scrape --incremental
ai-scraper scrape --since 7d
```

### REST API Server
```bash
ai-scraper serve --port 8080
# Access at http://localhost:8080/api/repos
```

### Export Options
```bash
ai-scraper db export --format markdown --output repos.md
ai-scraper db export --format html --output index.html
ai-scraper db export --format xlsx --output repos.xlsx
```

## VI. Use Cases (150 words)
- Personal learning: Track AI frontier projects
- Team sharing: Generate weekly reports
- Research: Discover projects in specific domains
- Content creation: Find trending topics

## VII. Call to Action (50 words)
- GitHub: https://github.com/lwx66615/github-ai-scraper
- Stars, Issues, and PRs welcome!
- Actively maintained

## Suggested Images
1. CLI screenshot with progress bar
2. Markdown report sample
3. Trending repos output
