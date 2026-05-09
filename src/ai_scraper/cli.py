"""CLI entry point for ai-scraper."""

import asyncio
from pathlib import Path
from typing import Optional

import click
import rich.table as table
from rich import print as rprint

from ai_scraper import __version__
from ai_scraper.api.github import GitHubClient
from ai_scraper.config import Config, load_config
from ai_scraper.filters.ai_filter import AIFilter
from ai_scraper.models.repository import FilterConfig as FilterConfigModel
from ai_scraper.storage.database import Database


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
@click.pass_context
def scrape(ctx: click.Context, min_stars: Optional[int], max_results: Optional[int]):
    """Scrape AI repositories from GitHub."""
    config: Config = ctx.obj["config"]

    # Override config with CLI options
    if min_stars is not None:
        config.filter.min_stars = min_stars
    if max_results is not None:
        config.scrape.max_results = max_results

    rprint("[bold blue]Starting scrape...[/bold blue]")

    async def run_scrape():
        client = GitHubClient(token=config.github.token)
        db = Database(Path(config.database.path))
        db.init_db()
        filter_instance = AIFilter()

        try:
            # Build search query
            topics_query = " ".join(f"topic:{t}" for t in config.filter.topics[:5])
            query = f"stars:>{config.filter.min_stars} {topics_query}"

            rprint(f"[dim]Query: {query}[/dim]")

            # Search repositories
            all_repos = []
            page = 1
            per_page = 100

            while len(all_repos) < config.scrape.max_results:
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
                    if filter_instance.is_ai_related(repo, filter_config):
                        score = filter_instance.score_relevance(repo)
                        db.save_repository(repo, relevance_score=score)
                        all_repos.append(repo)

                rprint(f"[dim]Page {page}: found {len(repos)} repos, {len(all_repos)} total AI-related[/dim]")
                page += 1

                if len(repos) < per_page:
                    break

            rprint(f"[bold green]Scraped {len(all_repos)} AI repositories[/bold green]")

        finally:
            await client.close()
            db.close()

    asyncio.run(run_scrape())


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
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
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
        desc = repo.description[:37] + "..." if repo.description and len(repo.description) > 40 else repo.description or ""
        tbl.add_row(repo.name, stars_str, repo.language or "-", desc)

    rprint(tbl)
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
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    trends = db.get_trending(days=days, limit=top)

    if not trends:
        rprint(f"[yellow]No trending data found for the last {days} days.[/yellow]")
        rprint("[dim]Run 'ai-scraper scrape' multiple times to build trend data.[/dim]")
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

    rprint(tbl)
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
        rprint(f"[yellow]Config file already exists at {config_path}[/yellow]")
        return

    # Copy default config
    import shutil
    default_config = Path(__file__).parent.parent.parent / "ai-scraper.yaml"

    if default_config.exists():
        shutil.copy(default_config, config_path)
        rprint(f"[green]Created config file at {config_path}[/green]")
    else:
        rprint("[red]Default config not found[/red]")


@config_cmd.command("show")
@click.pass_context
def config_show(ctx: click.Context):
    """Show current configuration."""
    config: Config = ctx.obj["config"]

    rprint("[bold]Current Configuration:[/bold]")
    rprint(f"  GitHub Token: {'***' if config.github.token else 'Not set'}")
    rprint(f"  Cache TTL: {config.github.cache_ttl}s")
    rprint(f"  Min Stars: {config.filter.min_stars}")
    rprint(f"  Keywords: {', '.join(config.filter.keywords[:5])}...")
    rprint(f"  Topics: {', '.join(config.filter.topics[:5])}...")
    rprint(f"  Max Results: {config.scrape.max_results}")
    rprint(f"  Database: {config.database.path}")
    rprint(f"  Scheduler: {'enabled' if config.scheduler.enabled else 'disabled'}")


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
        rprint("[yellow]No database found. Run 'ai-scraper scrape' first.[/yellow]")
        return

    db.init_db()
    stats = db.get_stats()

    rprint("[bold]Database Statistics:[/bold]")
    rprint(f"  Repository count: {stats['repository_count']}")
    rprint(f"  Snapshot count: {stats['snapshot_count']}")
    rprint(f"  Total stars: {stats['total_stars']:,}")

    db.close()


@db_cmd.command("clean")
@click.option("--days", type=int, default=30, help="Keep snapshots from last N days")
@click.pass_context
def db_clean(ctx: click.Context, days: int):
    """Clean old snapshots."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found.[/yellow]")
        return

    db.init_db()
    deleted = db.clean_old_snapshots(days=days)

    rprint(f"[green]Deleted {deleted} old snapshots[/green]")
    db.close()


@db_cmd.command("export")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--output", "-o", type=click.Path(), default="export.csv")
@click.pass_context
def db_export(ctx: click.Context, format: str, output: str):
    """Export database to file."""
    config: Config = ctx.obj["config"]
    db = Database(Path(config.database.path))

    if not Path(config.database.path).exists():
        rprint("[yellow]No database found.[/yellow]")
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

        rprint(f"[green]Exported {len(repos)} repositories to {output}[/green]")

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

        rprint(f"[green]Exported {len(repos)} repositories to {output}[/green]")

    db.close()


cli.add_command(db_cmd, name="db")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
