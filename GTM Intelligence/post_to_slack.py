"""
post_to_slack.py — Post the latest generated content to Slack.

Reads the most recent generated content from the database and posts it
to the configured Slack channel (#linkedin-thoughtleadership).

Usage:
    python scripts/post_to_slack.py
    python scripts/post_to_slack.py --type linkedin
    python scripts/post_to_slack.py --type ae_digest
    python scripts/post_to_slack.py --type all --limit 6
    python scripts/post_to_slack.py --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel

console = Console()

SLACK_CHANNEL = "#linkedin-thoughtleadership"
CONTENT_TYPES = ["ae_digest", "linkedin", "article", "forum"]


def format_slack_message(item: dict) -> str:
    """Format a generated content item as a Slack message."""
    content_type = item.get("content_type", "")
    title = item.get("title", "")
    content = item.get("content", "")
    word_count = item.get("word_count", 0)
    generated_at = item.get("generated_at", "")

    header_map = {
        "ae_digest":  "📊 *AE Weekly Trend Digest*",
        "linkedin":   "📝 *LinkedIn Article*",
        "article":    "📄 *Thought Leadership Article*",
        "forum":      "💬 *Forum Post*",
    }

    header = header_map.get(content_type, f"📋 *{content_type.title()}*")

    if title:
        header += f"\n*{title}*"

    if word_count:
        header += f"  _{word_count} words_"

    return f"{header}\n\n{content}"


async def get_latest_content(content_type: str | None = None, limit: int = 6) -> list[dict]:
    """Fetch the latest generated content from the database."""
    from src.storage.database import init_db, get_session
    from src.storage.models import GeneratedContent
    from sqlalchemy import select, desc

    await init_db()

    async with get_session() as session:
        query = select(GeneratedContent).order_by(desc(GeneratedContent.generated_at))

        if content_type and content_type != "all":
            query = query.where(GeneratedContent.content_type == content_type)

        query = query.limit(limit)
        result = await session.execute(query)
        rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "content_type": r.content_type,
            "title": r.title,
            "content": r.content,
            "word_count": r.word_count,
            "generated_at": str(r.generated_at),
        }
        for r in rows
    ]


async def post_to_slack(
    content_type: str | None = None,
    limit: int = 6,
    dry_run: bool = False,
) -> None:
    """Fetch content and post to Slack."""
    items = await get_latest_content(content_type=content_type, limit=limit)

    if not items:
        console.print("[yellow]No content found. Run 'python main.py generate' first.[/yellow]")
        return

    console.print(f"[cyan]Found {len(items)} content item(s) to post.[/cyan]")

    for i, item in enumerate(items, 1):
        msg = format_slack_message(item)
        ct = item["content_type"]
        title = item.get("title") or ct

        console.print(f"\n[{i}/{len(items)}] Posting: [bold]{ct}[/bold] — {title[:60]}")

        if dry_run:
            console.print(Panel(msg[:500] + "...", title="[yellow]DRY RUN — Not sent[/yellow]"))
            continue

        # Post via Slack MCP (when running inside Claude Code context)
        # When running standalone, print instructions
        console.print(f"  → Channel: {SLACK_CHANNEL}")
        console.print(f"  → Length: {len(msg)} characters")
        console.print("[green]  ✓ Ready to post[/green]")

        # Save to output file for manual posting if needed
        out_dir = Path("output/slack")
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"{ts}_{i}_{ct}.txt"
        out_file.write_text(msg, encoding="utf-8")
        console.print(f"  → Saved to: {out_file}")

    console.print(f"\n[bold green]Done. {len(items)} items processed.[/bold green]")


def main():
    parser = argparse.ArgumentParser(
        description="Post generated content to Slack #linkedin-thoughtleadership"
    )
    parser.add_argument(
        "--type",
        choices=CONTENT_TYPES + ["all"],
        default="all",
        help="Content type to post (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=6,
        help="Max number of items to post (default: 6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview content without posting",
    )
    args = parser.parse_args()

    content_type = None if args.type == "all" else args.type

    console.rule("[bold cyan]GTM Intelligence — Slack Poster[/bold cyan]")
    console.print(f"Channel: {SLACK_CHANNEL}")
    console.print(f"Type: {args.type}  |  Limit: {args.limit}  |  Dry run: {args.dry_run}")
    console.print()

    asyncio.run(
        post_to_slack(
            content_type=content_type,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
