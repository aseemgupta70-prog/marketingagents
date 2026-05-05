---
name: gtm-intelligence
description: "Use this skill to operate the GTM Intelligence system — an automated pipeline that monitors public accounting communities (Reddit, HackerNews, RSS), scores trending buyer pain themes using NLP, and generates non-salesy thought-leadership content (LinkedIn articles, short posts, AE digests, HTML banners) posted to Slack. Trigger this skill whenever the user asks to: run the content pipeline, generate LinkedIn or accounting articles, check trending accounting topics, post content to Slack #linkedin-thoughtleadership, operate the weekly GTM content automation, build the article summary deck, or troubleshoot why a scheduled run didn't fire. Project lives at: C:\\Aseem Backup\\GTM Engineering\\02. Claude\\01. Claude Code\\gtm-intelligence\\"
license: Proprietary — "Placeholder Company" AI internal use only
---

# GTM Intelligence Skill

## Quick Reference

| Task | Command |
|------|---------|
| Full pipeline (ingest → analyze → generate) | `python main.py run-all` |
| Ingest posts only | `python main.py ingest` |
| Analyze & score themes | `python main.py analyze` |
| View trending themes | `python main.py report --top 10` |
| Generate all content | `python main.py generate --type all --top-n 6` |
| Post content to Slack | `python scripts/post_to_slack.py` |
| System health check | `python scripts/health_check.py` |
| Export content to files | `python scripts/export_content.py` |
| Build summary deck | `node build-deck.js` |
| Start API server | `python main.py serve --port 8000` |

---

## Project Location

```
C:\Aseem Backup\GTM Engineering\02. Claude\01. Claude Code\gtm-intelligence\
```

Always `cd` to this directory before running any commands.

**Python interpreter:** `.venv\Scripts\python.exe` (Windows venv)  
**Node.js:** system `node` (v18+)

---

## Environment Setup

Before any run, confirm `.env` exists and contains:

```
ANTHROPIC_API_KEY=sk-ant-api03-...        ← Required: Claude content generation
REDDIT_CLIENT_ID=...                       ← Optional but recommended
REDDIT_CLIENT_SECRET=...                   ← Optional but recommended
REDDIT_USER_AGENT=GTMIntelligence/1.0      ← Optional but recommended
DATABASE_URL=sqlite:///./data/gtm_intel.db ← Default SQLite path
```

Without Reddit credentials, ingestion runs on HackerNews + RSS only (~5–10 posts). With Reddit: 250+ posts/run across 8 subreddits.

---

## Standard Weekly Run

This is what the scheduled Wednesday 7am task does:

```bash
cd "C:\Aseem Backup\GTM Engineering\02. Claude\01. Claude Code\gtm-intelligence"

# Step 1 — Ingest from all sources
python main.py ingest

# Step 2 — NLP analysis + theme scoring (7-day window)
python main.py analyze --lookback 7

# Step 3 — Generate content via Claude API
python main.py generate --type all --top-n 6

# Step 4 — Post everything to Slack
python scripts/post_to_slack.py
```

Or run the full pipeline in one command:
```bash
python main.py run-all --lookback 7 --top-n 6
```

---

## Content Types Generated

| Type | Description | Length |
|------|-------------|--------|
| `ae_digest` | Internal AE briefing — top trends + conversation angles | ~300 words |
| `linkedin` | Thought-leadership articles — practitioner voice, no sales | 400–500 words |
| `article` | Long-form trade publication style | 600–900 words |
| `forum` | Community forum reply style | 200–350 words |

All content is non-promotional, practitioner-voiced, no CTAs, no product names.

---

## Themes Tracked (10 total)

| Slug | Theme |
|------|-------|
| `ai-automation` | AI & Automation in Accounting |
| `month-end-close` | Month-End Close & Reconciliation |
| `ap-billpay` | Accounts Payable & Bill Pay |
| `audit-compliance` | Audit & Compliance |
| `payroll-integration` | Payroll Integration |
| `erp-integrations` | ERP & Software Integrations |
| `cash-flow` | Cash Flow & Financial Reporting |
| `tax-regulatory` | Tax & Regulatory |
| `staffing-capacity` | Staffing & Capacity |
| `vendor-management` | Vendor Management |

