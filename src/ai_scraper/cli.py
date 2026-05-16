"""CLI entry point for ai-scraper."""

import asyncio
import io
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
import rich.table as table
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ai_scraper import __version__
from ai_scraper.api.github import GitHubClient
from ai_scraper.api.gitlab import GitLabClient
from ai_scraper.config import Config, load_config
from ai_scraper.filters.ai_filter import AIFilter
from ai_scraper.keywords.extractor import KeywordExtractor
from ai_scraper.models.repository import FilterConfig as FilterConfigModel
from ai_scraper.output.markdown import MarkdownExporter
from ai_scraper.storage.database import Database

# Create console with UTF-8 encoding for Windows
# Use a wrapper to ensure UTF-8 encoding for output
if sys.platform == "win32":
    # Reconfigure stdout for UTF-8 if needed
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass
console = Console(force_terminal=True, legacy_windows=False)


def clean_text(text: str) -> str:
    """Remove emoji and special characters that can't be displayed in Windows terminal."""
    if not text:
        return ""
    # Remove emoji, zero-width joiners, and other non-printable characters
    # Keep only ASCII and common Unicode letters/numbers/punctuation
    result = []
    for char in text:
        # Keep ASCII printable characters and common Unicode ranges
        if (32 <= ord(char) <= 126 or  # ASCII printable
            '\u4e00' <= char <= '\u9fff' or  # Chinese characters
            '\u0400' <= char <= '\u04ff' or  # Cyrillic
            char in ' \t'):  # Basic whitespace
            result.append(char)
        elif char in '\n\r':
            result.append(' ')
    return ''.join(result)


def parse_since_param(since: Optional[str]) -> Optional[datetime]:
    """Parse the --since parameter into a datetime.

    Args:
        since: Either YYYY-MM-DD format or relative like '1d', '1w', '1m'.

    Returns:
        datetime representing the cutoff time, or None if since is None.

    Raises:
        ValueError: If the format is invalid.
    """
    if since is None:
        return None

    # Try YYYY-MM-DD format first
    if re.match(r'^\d{4}-\d{2}-\d{2}$', since):
        return datetime.strptime(since, '%Y-%m-%d')

    # Try relative format: number + unit (d, w, m)
    match = re.match(r'^(\d+)([dwmy])$', since.lower())
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit == 'd':
            return datetime.now() - timedelta(days=amount)
        elif unit == 'w':
            return datetime.now() - timedelta(weeks=amount)
        elif unit == 'm':
            return datetime.now() - timedelta(days=amount * 30)
        elif unit == 'y':
            return datetime.now() - timedelta(days=amount * 365)

    raise ValueError(
        f"Invalid --since format: '{since}'. "
        "Use YYYY-MM-DD or relative format like '1d', '1w', '1m', '1y'."
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]):
    """GitHub AI high-star repositories scraper."""
    ctx.ensure_object(dict)

    config_path = Path(config) if config else Path("ai-scraper.yaml")
    ctx.obj["config"] = load_config(config_path)
    ctx.obj["config_path"] = config_path


