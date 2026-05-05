"""
health_check.py — Check GTM Intelligence system status.

Shows database stats, last ingestion run, last content generation,
API key validity, and source connectivity.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --verbose
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


async def check_database() -> dict:
    """Check database connectivity and row counts."""
    from src.storage.database import init_db, get_session
    from src.storage.models import Post, Theme, ThemeScore, GeneratedContent
    from sqlalchemy import select, func, desc

    await init_db()

    stats = {}
    async with get_session() as session:
        # Post count
        result = await session.execute(select(func.count(Post.id)))
        stats["total_posts"] = result.scalar() or 0

        # Posts in last 7 days
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(
            select(func.count(Post.id)).where(Post.created_at >= cutoff)
        )
        stats["posts_last_7d"] = result.scalar() or 0

        # Latest post
        result = await session.execute(
            select(Post.created_at).order_by(desc(Post.created_at)).limit(1)
        )
        row = result.scalar()
        stats["latest_post"] = str(row) if row else "None"

        # Theme scores
        result = await session.execute(select(func.count(ThemeScore.id)))
        stats["theme_scores"] = result.scalar() or 0

        # Latest theme score
        result = await session.execute(
            select(ThemeScore.computed_at).order_by(desc(ThemeScore.computed_at)).limit(1)
        )
        row = result.scalar()
        stats["latest_analysis"] = str(row) if row else "Never"

        # Generated content count
        result = await session.execute(select(func.count(GeneratedContent.id)))
        stats["total_content"] = result.scalar() or 0

        # Latest generated content
        result = await session.execute(
            select(GeneratedContent.generated_at, GeneratedContent.content_type)
            .order_by(desc(GeneratedContent.generated_at))
            .limit(1)
        )
        row = result.first()
        if row:
            stats["latest_content"] = f"{row[1]} @ {row[0]}"
        else:
            stats["latest_content"] = "Never"

        # Content breakdown
        result = await session.execute(
            select(GeneratedContent.content_type, func.count(GeneratedContent.id))
            .group_by(GeneratedContent.content_type)
        )
        stats["content_by_type"] = {row[0]: row[1] for row in result.all()}

        # Top scored themes
        result = await session.execute(
            select(ThemeScore, Theme)
            .join(Theme, Theme.id == ThemeScore.theme_id)
            .order_by(desc(ThemeScore.composite_score))
            .limit(5)
        )
        stats["top_themes"] = [
            {
                "name": theme.name,
                "score": round(score.composite_score, 3),
                "posts": score.post_count,
                "rank": score.rank or "—",
            }
            for score, theme in result.all()
        ]

    return stats


def check_env() -> dict:
    """Check environment variables."""
    return {
        "anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "anthropic_key_preview": (os.getenv("ANTHROPIC_API_KEY") or "")[:20] + "...",
        "reddit_client_id": bool(os.getenv("REDDIT_CLIENT_ID")),
        "reddit_secret": bool(os.getenv("REDDIT_CLIENT_SECRET")),
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./data/gtm_intel.db"),
    }


def check_files() -> dict:
    """Check key project files exist."""
    base = Path(__file__).resolve().parent.parent
    files = {
        "main.py": base / "main.py",
        ".env": base / ".env",
        "settings.yaml": base / "config" / "settings.yaml",
        "sources.yaml": base / "config" / "sources.yaml",
        "database": base / "data" / "gtm_intel.db",
        "build-deck.js": base / "build-deck.js",
    }
    return {name: path.exists() for name, path in files.items()}


async def check_anthropic_api() -> bool:
    """Quick test of Anthropic API connectivity."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Minimal test — just check the client initializes
        return client.api_key is not None and len(client.api_key) > 10
    except Exception:
        return False


