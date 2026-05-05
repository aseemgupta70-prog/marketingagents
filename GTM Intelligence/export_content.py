"""
export_content.py — Export generated content to markdown files.

Pulls the latest generated content from the database and writes
each item to a dated markdown file under ./output/.

Usage:
    python scripts/export_content.py
    python scripts/export_content.py --type linkedin
    python scripts/export_content.py --limit 6 --out-dir ./exports
    python scripts/export_content.py --week 2026-04-15
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table

console = Console()

CONTENT_TYPES = ["ae_digest", "linkedin", "article", "forum"]


async def export_content(
    content_type: str | None,
    limit: int,
    out_dir: Path,
    week_of: str | None,
) -> list[Path]:
    """Fetch content from DB and write to markdown files."""
    from src.storage.database import init_db, get_session
    from src.storage.models import GeneratedContent
    from sqlalchemy import select, desc

    await init_db()
    out_dir.mkdir(parents=True, exist_ok=True)

    async with get_session() as session:
        query = select(GeneratedContent).order_by(desc(GeneratedContent.generated_at))

        if content_type and content_type != "all":
            query = query.where(GeneratedContent.content_type == content_type)

        if week_of:
            try:
                week_start = datetime.strptime(week_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                week_end = week_start + timedelta(days=7)
                query = query.where(GeneratedContent.generated_at >= week_start)
                query = query.where(GeneratedContent.generated_at < week_end)
            except ValueError:
                console.print(f"[red]Invalid date format: {week_of}. Use YYYY-MM-DD[/red]")
                return []

        query = query.limit(limit)
        result = await session.execute(query)
        rows = result.scalars().all()

    if not rows:
        console.print("[yellow]No content found matching criteria.[/yellow]")
        return []

    saved = []
    for row in rows:
        ts = row.generated_at.strftime("%Y%m%d_%H%M%S") if row.generated_at else "unknown"
        slug = (row.title or row.content_type or "content")[:50]
        slug = "".join(c if c.isalnum() or c in "-_ " else "" for c in slug)
        slug = slug.strip().replace(" ", "_").lower()

        filename = f"{ts}_{row.content_type}_{slug}.md"
        filepath = out_dir / filename

        # Build markdown content
        lines = [
            f"# {row.title or row.content_type.replace('_', ' ').title()}",
            "",
            f"**Type:** {row.content_type}  ",
            f"**Generated:** {row.generated_at}  ",
            f"**Words:** {row.word_count or 'N/A'}  ",
            "",
            "---",
            "",
            row.content or "",
        ]

        filepath.write_text("\n".join(lines), encoding="utf-8")
        saved.append(filepath)
        console.print(f"[green]✓[/green] {filepath.name}  [dim]({row.word_count or '?'} words)[/dim]")

    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Export generated content to markdown files"
    )
    parser.add_argument(
        "--type",
        choices=CONTENT_TYPES + ["all"],
        default="all",
        help="Content type to export (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max items to export (default: 20)",
    )
    parser.add_argument(
        "--out-dir",
        default="./output/exports",
        help="Output directory (default: ./output/exports)",
    )
    parser.add_argument(
        "--week",
        default=None,
        metavar="YYYY-MM-DD",
        help="Export content from a specific week (start date)",
    )
    args = parser.parse_args()

    content_type = None if args.type == "all" else args.type
    out_dir = Path(args.out_dir)

    console.rule("[bold cyan]GTM Intelligence — Content Exporter[/bold cyan]")
    console.print(f"Type: [bold]{args.type}[/bold]  |  Limit: {args.limit}  |  Output: {out_dir}")
    if args.week:
        console.print(f"Week of: {args.week}")
    console.print()

    saved = asyncio.run(
        export_content(
            content_type=content_type,
            limit=args.limit,
            out_dir=out_dir,
            week_of=args.week,
        )
    )

    console.print(f"\n[bold]Exported {len(saved)} file(s) to {out_dir}/[/bold]")


if __name__ == "__main__":
    main()