@cli.command()
@click.option("--min-stars", type=int, help="Minimum stars filter")
@click.option("--max-results", type=int, help="Maximum results to fetch")
@click.option("--incremental", is_flag=True, help="Only fetch repos updated since last scrape")
@click.option("--since", type=str, help="Fetch repos updated since date (YYYY-MM-DD or 1d/1w/1m)")
@click.option("--progress/--no-progress", default=True, help="Show progress bar (default: on)")
@click.option("--platform", type=click.Choice(["github", "gitlab"]), default="github", help="Platform to scrape (github or gitlab)")
@click.option("--gitlab-url", type=str, help="GitLab instance URL (for self-hosted GitLab)")
@click.pass_context
def scrape(ctx: click.Context, min_stars: Optional[int], max_results: Optional[int],
           incremental: bool, since: Optional[str], progress: bool, platform: str, gitlab_url: Optional[str]):
    """Scrape AI repositories from GitHub or GitLab."""
    config: Config = ctx.obj["config"]

    # Override config with CLI options
    if min_stars is not None:
        config.filter.min_stars = min_stars
    if max_results is not None:
        config.scrape.max_results = max_results

    # Parse --since parameter
    since_date: Optional[datetime] = None
    if since:
        try:
            since_date = parse_since_param(since)
            console.print(f"[dim]Fetching repos updated since: {since_date}[/dim]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    console.print(f"[bold blue]Starting scrape from {platform}...[/bold blue]")

    async def run_scrape(since_date_inner: Optional[datetime]):
        # Create appropriate client based on platform
        if platform == "gitlab":
            client = GitLabClient(
                token=config.gitlab.token or config.github.token,
                base_url=gitlab_url or config.gitlab.base_url
            )
        else:
            client = GitHubClient(token=config.github.token)

        db = Database(Path(config.database.path))
        db.init_db()
        filter_instance = AIFilter()
        keyword_extractor = KeywordExtractor(
            Path(config.keywords.file),
            max_keywords=config.keywords.max_keywords
        )
        markdown_exporter = MarkdownExporter(
            Path(config.output.dir),
            filename=config.output.filename
        )

        try:
            # Handle incremental mode
            if incremental and since_date_inner is None:
                last_scrape = db.get_last_scrape_time()
                if last_scrape:
                    since_date_inner = last_scrape
                    if not progress:
                        console.print(f"[dim]Incremental mode: fetching repos since last scrape ({last_scrape})[/dim]")
                else:
                    if not progress:
                        console.print("[dim]Incremental mode: no previous scrape found, fetching all repos[/dim]")

            # Build search query based on platform
            primary_topic = config.filter.topics[0] if config.filter.topics else "ai"

            if platform == "gitlab":
                # GitLab uses different search syntax
                query = "ai"  # GitLab search is simpler
                if not progress:
                    console.print(f"[dim]Searching GitLab for: {query}[/dim]")
            else:
                # GitHub search
                query = f"stars:>{config.filter.min_stars} topic:{primary_topic}"
                if since_date_inner:
                    date_str = since_date_inner.strftime('%Y-%m-%d')
                    query += f" pushed:>{date_str}"
                if not progress:
                    console.print(f"[dim]Query: {query}[/dim]")

            # Search repositories
            all_repos = []
            page = 1
            per_page = min(100, config.scrape.max_results)
            max_results = config.scrape.max_results

            if progress:
                # Use progress bar
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress_bar:
                    task = progress_bar.add_task(
                        f"[cyan]Scraping {platform} repositories...",
                        total=max_results
                    )

                    while len(all_repos) < max_results:
                        # Use appropriate search method based on platform
                        if platform == "gitlab":
                            repos = await client.search_projects(
                                query=query,
                                sort="star_count",
                                order="desc",
                                page=page,
                                per_page=per_page,
                                min_stars=config.filter.min_stars,
                            )
                        else:
                            repos = await client.search_repositories(
                                query=query,
                                sort="stars",
                                order="desc",
                                page=page,
                                per_page=per_page,
                            )

                        if not repos:
                            break

                        # Filter AI-related repos
                        filter_config = FilterConfigModel(
                            keywords=config.filter.keywords,
                            topics=config.filter.topics,
                            languages=config.filter.languages,
                            exclude_keywords=config.filter.exclude_keywords,
                            min_stars=config.filter.min_stars,
                        )

                        for repo in repos:
                            if len(all_repos) >= max_results:
                                break  # 达到限制，停止添加
                            if filter_instance.is_ai_related(repo, filter_config):
                                score = filter_instance.score_relevance(repo)
                                db.save_repository(repo, relevance_score=score)
                                # Save snapshot for trend analysis
                                db.save_snapshot(repo.id, repo.stars, datetime.now())
                                all_repos.append(repo)
                                progress_bar.update(task, completed=len(all_repos))

                        # 检查是否达到限制
                        if len(all_repos) >= max_results:
                            break

                        page += 1

                        if len(repos) < per_page:
                            break

                    # Ensure progress shows final count
                    progress_bar.update(task, completed=len(all_repos))
            else:
                # No progress bar - use original console output
                while len(all_repos) < max_results:
                    if platform == "gitlab":
                        repos = await client.search_projects(
                            query=query,
                            sort="star_count",
                            order="desc",
                            page=page,
                            per_page=per_page,
                            min_stars=config.filter.min_stars,
                        )
                    else:
                        repos = await client.search_repositories(
                            query=query,
                            sort="stars",
                            order="desc",
                            page=page,
                            per_page=per_page,
                        )

                    if not repos:
                        break

                    # Filter AI-related repos
                    filter_config = FilterConfigModel(
                        keywords=config.filter.keywords,
                        topics=config.filter.topics,
                        languages=config.filter.languages,
                        exclude_keywords=config.filter.exclude_keywords,
                        min_stars=config.filter.min_stars,
                    )

                    for repo in repos:
                        if len(all_repos) >= max_results:
                            break  # 达到限制，停止添加
                        if filter_instance.is_ai_related(repo, filter_config):
                            score = filter_instance.score_relevance(repo)
                            db.save_repository(repo, relevance_score=score)
                            # Save snapshot for trend analysis
                            db.save_snapshot(repo.id, repo.stars, datetime.now())
                            all_repos.append(repo)

                    # 检查是否达到限制
                    if len(all_repos) >= max_results:
                        break

                    console.print(f"[dim]Page {page}: found {len(repos)} repos, {len(all_repos)} total AI-related[/dim]")
                    page += 1

                    if len(repos) < per_page:
                        break

            if all_repos:
                console.print("[dim]Extracting keywords...[/dim]")
                existing_keywords = keyword_extractor.load_keywords()
                new_keywords = keyword_extractor.extract_from_repos(all_repos)
                merged = keyword_extractor.merge_keywords(existing_keywords, new_keywords)
                keyword_extractor.save_keywords(merged)
                console.print(f"[dim]Keywords updated: {len(merged)} total[/dim]")

                console.print("[dim]Generating Markdown report...[/dim]")
                output_path = markdown_exporter.export_repositories(all_repos)
                console.print(f"[dim]Report saved to: {output_path}[/dim]")

            console.print(f"[bold green]Scraped {len(all_repos)} AI repositories[/bold green]")

        finally:
            await client.close()
            db.close()

    asyncio.run(run_scrape(since_date))


@cli.command("list")
@click.option("--sort", type=click.Choice(["stars", "updated", "relevance"]), default="stars")
@click.option("--lang", type=str, help="Filter by language")
@click.option("--limit", type=int, default=20, help="Number of results")
@click.pass_context
def list_repos(ctx: click.Context, sort: str, lang: Optional[str], limit: int):
    """List scraped repositories."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    repos = db.get_all_repositories(limit=limit, sort_by=sort)

    # Filter by language if specified
    if lang:
        repos = [r for r in repos if r.language and r.language.lower() == lang.lower()]

    # Create table
    tbl = table.Table(title=f"AI Repositories (sorted by {sort})")
    tbl.add_column("Name", style="cyan")
    tbl.add_column("Stars", justify="right", style="yellow")
    tbl.add_column("Language", style="green")
    tbl.add_column("Description", max_width=40)

    for repo in repos:
        stars_str = f"{repo.stars:,}"
        desc = clean_text(repo.description)
        desc = desc[:37] + "..." if desc and len(desc) > 40 else desc or ""
        tbl.add_row(repo.name, stars_str, repo.language or "-", desc)

    console.print(tbl)
    db.close()


@cli.command()
@click.option("--days", type=int, default=7, help="Days to analyze")
@click.option("--top", type=int, default=10, help="Number of top results")
@click.pass_context
def trending(ctx: click.Context, days: int, top: int):
    """Show trending repositories by star growth."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    trends = db.get_trending(days=days, limit=top)

    if not trends:
        console.print(f"[yellow]No trending data found for the last {days} days.[/yellow]")
        console.print("[dim]Run 'ai-scraper scrape' multiple times to build trend data.[/dim]")
        db.close()
        return

    tbl = table.Table(title=f"Trending Repositories (last {days} days)")
    tbl.add_column("Repository", style="cyan")
    tbl.add_column("Growth", justify="right", style="green")
    tbl.add_column("Stars", justify="right", style="yellow")

    for trend in trends:
        growth_str = f"+{trend.growth_rate * 100:.1f}%"
        stars_str = f"{trend.current_stars:,}"
        tbl.add_row(trend.repo_name, growth_str, stars_str)

    console.print(tbl)
    db.close()


@cli.group()
def config_cmd():
    """Configuration management."""
    pass


@config_cmd.command("init")
@click.pass_context
def config_init(ctx: click.Context):
    """Initialize configuration file."""
    config_path: Path = ctx.obj["config_path"]

    if config_path.exists():
        console.print(f"[yellow]Config file already exists at {config_path}[/yellow]")
        return

    # Copy default config
    import shutil
    default_config = Path(__file__).parent.parent.parent / "ai-scraper.yaml"

    if default_config.exists():
        shutil.copy(default_config, config_path)
        console.print(f"[green]Created config file at {config_path}[/green]")
    else:
        console.print("[red]Default config not found[/red]")


@config_cmd.command("show")
@click.pass_context
def config_show(ctx: click.Context):
    """Show current configuration."""
    config: Config = ctx.obj["config"]

    console.print("[bold]Current Configuration:[/bold]")
    console.print(f"  GitHub Token: {'***' if config.github.token else 'Not set'}")
    console.print(f"  GitLab Token: {'***' if config.gitlab.token else 'Not set'}")
    console.print(f"  GitLab URL: {config.gitlab.base_url}")
    console.print(f"  Cache TTL: {config.github.cache_ttl}s")
    console.print(f"  Min Stars: {config.filter.min_stars}")
    console.print(f"  Keywords: {', '.join(config.filter.keywords[:5])}...")
    console.print(f"  Topics: {', '.join(config.filter.topics[:5])}...")
    console.print(f"  Max Results: {config.scrape.max_results}")
    console.print(f"  Database: {config.database.path}")
    console.print(f"  Scheduler: {'enabled' if config.scheduler.enabled else 'disabled'}")


cli.add_command(config_cmd, name="config")


@cli.group()
def db_cmd():
    """Database management."""
    pass


@db_cmd.command("stats")
@click.pass_context
def db_stats(ctx: click.Context):
    """Show database statistics."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    stats = db.get_stats()

    console.print("[bold]Database Statistics:[/bold]")
    console.print(f"  Repository count: {stats['repository_count']}")
    console.print(f"  Snapshot count: {stats['snapshot_count']}")
    console.print(f"  Total stars: {stats['total_stars']:,}")

    db.close()


@db_cmd.command("clean")
@click.option("--days", type=int, default=30, help="Keep snapshots from last N days")
@click.option("--invalid", is_flag=True, help="Remove repos with invalid data")
@click.option("--vacuum", is_flag=True, help="Optimize database size")
@click.pass_context
def db_clean(ctx: click.Context, days: int, invalid: bool, vacuum: bool):
    """Clean and optimize database.

    Examples:
        ai-scraper db clean --days 30        # Clean old snapshots
        ai-scraper db clean --invalid        # Remove invalid repos
        ai-scraper db clean --vacuum         # Optimize database
        ai-scraper db clean --invalid --vacuum  # Both
    """
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found.[/yellow]")
        return

    db.init_db()

    # Clean old snapshots (default behavior)
    if not invalid and not vacuum:
        deleted = db.clean_old_snapshots(days=days)
        console.print(f"[green]Deleted {deleted} old snapshots[/green]")

    # Remove invalid repos
    if invalid:
        removed = db.clean_invalid_repos()
        console.print(f"[green]Removed {removed} invalid repositories[/green]")

    # Optimize database
    if vacuum:
        db.vacuum()
        console.print("[green]Database optimized[/green]")

    db.close()


@db_cmd.command("export")
@click.option("--format", "-f", type=click.Choice(["csv", "json", "html", "markdown"]), default="csv")
@click.option("--output", "-o", type=click.Path(), default="export.csv")
@click.pass_context
def db_export(ctx: click.Context, format: str, output: str):
    """Export database to file."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        console.print("[yellow]No database found.[/yellow]")
        return

    db.init_db()
    repos = db.get_all_repositories(limit=10000)

    if format == "csv":
        import csv

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "stars", "language", "description", "url"])

            for repo in repos:
                writer.writerow([
                    repo.name,
                    repo.stars,
                    repo.language or "",
                    repo.description or "",
                    repo.url,
                ])

        console.print(f"[green]Exported {len(repos)} repositories to {output}[/green]")

    elif format == "json":
        import json

        data = {
            "repositories": [
                {
                    "name": r.name,
                    "stars": r.stars,
                    "language": r.language,
                    "description": r.description,
                    "url": r.url,
                }
                for r in repos
            ],
            "total": len(repos),
        }

        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        console.print(f"[green]Exported {len(repos)} repositories to {output}[/green]")

    elif format == "html":
        from ai_scraper.output.html import HTMLExporter
        exporter = HTMLExporter(Path(config.output.dir), filename=output)
        path = exporter.export_repositories(repos)
        console.print(f"[green]Exported {len(repos)} repositories to {path}[/green]")

    elif format == "markdown":
        from ai_scraper.output.markdown import MarkdownExporter
        exporter = MarkdownExporter(Path(config.output.dir), filename=output)
        path = exporter.export_repositories(repos)
        console.print(f"[green]Exported {len(repos)} repositories to {path}[/green]")

    db.close()