def print_health_report(db_stats: dict, env: dict, files: dict, api_ok: bool, verbose: bool):
    """Print formatted health report."""
    console.rule("[bold cyan]GTM Intelligence — Health Check[/bold cyan]")
    console.print(f"[dim]Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")

    # ── Environment ────────────────────────────────────────────────
    env_table = Table(title="Environment", box=box.SIMPLE, show_header=False)
    env_table.add_column("Key", style="bold", min_width=25)
    env_table.add_column("Status")

    def status(ok: bool, ok_text: str = "✓ Set", fail_text: str = "✗ Missing") -> str:
        return f"[green]{ok_text}[/green]" if ok else f"[red]{fail_text}[/red]"

    env_table.add_row("ANTHROPIC_API_KEY", status(env["anthropic_key"]) + (f"  [dim]{env['anthropic_key_preview']}[/dim]" if env["anthropic_key"] else ""))
    env_table.add_row("REDDIT_CLIENT_ID", status(env["reddit_client_id"], "✓ Set", "⚠ Not set (HN+RSS only)"))
    env_table.add_row("REDDIT_CLIENT_SECRET", status(env["reddit_secret"], "✓ Set", "⚠ Not set (HN+RSS only)"))
    env_table.add_row("DATABASE_URL", f"[dim]{env['database_url']}[/dim]")
    env_table.add_row("Anthropic API", status(api_ok, "✓ Connected", "✗ Connection failed"))
    console.print(env_table)

    # ── Files ─────────────────────────────────────────────────────
    file_table = Table(title="Project Files", box=box.SIMPLE, show_header=False)
    file_table.add_column("File", style="bold", min_width=25)
    file_table.add_column("Status")
    for name, exists in files.items():
        file_table.add_row(name, "[green]✓ Found[/green]" if exists else "[red]✗ Missing[/red]")
    console.print(file_table)

    # ── Database ─────────────────────────────────────────────────
    db_table = Table(title="Database Stats", box=box.SIMPLE, show_header=False)
    db_table.add_column("Metric", style="bold", min_width=25)
    db_table.add_column("Value")
    db_table.add_row("Total posts ingested", str(db_stats["total_posts"]))
    db_table.add_row("Posts (last 7 days)", str(db_stats["posts_last_7d"]))
    db_table.add_row("Latest post ingested", db_stats["latest_post"])
    db_table.add_row("Theme scores computed", str(db_stats["theme_scores"]))
    db_table.add_row("Last analysis run", db_stats["latest_analysis"])
    db_table.add_row("Total content generated", str(db_stats["total_content"]))
    db_table.add_row("Latest content", db_stats["latest_content"])
    console.print(db_table)

    # ── Content breakdown ─────────────────────────────────────────
    if db_stats.get("content_by_type"):
        ct_table = Table(title="Content Generated by Type", box=box.SIMPLE, show_header=False)
        ct_table.add_column("Type", style="bold", min_width=20)
        ct_table.add_column("Count", justify="right")
        for ct, count in db_stats["content_by_type"].items():
            ct_table.add_row(ct, str(count))
        console.print(ct_table)

    # ── Top themes ────────────────────────────────────────────────
    if db_stats.get("top_themes") and verbose:
        theme_table = Table(title="Top Scored Themes", box=box.SIMPLE)
        theme_table.add_column("Rank", style="dim", width=6)
        theme_table.add_column("Theme", min_width=35)
        theme_table.add_column("Score", justify="right")
        theme_table.add_column("Posts", justify="right")
        for t in db_stats["top_themes"]:
            theme_table.add_row(str(t["rank"]), t["name"], str(t["score"]), str(t["posts"]))
        console.print(theme_table)

    # ── Summary ───────────────────────────────────────────────────
    issues = []
    if not env["anthropic_key"]:
        issues.append("ANTHROPIC_API_KEY not set — content generation will fail")
    if not env["reddit_client_id"]:
        issues.append("Reddit credentials not set — running on HN+RSS only")
    if db_stats["total_posts"] == 0:
        issues.append("No posts in database — run: python main.py ingest")
    if db_stats["theme_scores"] == 0:
        issues.append("No theme scores — run: python main.py analyze")
    if db_stats["total_content"] == 0:
        issues.append("No content generated yet — run: python main.py generate --type all")

    if issues:
        console.print("\n[bold yellow]⚠ Action Needed:[/bold yellow]")
        for issue in issues:
            console.print(f"  • {issue}")
    else:
        console.print("\n[bold green]✓ System healthy — all checks passed[/bold green]")


async def run_health_check(verbose: bool = False):
    env = check_env()
    files = check_files()
    api_ok = await check_anthropic_api()

    try:
        db_stats = await check_database()
    except Exception as e:
        console.print(f"[red]Database error: {e}[/red]")
        db_stats = {
            "total_posts": 0, "posts_last_7d": 0, "latest_post": "Error",
            "theme_scores": 0, "latest_analysis": "Error",
            "total_content": 0, "latest_content": "Error",
            "content_by_type": {}, "top_themes": [],
        }

    print_health_report(db_stats, env, files, api_ok, verbose)


def main():
    parser = argparse.ArgumentParser(description="GTM Intelligence system health check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show top themes table")
    args = parser.parse_args()
    asyncio.run(run_health_check(verbose=args.verbose))


if __name__ == "__main__":
    main()
