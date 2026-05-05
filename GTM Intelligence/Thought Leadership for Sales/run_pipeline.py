"""
run_pipeline.py — Run the full GTM Intelligence pipeline end-to-end.

This is the script called by the Wednesday 7am scheduled task.
Steps: ingest → analyze → generate → export → (optionally post to Slack)

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --top-n 6 --lookback 7
    python scripts/run_pipeline.py --skip-ingest        # analyze + generate only
    python scripts/run_pipeline.py --skip-slack         # no Slack posting
    python scripts/run_pipeline.py --dry-run            # no DB writes, no Slack
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.rule import Rule

console = Console()


def elapsed(start: float) -> str:
    secs = time.time() - start
    if secs < 60:
        return f"{secs:.1f}s"
    return f"{int(secs // 60)}m {int(secs % 60)}s"


async def run_pipeline(
    lookback: int = 7,
    top_n: int = 6,
    skip_ingest: bool = False,
    skip_slack: bool = False,
    dry_run: bool = False,
) -> dict:
    """Run the full pipeline and return a summary dict."""
    from src.storage.database import init_db

    pipeline_start = time.time()
    results = {
        "run_at": datetime.now().isoformat(),
        "ingest": {},
        "analyze": {},
        "generate": {},
        "errors": [],
    }

    await init_db()
    console.rule("[bold cyan]GTM Intelligence — Full Pipeline Run[/bold cyan]")
    console.print(f"[dim]{results['run_at']}  |  lookback={lookback}d  |  top_n={top_n}  |  dry_run={dry_run}[/dim]\n")

    # ── Step 1: Ingest ────────────────────────────────────────────
    if not skip_ingest:
        console.print("[bold][1/3] Ingesting posts...[/bold]")
        step_start = time.time()
        try:
            if not dry_run:
                from src.ingestion.manager import run_ingestion
                stats = await run_ingestion()
            else:
                stats = {"total": 0, "new": 0, "skipped": 0, "errors": 0}

            results["ingest"] = stats
            console.print(
                f"  [green]✓[/green] {stats['new']} new posts saved  "
                f"[dim]({stats['total']} fetched, {stats.get('skipped', 0)} skipped)[/dim]  "
                f"[dim]{elapsed(step_start)}[/dim]"
            )
        except Exception as e:
            results["errors"].append(f"Ingest failed: {e}")
            console.print(f"  [red]✗ Ingest error: {e}[/red]")
    else:
        console.print("[dim][1/3] Skipping ingest (--skip-ingest)[/dim]")

    # ── Step 2: Analyze ───────────────────────────────────────────
    console.print("\n[bold][2/3] Running analysis...[/bold]")
    step_start = time.time()
    try:
        if not dry_run:
            from src.analysis.pipeline import run_analysis_pipeline
            stats = await run_analysis_pipeline(lookback_days=lookback)
        else:
            stats = {"posts_analyzed": 0, "themes_scored": 0, "errors": 0}

        results["analyze"] = stats
        console.print(
            f"  [green]✓[/green] {stats['posts_analyzed']} posts analyzed, "
            f"{stats['themes_scored']} themes scored  "
            f"[dim]{elapsed(step_start)}[/dim]"
        )
    except Exception as e:
        results["errors"].append(f"Analysis failed: {e}")
        console.print(f"  [red]✗ Analysis error: {e}[/red]")

    # ── Step 3: Generate ──────────────────────────────────────────
    console.print("\n[bold][3/3] Generating content...[/bold]")
    step_start = time.time()
    try:
        if not dry_run:
            from src.generation.content_generator import run_content_generation
            gen_results = await run_content_generation(top_n=top_n)
        else:
            gen_results = {}

        results["generate"] = gen_results
        for ct, cid in gen_results.items():
            console.print(f"  [green]✓[/green] {ct}  [dim](id={cid})[/dim]")

        if not gen_results:
            console.print("  [yellow]No content generated. Check theme scores.[/yellow]")

        console.print(f"  [dim]{elapsed(step_start)}[/dim]")
    except Exception as e:
        results["errors"].append(f"Generation failed: {e}")
        console.print(f"  [red]✗ Generation error: {e}[/red]")

    # ── Export to files ───────────────────────────────────────────
    if not dry_run and results["generate"]:
        from pathlib import Path as P
        out_dir = P("output") / datetime.now().strftime("%Y%m%d")
        out_dir.mkdir(parents=True, exist_ok=True)

        from src.generation.content_generator import get_latest_content
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for ct in results["generate"]:
            items = await get_latest_content(content_type=ct)
            if items:
                item = items[0]
                fpath = out_dir / f"{ts}_{ct}.md"
                fpath.write_text(item["content"], encoding="utf-8")
        console.print(f"\n  [dim]Files saved to {out_dir}/[/dim]")

    # ── Summary ───────────────────────────────────────────────────
    total_time = elapsed(pipeline_start)
    console.print()
    console.rule("[bold green]Pipeline Complete[/bold green]")
    console.print(f"  Total time: [bold]{total_time}[/bold]")

    if results["errors"]:
        console.print(f"\n[red]Errors ({len(results['errors'])}):[/red]")
        for err in results["errors"]:
            console.print(f"  • {err}")
    else:
        console.print("  [green]No errors.[/green]")

    if skip_slack:
        console.print("  [dim]Slack posting skipped (--skip-slack)[/dim]")
    elif not dry_run:
        console.print("\n[dim]To post to Slack, run: python scripts/post_to_slack.py[/dim]")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run the full GTM Intelligence pipeline"
    )
    parser.add_argument("--lookback", type=int, default=7, help="Days to look back (default: 7)")
    parser.add_argument("--top-n", type=int, default=6, help="Top N themes for content (default: 6)")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip ingestion step")
    parser.add_argument("--skip-slack", action="store_true", help="Skip Slack posting step")
    parser.add_argument("--dry-run", action="store_true", help="Simulate run without writes")
    args = parser.parse_args()

    asyncio.run(
        run_pipeline(
            lookback=args.lookback,
            top_n=args.top_n,
            skip_ingest=args.skip_ingest,
            skip_slack=args.skip_slack,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