cli.add_command(db_cmd, name="db")


@cli.group()
def keywords_cmd():
    """Keywords management."""
    pass


@keywords_cmd.command("list")
@click.pass_context
def keywords_list(ctx: click.Context):
    """List all keywords."""
    config: Config = ctx.obj["config"]
    extractor = KeywordExtractor(Path(config.keywords.file))
    keywords = extractor.get_keywords_for_search()
    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return
    console.print(f"[bold]Keywords ({len(keywords)}):[/bold]")
    for kw in sorted(keywords):
        console.print(f"  {kw}")


@keywords_cmd.command("extract")
@click.pass_context
def keywords_extract(ctx: click.Context):
    """Manually extract keywords from existing database."""
    config: Config = ctx.obj["config"]
    if not Path(config.database.path).exists():
        console.print("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return
    db = Database(Path(config.database.path))
    db.init_db()
    repos = db.get_all_repositories(limit=10000)
    db.close()
    if not repos:
        console.print("[yellow]No repositories in database.[/yellow]")
        return
    extractor = KeywordExtractor(Path(config.keywords.file), max_keywords=config.keywords.max_keywords)
    existing = extractor.load_keywords()
    new = extractor.extract_from_repos(repos)
    merged = extractor.merge_keywords(existing, new)
    extractor.save_keywords(merged)
    console.print(f"[green]Extracted {len(new)} new keywords[/green]")
    console.print(f"[green]Total: {len(merged)} keywords[/green]")


@keywords_cmd.command("clear")
@click.pass_context
def keywords_clear(ctx: click.Context):
    """Clear all keywords."""
    config: Config = ctx.obj["config"]
    extractor = KeywordExtractor(Path(config.keywords.file))
    extractor.save_keywords(set())
    console.print("[green]Keywords cleared.[/green]")


cli.add_command(keywords_cmd, name="keywords")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8080, help="Server port")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int):
    """Start REST API server."""
    from ai_scraper.api_server import run_server
    console.print(f"[bold green]Starting API server at http://{host}:{port}[/bold green]")
    run_server(host=host, port=port)