---

## Scoring Weights

| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Frequency | 30% | How often a theme appears across posts |
| Momentum | 25% | Trending up vs prior week |
| Pain Intensity | 20% | VADER sentiment → emotional signal |
| Source Diversity | 15% | Multi-platform signal = higher confidence |
| Recency | 10% | Newer posts score higher |

---

## Slack Posting

Content is posted to channel **#linkedin-thoughtleadership** (channel ID: CNW46E5BN).

Post order per weekly run:
1. Trending topics summary
2. AE Digest
3. 6 LinkedIn articles (full text)
4. 6 short posts (100-word versions)
5. 6 banner images

To post manually:
```bash
python scripts/post_to_slack.py
```

To post specific content type:
```bash
python scripts/post_to_slack.py --type linkedin
python scripts/post_to_slack.py --type ae_digest
```

---

## Scheduled Automation

The system uses Claude Code Scheduled Tasks MCP — **not** a local cron file.

**Schedule:** Every Wednesday at 7:00 AM PT  
**What runs:** Full pipeline + Slack posting  

**Known issue:** Slack tool permissions time out on first unattended run. Fix: open Claude Code → Scheduled Tasks → click "Run Now" once to pre-authorize permissions.

---

## Troubleshooting

### No content generated
```bash
# Check if themes have been scored recently
python main.py report --top 10

# If no themes, run analysis first
python main.py analyze --lookback 7

# If still nothing, check DB has posts
python scripts/health_check.py
```

### API key error
```bash
# Verify .env is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:20])"
```

### Scheduled task didn't fire
1. Check Claude Code Scheduled Tasks panel
2. Click "Run Now" to pre-approve Slack permissions
3. Verify cron expression: `0 7 * * 3` (Wed 7am local time)
4. Note: runs in machine local time (IST = UTC+5:30), not PT

### Reddit not returning posts
- Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`
- Get credentials at: https://www.reddit.com/prefs/apps (Script type app)

---

## Data Sources

| Source | Details | Auth |
|--------|---------|------|
| Reddit | 8 subreddits via PRAW — r/accounting, r/bookkeeping, r/QuickBooks, r/taxpros, r/CFO, r/xero, r/smallbusiness, r/financialindependence | Client ID + Secret in `.env` |
| HackerNews | Algolia Search API, 9 keyword queries | None required |
| RSS Feeds | AccountingToday, Journal of Accountancy, AccountingWEB, CPA Practice Advisor, Going Concern, Insightful Accountant | None required |

---

## Deck Generation

To build the 12-slide PowerPoint summary deck:

```bash
cd "C:\Aseem Backup\GTM Engineering\02. Claude\01. Claude Code\gtm-intelligence"
node build-deck.js
# Output: GTM-Intelligence-Article-Summary.pptx
```

Requires `pptxgenjs` (already installed via `npm install`).

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `main.py` | All CLI commands entry point |
| `build-deck.js` | PowerPoint deck generator |
| `config/settings.yaml` | Scoring weights, model name, ingestion limits |
| `config/sources.yaml` | Reddit subreddits, HN queries, RSS feed URLs |
| `.env` | API keys — never commit this |
| `data/gtm_intel.db` | SQLite database (auto-created on `init`) |
| `src/generation/prompts.py` | All Claude prompt templates |
| `src/analysis/themes.py` | 10 theme definitions |
| `scripts/post_to_slack.py` | Slack posting utility |
| `scripts/health_check.py` | System status checker |
| `scripts/export_content.py` | Export content to markdown files |

---

## Running Tests

```bash
pytest                          # All tests (in-memory SQLite)
pytest tests/test_analysis.py   # NLP pipeline
pytest tests/test_generation.py # Content generation
pytest tests/test_ingestion.py  # Source ingestion
```
