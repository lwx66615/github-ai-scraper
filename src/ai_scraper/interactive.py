"""Interactive CLI mode."""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()


def show_main_menu() -> str:
    """Show main menu and get user choice.

    Returns:
        User's menu choice.
    """
    console.print(Panel.fit(
        "[bold cyan]GitHub AI Scraper[/bold cyan]\n"
        "AI Repository Discovery Tool",
        border_style="cyan"
    ))

    console.print("\n[bold]What would you like to do?[/bold]\n")
    console.print("  [1] Quick Scrape    - Fetch top AI repos (fast)")
    console.print("  [2] Deep Scrape     - Comprehensive search (slow)")
    console.print("  [3] Custom Scrape   - Set your own parameters")
    console.print("  [4] View Results    - List scraped repositories")
    console.print("  [5] Trending        - See trending repos")
    console.print("  [6] Export Data     - Export to CSV/JSON")
    console.print("  [7] Settings        - Configure options")
    console.print("  [q] Quit\n")

    return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "q"])


def get_scrape_params() -> dict:
    """Interactively get scrape parameters.

    Returns:
        Dictionary of scrape parameters.
    """
    console.print("\n[bold]Custom Scrape Configuration[/bold]\n")

    # Get min_stars with validation
    while True:
        try:
            min_stars = int(Prompt.ask("Minimum stars", default="100"))
            if min_stars < 0:
                console.print("[red]Minimum stars must be non-negative[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    # Get max_results with validation
    while True:
        try:
            max_results = int(Prompt.ask("Maximum results", default="100"))
            if max_results <= 0:
                console.print("[red]Maximum results must be greater than 0[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    language = Prompt.ask("Language filter (leave empty for all)", default="")

    return {
        "min_stars": min_stars,
        "max_results": max_results,
        "language": language or None,
    }


def show_scrape_progress(current: int, total: int, repo_name: str):
    """Show progress during scraping.

    Args:
        current: Current count.
        total: Total expected.
        repo_name: Name of current repo.
    """
    percent = (current / total * 100) if total > 0 else 0
    console.print(f"  [{current}/{total}] {percent:.0f}% - {repo_name[:40]}")


def confirm_action(message: str) -> bool:
    """Ask for confirmation.

    Args:
        message: Confirmation message.

    Returns:
        True if confirmed.
    """
    from rich.prompt import Confirm
    return Confirm.ask(message)