@cli.command()
@click.option("--cron", default="0 9 * * *", help="Cron expression for schedule")
@click.option("--max-results", default=100, help="Max results per scrape")
@click.pass_context
def schedule(ctx: click.Context, cron: str, max_results: int):
    """Schedule periodic scraping.

    Example cron expressions:
      "0 9 * * *"     - Daily at 9:00 AM
      "0 */6 * * *"   - Every 6 hours
      "0 9 * * 1-5"   - Weekdays at 9:00 AM
    """
    from ai_scraper.scheduler import scheduler

    async def run_scrape():
        console.print(f"[dim]{datetime.now()}: Starting scheduled scrape[/dim]")
        ctx.invoke(scrape, max_results=max_results)

    scheduler.add_task("scrape", cron, lambda: asyncio.run(run_scrape()))

    console.print(f"[bold green]Scheduler started[/bold green]")
    console.print(f"[dim]Next run: {scheduler.tasks['scrape']['next_run']}[/dim]")

    asyncio.run(scheduler.run())


@cli.command()
@click.pass_context
def interactive(ctx: click.Context):
    """Start interactive mode with menu-driven interface."""
    from ai_scraper.interactive import show_main_menu, get_scrape_params
    from rich.prompt import Prompt

    while True:
        choice = show_main_menu()

        if choice == "q":
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        elif choice == "1":
            # Quick scrape
            ctx.invoke(scrape, max_results=50)
        elif choice == "2":
            # Deep scrape
            ctx.invoke(scrape, max_results=500)
        elif choice == "3":
            # Custom scrape
            params = get_scrape_params()
            ctx.invoke(scrape, **params)
        elif choice == "4":
            # View results
            ctx.invoke(list_repos)
        elif choice == "5":
            # Trending
            ctx.invoke(trending)
        elif choice == "6":
            # Export
            format_choice = Prompt.ask("Export format", choices=["csv", "json", "html"], default="csv")
            ctx.invoke(db_export, format=format_choice, output=f"export.{format_choice}")
        elif choice == "7":
            # Settings
            ctx.invoke(config_show)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
