# Docyt AI — Enterprise Pricing Proposal System
### Hotel Management Company (ICP2) · MEDDPIC-Driven · Sales-Ready

> **Version:** 2.0 · May 2026  
> **Author:** Aseem · Docyt Revenue Operations  
> **Status:** Production-ready · Used for Coury Hospitality $700K close

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Data Sources & Tools](#3-data-sources--tools)
4. [Pricing Framework](#4-pricing-framework)
5. [MEDDPIC Intelligence Layer](#5-meddpic-intelligence-layer)
6. [Proposal Structure — 15-Slide Playbook](#6-proposal-structure--15-slide-playbook)
7. [Branding Guidelines](#7-branding-guidelines-docyt-brand-system)
8. [Scripts & Code](#8-scripts--code)
9. [QA Process](#9-qa-process)
10. [Deal Reference — Coury Hospitality](#10-deal-reference--coury-hospitality)
11. [Reuse Guide — How to Generate the Next Proposal](#11-reuse-guide--how-to-generate-the-next-proposal)
12. [File Index](#12-file-index)

---

## 1. System Overview

This repository packages the complete workflow for generating **sales-ready enterprise pricing proposals** for U.S. hotel management companies (Docyt ICP2). The system:

- **Pulls live deal intelligence** from Grain AI notetaker transcripts
- **Analyzes MEDDPIC signals** automatically from meeting notes
- **Applies the 2026 pricing tier model** from `2026_Hotel_Pricing.xlsx`
- **Generates a 15-slide branded PowerPoint** using `pptxgenjs`
- **Runs visual QA** via LibreOffice → PDF → `pdftoppm` rasterization

### What Gets Produced

| Deliverable | Format | Purpose |
|---|---|---|
| Enterprise Pricing Proposal | `.pptx` (15 slides) | C-suite delivery, board review |
| MEDDPIC Deal Snapshot | Slide 5 (embedded in deck) | AE internal reference |
| ROI & 3-Year Model | Slides 8–9 | Economic justification |
| Competitive Matrix | Slide 12 | Objection handling |
| Close Path | Slide 15 | Next-step alignment |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROPOSAL GENERATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────┘

  INPUT LAYER
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  Grain MCP       │   │  2026_Hotel_      │   │  Prospect Brief  │
  │  - list_meetings │   │  Pricing.xlsx     │   │  (name, props,   │
  │  - fetch_notes   │   │  (tier framework) │   │   stack, stage)  │
  │  - search_mtgs   │   │                  │   │                  │
  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
           │                      │                       │
           ▼                      ▼                       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                     MEDDPIC ANALYSIS LAYER                       │
  │                                                                  │
  │  M = Metrics (ACV, property count, current stack cost)           │
  │  E = Economic Buyer (name, role, decision authority)             │
  │  D = Decision Criteria (SOX, price, automation, deadline)        │
  │  D = Decision Process (pilot → review → go-live → expand)        │
  │  P = Paper Process (contract status, clauses, timeline)          │
  │  I = Identified Pain (fragmentation, manual work, visibility)    │
  │  C = Champion (name, role, engagement depth)                     │
  └─────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                   PRICING CALCULATION ENGINE                     │
  │                                                                  │
  │  Per-entity monthly pricing = f(gross revenue tier)              │
  │  Tier 1: <$1.5M  → 70% discount → $450/mo combined              │
  │  Tier 2: $1.5–3M → 50% discount → $750/mo combined              │
  │  Tier 3: $3–5M   → 30% discount → $1,050/mo combined            │
  │  Tier 4: $5M+    → Custom                                        │
  │                                                                  │
  │  Core: AI Bookkeeping ($750) + BI ($750) = $1,500/mo base        │
  │  Add-ons: Audit Ready + Books by 5th + Forecasting = $300/mo ea  │
  └─────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                  PPTX GENERATION ENGINE (pptxgenjs)              │
  │                                                                  │
  │  Slide 01 — Cover (Navy, brand bars, deal highlights)            │
  │  Slide 02 — Executive Summary (White + cyan accent)              │
  │  Slide 03 — Portfolio Overview (White + gold accent)             │
  │  Slide 04 — Problem: Multi-Vendor Trap (White + pink)            │
  │  Slide 05 — MEDDPIC Deal Intelligence (White + cyan)             │
  │  Slide 06 — Before / After Cost Comparison (White + gold)        │
  │  Slide 07 — Investment Summary by Tier (Offwhite + gold)         │
  │  Slide 08 — ROI Analysis (White + cyan)                          │
  │  Slide 09 — 3-Year Financial Model + Chart (White + cyan)        │
  │  Slide 10 — Optional Add-Ons (White + cyan)                      │
  │  Slide 11 — Platform Features (White + navy)                     │
  │  Slide 12 — Competitive Matrix (White + pink)                    │
  │  Slide 13 — SOX / Compliance Advantage (Navy dark slide)         │
  │  Slide 14 — Implementation Roadmap (White + gold)                │
  │  Slide 15 — Next Steps / Close Path (Navy dark slide)            │
  └─────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                          QA LAYER                                │
  │                                                                  │
  │  1. soffice.py --headless --convert-to pdf  (LibreOffice)        │
  │  2. pdftoppm -jpeg -r 100 output.pdf slide  (Poppler)            │
  │  3. Visual inspection of slide-NN.jpg per slide                  │
  │  4. Fix overflow, clipping, alignment issues                     │
  │  5. Re-generate → re-inspect (one fix cycle max)                 │
  └─────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                       OUTPUT                                     │
  │  Docyt_{Prospect}_Proposal_2026.pptx   → AE delivery             │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Sources & Tools

### 3.1 Grain AI Notetaker (MCP Integration)

**Purpose:** Extract deal intelligence, competitive stack details, and MEDDPIC signals from recorded sales calls.

**Tools used in this pipeline:**

```
Grain:list_meetings        — Find all external calls (participant_scope: "external")
Grain:list_meetings        — title_search filter for prospect name (e.g. "Coury", "hotel")
Grain:fetch_meeting_notes  — Retrieve AI-structured notes from most relevant meetings
Grain:search_meetings      — Semantic search across transcripts for specific topics
```

**Query pattern:**
```javascript
// Step 1: Find relevant meetings
Grain.list_meetings({ filters: { participant_scope: "external", title_search: "Coury" }, limit: 5 })

// Step 2: Fetch AI notes from top 2 meetings
Grain.fetch_meeting_notes({ meeting_id: "<uuid>" })

// Step 3: Optional deep search
Grain.search_meetings({
  search_queries: ["pricing proposal M3 ProfitSword replacement", "SOX compliance budget decision"],
  filters: { participant_scope: "external" }
})
```

**Key data extracted:**
- Current vendor stack (M3, ProfitSword, BirchStreet)
- Economic buyer name and authority level
- Contract expiry dates (ProfitSword → June 30)
- Pilot scope and go-live date (July 1, Hard Rock)
- Pain points mentioned verbatim
- Champion names and engagement signals
- Pricing discussed on calls

---

### 3.2 2026_Hotel_Pricing.xlsx

**Purpose:** Source of truth for Docyt's current hospitality pricing tiers.

**File location:** `/mnt/project/2026_Hotel_Pricing.xlsx`

**Parsing code:**
```python
import openpyxl

wb = openpyxl.load_workbook('/mnt/project/2026_Hotel_Pricing.xlsx')
ws = wb['Sheet1']
for row in ws.iter_rows(values_only=True):
    if any(c is not None for c in row):
        print(row)
```

**Extracted pricing model:**

| Module | Base Price | Tier 1 (<$1.5M) | Tier 2 ($1.5–3M) | Tier 3 ($3–5M) | Tier 4 ($5M+) |
|---|---|---|---|---|---|
| AI Bookkeeping | $750/mo | $225/mo | $375/mo | $525/mo | Custom |
| Business Intelligence | $750/mo | $225/mo | $375/mo | $525/mo | Custom |
| **Core Combined** | **$1,500/mo** | **$450/mo** | **$750/mo** | **$1,050/mo** | **Custom** |
| Audit Ready Financials | $300/mo | $90/mo | $150/mo | $210/mo | Custom |
| Books Closed by 5th | $300/mo | $90/mo | $150/mo | $210/mo | Custom |
| Advanced Forecasting | $300/mo | $90/mo | $150/mo | $210/mo | Custom |
| **All-In (Core + 3 Add-Ons)** | **$2,400/mo** | **$720/mo** | **$1,200/mo** | **$1,680/mo** | **Custom** |

> **Critical note:** The tier discount applies to the **max discount column** in the Excel — use the 4-tier framework (matching the $1.5M/$3M/$5M revenue breakpoints), not the 3-tier formula table. Document as a confirmable assumption in proposals.

---

### 3.3 pptxgenjs (Node.js)

**Purpose:** Generate production-quality PowerPoint decks programmatically.

**Install:**
```bash
npm install -g pptxgenjs react react-dom react-icons sharp
```

**Critical rules (learned from production use):**

```javascript
// ✅ CORRECT — never use # with hex colors
color: "FF6790"     // ← pptxgenjs, no hash
color: "#FF6790"    // ← CSS, NOT for pptxgenjs

// ✅ CORRECT — shadow factory function (pptxgenjs mutates objects in-place)
const mkShadow = () => ({ type:"outer", color:"000000", blur:8, offset:2, angle:135, opacity:0.10 });
// Use mkShadow() each call — never reuse the same object

// ✅ CORRECT — entity merge
Object.assign(entity, { tier: tierData })   // use tier:, never name: (overwrites entity name)

// ✅ CORRECT — LAYOUT_WIDE dimensions
pres.layout = "LAYOUT_WIDE";  // 13.3" × 7.5"
// Keep all content above y=7.0 to avoid footer clipping

// ✅ CORRECT — opacity in shadow
shadow: { type:"outer", blur:6, offset:2, color:"000000", opacity:0.12 }  // ← correct
shadow: { type:"outer", blur:6, offset:2, color:"00000020" }               // ← CORRUPTS FILE
```

---

### 3.4 LibreOffice + Poppler (QA)

**Purpose:** Convert `.pptx` to PDF, rasterize to JPEG for visual inspection.

```bash
# Convert to PDF
python3 /mnt/skills/public/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf output.pptx

# Clear stale images
rm -f slide-*.jpg

# Rasterize at 100 DPI (150 DPI for sharper QA)
pdftoppm -jpeg -r 100 output.pdf slide

# List generated files
ls -1 "$PWD"/slide-*.jpg
```

**Zero-padding note:** `pdftoppm` zero-pads based on total page count:
- 1–9 pages → `slide-1.jpg`
- 10–99 pages → `slide-01.jpg`
- 100+ pages → `slide-001.jpg`

---

## 4. Pricing Framework

### Tier Structure

```
Revenue Band          Discount    Core (AI Bookkeeping + BI)    All-In (+3 Add-Ons)
─────────────────────────────────────────────────────────────────────────────────────
Tier 1: < $1.5M/yr    70% off     $450/mo per entity            $720/mo per entity
Tier 2: $1.5M–$3M/yr  50% off     $750/mo per entity            $1,200/mo per entity
Tier 3: $3M–$5M/yr    30% off     $1,050/mo per entity          $1,680/mo per entity
Tier 4: > $5M/yr      Custom      Custom                        Custom
```

### ACV Calculation

```
ACV = Σ (entities × applicable monthly rate × 12)

Example — Coury Hospitality (43 entities, mixed Tier 3/4):
  ~20 entities @ Tier 3 ($1,050/mo) = $20 × $1,050 × 12 = $252,000
  ~23 entities @ Tier 4 (custom ~$1,350/mo) = $23 × $1,350 × 12 = $373,500
  Gross list price = ~$625,500
  Negotiated to: $700,000 (includes add-ons + services)
  Discounted from list: $750,000 → $700,000 (confirmed in Grain notes)
```

### Optional Add-Ons — What's Included

| Add-On | Features | Best For |
|---|---|---|
| **Audit Ready Financials** | Daily income journal recon · Vendor accruals · Intercompany recon · Advanced payroll accounting · Documentary evidence | SOX compliance · Audit prep |
| **Books Closed by 5th** | PDF statement scraping · Recon by 2nd–3rd · Executive summary in mgmt package | CFO reporting · Fast close |
| **Advanced Forecasting** | Revenue forecast by segment · 12-wk cash flow · Labor forecasting · Delphi/OTB integration | Revenue management · M&A modeling |

---

## 5. MEDDPIC Intelligence Layer

### What MEDDPIC Signals to Extract from Grain

When fetching meeting notes, map the content to these 7 dimensions:

```
M — METRICS
  • ACV (confirmed or estimated)
  • Number of properties / entities
  • Current stack cost (software + labor)
  • Month-end close cycle time
  • Growth metrics (M&A pipeline, new properties)
  • Compliance deadlines (SOX, audit dates)

E — ECONOMIC BUYER
  • Name, title, seniority
  • Who has final signature authority
  • Board/ownership visibility
  • Whether they attend calls directly

D — DECISION CRITERIA (ranked)
  • Compliance readiness (SOX/SOC 2)
  • Price vs current stack
  • Automation depth / feature parity
  • Implementation timeline
  • Integration requirements

D — DECISION PROCESS
  • Pilot structure (which property, duration)
  • Review milestones (dates + owners)
  • Contract review chain
  • Go-live dependency (contract expiry, fiscal year)

P — PAPER PROCESS
  • Current contract status (signed / pending / drafting)
  • Key clauses (cancellation, start date)
  • Materials requested (SOC 2, security questionnaire)
  • COA / data delivery commitments

I — IDENTIFIED PAIN (verbatim from calls)
  • System fragmentation (# of vendors)
  • Manual reconciliation volume
  • Reporting lag
  • Compliance gaps
  • Scale limitations

C — CHAMPION
  • Name, role, day-to-day ownership
  • Frequency of engagement (attends all calls?)
  • Internal advocacy signals
  • Data delivery ownership
```

### Grain Search Strategy

```javascript
// Most efficient query pattern (from production experience):
// 1. Filter by participant_scope: "external" to get prospect calls only
// 2. Use title_search: "[prospect name]" to narrow to account
// 3. Fetch notes from top 2 meetings (onboarding/commercial + systems integration)

// Highest-value meeting types for MEDDPIC:
//   "Docyt // [Company]"           — commercial/pricing call
//   "Docyt onboarding timelines"   — implementation + contract discussion
//   "Systems Integration"          — competitive stack details
```

---

## 6. Proposal Structure — 15-Slide Playbook

| Slide | Title | Accent Color | Primary Content |
|---|---|---|---|
| 01 | Cover | Navy bg | Deal headline, ACV, entity count, go-live date, systems replaced |
| 02 | Executive Summary | Cyan top | 6-pillar summary cards — SOX, Cost, Consolidation, Real-Time, Scale, Pilot |
| 03 | Portfolio Overview | Gold top | Property/entity stats, M&A context, stakeholder map, contract window |
| 04 | The Problem | Pink top | Current 3-vendor stack visual + 6 identified pain points |
| 05 | MEDDPIC Intelligence | Cyan top | 7-row MEDDPIC table sourced from Grain notes |
| 06 | Before / After Cost | Gold top | Side-by-side cost architecture: current stack vs Docyt all-in |
| 07 | Investment Summary | Gold top | 4 tier cards with discount badges + add-ons breakdown |
| 08 | ROI Analysis | Cyan top | 4 ROI callouts + 3-year benefit/investment table |
| 09 | 3-Year Financial Model | Cyan top | Native bar chart (pptxgenjs) + M&A scaling scenarios |
| 10 | Optional Add-Ons | Cyan top | 3 add-on detail cards with feature bullets |
| 11 | Platform Features | Navy top | 4-quadrant feature grid (accounting, revenue, reporting, BI) |
| 12 | Competitive Matrix | Pink top | Feature comparison table vs M3, ProfitSword, QuickBooks |
| 13 | SOX Compliance | Navy bg (dark) | 6 SOX/compliance advantage cards |
| 14 | Implementation Roadmap | Gold top | 4-phase timeline with milestones and owners |
| 15 | Next Steps / Close | Navy bg (dark) | 5 numbered action items with dates and owners + CTA bar |

---

## 7. Branding Guidelines — Docyt Brand System

### Color Palette

```javascript
const BRAND = {
  navy:     "0D1B40",   // Primary background (cover, dark slides, emphasis)
  cyan:     "03C5D7",   // Data/BI slides, top accent bars, CTAs
  pink:     "FF6790",   // Problem/contrast slides, pain-point framing
  gold:     "F5C842",   // Commercial/action slides, pricing highlights
  white:    "FFFFFF",   // Content slide backgrounds
  offwhite: "F8F9FC",   // Card fills, secondary backgrounds
  charcoal: "1E2B3C",   // Body text on light backgrounds
  slate:    "4A5568",   // Secondary text, descriptions
  muted:    "718096",   // Captions, footnotes
  border:   "E2E8F0",   // Card borders, dividers
};
```

### Color Assignment Rules

| Slide Type | Background | Accent Bar | Card Fill |
|---|---|---|---|
| Cover | Navy (`0D1B40`) | Brand bars (gold/pink/cyan) | N/A |
| Data / BI slides | White | Cyan | Light blue (`EDF9FB`) |
| Problem / contrast | White | Pink | Pink tint (`FFF5F7`) |
| Commercial / pricing | White or Offwhite | Gold | Offwhite |
| Emphasis / compliance | Navy | Cyan left rail | Dark navy card (`162550`) |
| Close / next steps | Navy | Brand bars | Dark card (`162550`) |

### Logo Construction

Docyt's logo is constructed from:
1. **Three colored bars** (left side): Gold → Pink → Cyan (vertical rectangles, `rx=3` rounded, 12px wide, 4px gap)
2. **Wordmark**: `"docyt"` in Arial Black / bold, 36pt, adjacent to bars
3. **Dark bg version**: White wordmark
4. **Light bg version**: Navy wordmark (`0D1B40`)

```javascript
// SVG logo construction (no external file required)
const logoSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 60">
  <rect x="0"  y="8" width="12" height="44" rx="3" fill="#F5C842"/>
  <rect x="16" y="8" width="12" height="44" rx="3" fill="#FF6790"/>
  <rect x="32" y="8" width="12" height="44" rx="3" fill="#03C5D7"/>
  <text x="54" y="46" font-family="Arial Black, Arial" font-weight="900"
        font-size="36" fill="#FFFFFF" letter-spacing="-1">docyt</text>
</svg>`;
const logoB64 = "image/svg+xml;base64," + Buffer.from(logoSvg).toString("base64");

// Embed on slide (dark bg):
slide.addImage({ data: logoB64, x: 0.3, y: 0.15, w: 1.4, h: 0.32 });
```

### Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Slide headline | Calibri | 26–40pt | Bold |
| Section header | Calibri | 14–18pt | Bold |
| Card title | Calibri | 10–13pt | Bold |
| Body text | Calibri | 9–11pt | Regular |
| Caption / footnote | Calibri | 7.5–9pt | Regular / Italic |
| Big stat callout | Calibri | 34–40pt | Bold |

---

## 8. Scripts & Code

### 8.1 Main Proposal Generator

**File:** `coury_proposal.js`  
**Runtime:** Node.js  
**Dependencies:** `pptxgenjs`

```bash
# Run
node coury_proposal.js

# Output
# ✅  Deck written: Docyt_Coury_Hospitality_Proposal_2026.pptx
```

**Script structure:**

```javascript
// ─── 1. CONSTANTS ────────────────────────────────────────────────────────────
const C = { navy:"0D1B40", cyan:"03C5D7", pink:"FF6790", gold:"F5C842", ... };

// ─── 2. HELPERS ──────────────────────────────────────────────────────────────
const mkShadow = () => ({ type:"outer", color:"000000", blur:8, offset:2, angle:135, opacity:0.10 });
function addLogoLight(slide, x, y, w, h) { ... }
function addLogoDark(slide, x, y, w, h) { ... }
function addFooter(slide, text, dark) { ... }

// ─── 3. PRESENTATION INIT ────────────────────────────────────────────────────
let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";   // 13.3" × 7.5"

// ─── 4. SLIDES 1–15 ──────────────────────────────────────────────────────────
// Each slide in a scoped block: { let s = pres.addSlide(); ... }

// ─── 5. WRITE ────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "output.pptx" });
```

### 8.2 Pricing Data Reader

```python
#!/usr/bin/env python3
"""Read 2026 Hotel Pricing Excel and extract tier structure."""
import openpyxl

def extract_pricing(path="/mnt/project/2026_Hotel_Pricing.xlsx"):
    wb = openpyxl.load_workbook(path)
    ws = wb['Sheet1']
    
    tiers = {}
    modules = []
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1] == '/mo' and row[2]:
            module_name = row[2]
            base_price = row[0]
            # Discounts: col D=Tier1, E=Tier2, F=Tier3
            discounts = { 'tier1': row[3], 'tier2': row[4], 'tier3': row[5] }
            modules.append({
                'name': module_name,
                'base': base_price,
                'tier1_price': base_price * (1 - discounts['tier1']),
                'tier2_price': base_price * (1 - discounts['tier2']),
                'tier3_price': base_price * (1 - discounts['tier3']),
            })
    
    return modules

if __name__ == "__main__":
    for m in extract_pricing():
        print(f"{m['name']:30s}  T1=${m['tier1_price']:.0f}  T2={m['tier2_price']:.0f}  T3={m['tier3_price']:.0f}")
```

### 8.3 Grain MEDDPIC Extractor (Pseudo-code)

```javascript
/**
 * Extracts MEDDPIC signals from Grain meeting notes for a given prospect.
 * Requires Grain MCP connection in Claude.ai.
 *
 * @param {string} prospectName - e.g. "Coury"
 * @returns {object} meddpic - structured MEDDPIC object
 */
async function extractMEDDPIC(prospectName) {
  // 1. Find prospect meetings
  const meetings = await Grain.list_meetings({
    filters: { participant_scope: "external", title_search: prospectName },
    limit: 5
  });

  // 2. Fetch notes from top 2 meetings (most recent + most relevant)
  const notes = await Promise.all(
    meetings.list.slice(0, 2).map(m => Grain.fetch_meeting_notes({ meeting_id: m.id }))
  );

  // 3. Parse MEDDPIC from combined notes text
  const combined = notes.map(n => n.content).join("\n\n");

  return {
    metrics:        extractSection(combined, ["ACV", "properties", "entities", "deadline", "close cycle"]),
    economicBuyer:  extractSection(combined, ["CFO", "VP", "board", "contract", "decision maker"]),
    decisionCriteria: extractSection(combined, ["SOX", "price", "automation", "go-live", "integration"]),
    decisionProcess: extractSection(combined, ["pilot", "review", "timeline", "rollout", "cutover"]),
    paperProcess:   extractSection(combined, ["contract", "signed", "clause", "COA", "materials"]),
    identifiedPain: extractSection(combined, ["pain", "problem", "manual", "fragmented", "slow"]),
    champion:       extractSection(combined, ["champion", "controller", "attends", "owns"]),
  };
}
```

### 8.4 QA Automation Script

```bash
#!/bin/bash
# qa_deck.sh — Full visual QA pipeline for any pptxgenjs-generated deck
# Usage: ./qa_deck.sh MyDeck.pptx

PPTX="$1"
PDF="${PPTX%.pptx}.pdf"

echo "► Converting to PDF..."
python3 /mnt/skills/public/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf "$PPTX"

echo "► Rasterizing slides..."
rm -f slide-*.jpg
pdftoppm -jpeg -r 100 "$PDF" slide

echo "► Slides generated:"
ls -1 "$PWD"/slide-*.jpg | nl

echo "► Done. Inspect slide-NN.jpg files for visual defects."
echo "  Common issues to check:"
echo "  - Footer overlapping last content element"
echo "  - Text overflowing card boundaries"
echo "  - Elements below y=7.0 (LAYOUT_WIDE clipping)"
echo "  - Low-contrast text on colored backgrounds"
```

---

## 9. QA Process

### Visual QA Checklist (run after every generation)

```
□ Slide 1  — Cover: All 4 deal stats visible, logo renders, no clipping below y=7.0
□ Slide 2  — Exec Summary: All 6 cards visible, summary paragraph not cut off
□ Slide 3  — Portfolio: 4 stat cards fully visible, deal context rows complete
□ Slide 4  — Problem: 3 vendor cards + 6 pain cards all visible
□ Slide 5  — MEDDPIC: All 7 rows (M/E/D/D/P/I/C) clear, no footer overlap
□ Slide 6  — Before/After: Both columns fully visible, totals row visible
□ Slide 7  — Tiers: All 4 tier cards + 3 add-on cards visible
□ Slide 8  — ROI: 4 callout cards + full table rows visible
□ Slide 9  — 3-Yr Model: Chart renders, sidebar scenarios visible
□ Slide 10 — Add-Ons: All 3 add-on cards with 6 bullets each visible
□ Slide 11 — Features: All 4 quadrant cards + bullet rows visible
□ Slide 12 — Matrix: All rows and columns, Y/✗/~ symbols clear, no cell overflow
□ Slide 13 — SOX: All 6 dark cards visible on navy background
□ Slide 14 — Roadmap: All 4 phase columns + 6 items per column visible
□ Slide 15 — Close: All 5 action steps clear, CTA bar not overlapping step 5
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| Footer overlapping content | Content rows pushed too low | Reduce `y` spacing between rows or reduce row height |
| Text overflowing card | Text too long for allocated height | Reduce font size, increase card height, or truncate text |
| Slide 15 step 5 cuts into CTA bar | CTA bar `y` too high | Move CTA bar down to `y=6.55` |
| Tier 4 shows "Custom OFF" | `disc` field value literal | Add logic: `if(disc==="Custom") return "Custom"` |
| Shadow corruption | Reused shadow object | Always use `mkShadow()` factory function |
| Colors render as black | `#` prefix on hex color | Remove all `#` prefixes from hex colors |

---

## 10. Deal Reference — Coury Hospitality

### Deal Summary

```
Account:        Coury Hospitality (couryh.com)
HQ:             Dallas, TX
Portfolio:      15 properties, 43–45 entities (all provisioned in Docyt)
Pilot property: Hard Rock Hotel Dallas (complex full-service flagship)
ACV:            $700,000/year (discounted from $750,000 list)
Status:         Implementation contract signed; subscription contract pending
Go-live target: July 1, 2026 (Hard Rock)
Full rollout:   Q3–Q4 2026 (all 15 properties)
M&A upside:     86-property acquisition in progress → potential ~$3.5M ACV
```

### Stakeholders

| Name | Role | Scope |
|---|---|---|
| Dustin ODonnell | CFO/VP — Economic Buyer | dodonnell@couryh.com |
| Bo Patel | Owner/Stakeholder | bo@couryh.com |
| Jessica Lamont | Controller — Champion | jlamont@couryh.com |
| Sidharth Saxena | Docyt CEO — AE | sid@docyt.com |
| Rahul Kumar | Dir. Strategic Partnerships | rahul@docyt.com |
| Radhika Makwana | Onboarding Lead | radhika.makwana@docyt.com |
| Sugam Pandey | Engineering Lead | sugam@docyt.com |

### Systems Being Replaced

| System | Purpose | Replaced By |
|---|---|---|
| M3 | GL accounting | Docyt AI Bookkeeping module |
| ProfitSword / Actabl | BI & forecasting | Docyt Business Intelligence + Advanced Forecasting |
| (BirchStreet retained) | AP/bill payments (Avendra rebate) | Integration — Docyt pulls bills, marks as paid |

### Integration Roadmap

```
Dayforce        — Payroll/time clock API (in validation)
BirchStreet     — AP integration (Tyler Garrett contact)
Delphi          — Forecasting data (priority: Hard Rock)
Marriott OTB    — Forward-looking occupancy data
Hilton OTB      — Forward-looking occupancy data
PMS (Hard Rock) — Revenue feed into Docyt
Bank feeds      — All 43 entities (pending activation)
```

### Key Dates

```
May 8     — Jessica delivers Hard Rock COA to Docyt
May 22    — System review call (Dustin + Docyt team)
May–June  — On-site engineering deployment, Dallas (1–2 weeks)
June 1    — Parallel run begins
June 30   — ProfitSword contract ends
July 1    — Hard Rock go-live (HARD deadline)
Q3 2026   — Full 15-property rollout
Q4 2026   — SOX audit (Docyt simplifies vendor surface)
```

---

## 11. Reuse Guide — How to Generate the Next Proposal

### Step-by-Step

**1. Gather inputs**

```
□ Prospect name and HQ location
□ Number of properties and entities
□ Current accounting stack (ask: "What do you use for accounting and BI today?")
□ Key pain points (from discovery call)
□ Economic buyer name and title
□ Champion name and title
□ Deal stage and next milestone
□ Any confirmed contract or pilot details
```

**2. Pull Grain intelligence**

```
Grain.list_meetings({ filters: { participant_scope: "external", title_search: "[ProspectName]" }, limit: 5 })
Grain.fetch_meeting_notes({ meeting_id: "[most_recent_commercial_call_id]" })
Grain.fetch_meeting_notes({ meeting_id: "[systems_integration_call_id]" })
```

**3. Calculate pricing**

```
For each property/entity:
  → Estimate gross revenue per property
  → Assign tier (1–4)
  → Apply tier discount to $1,500/mo base
  → Add applicable add-ons ($300/mo each)
  → Sum × 12 = ACV

Apply enterprise discount based on total ACV and strategic value.
```

**4. Update the script**

Change these variables in `coury_proposal.js`:

```javascript
// Slide 1 — Cover
"Enterprise Pricing Proposal"            // title
"[Prospect Name]  ·  [N] Properties  ·  [City, ST]"  // subtitle
["$[ACV]", "[N] entities", "[Go-Live]", "[Stack Replaced]"]  // highlights

// Slide 3 — Portfolio
stats = [N properties, N entities, ...]

// Slide 5 — MEDDPIC
meddpic = [ ... from Grain notes ... ]

// Slide 6 — Before/After
beforeItems = [ ... current stack line items ... ]

// Slide 15 — Next Steps
steps = [ ... specific actions with dates and owners ... ]
```

**5. Run and QA**

```bash
node proposal.js
./qa_deck.sh output.pptx
# Fix any visual defects
# Copy to /mnt/user-data/outputs/
```

---

## 12. File Index

```
docyt-pricing-proposal-system/
│
├── README.md                                  ← This file
│
├── scripts/
│   ├── coury_proposal.js                      ← Main pptxgenjs generator (Coury Hospitality)
│   ├── pricing_reader.py                      ← Excel pricing model parser
│   └── qa_deck.sh                             ← Visual QA automation script
│
├── data/
│   └── 2026_Hotel_Pricing.xlsx               ← Source of truth for pricing tiers (read-only)
│
├── output/
│   └── Docyt_Coury_Hospitality_Proposal_2026.pptx  ← Final deliverable
│
└── docs/
    ├── brand_colors.md                        ← Docyt color reference
    ├── meddpic_template.md                    ← MEDDPIC extraction template
    └── slide_design_rules.md                  ← Slide layout conventions
```

---

## Appendix A — Competitive Positioning Reference

| Capability | Docyt | M3 | ProfitSword | QuickBooks |
|---|---|---|---|---|
| AI-Powered GL Coding | ✓ | ~ | ✗ | ✗ |
| Real-Time Revenue Reconciliation | ✓ | ✗ | ~ | ✗ |
| USALI 11th Edition Reporting | ✓ | ✓ | ~ | ✗ |
| 30+ Native PMS Integrations | ✓ | ~ | ~ | ✗ |
| Daily Flash Revenue Report | ✓ | ✗ | ~ | ✗ |
| Labor Cost Forecasting | ✓ | ✗ | ✓ | ✗ |
| SOC 2 Type 2 Certified | ✓ | ✓ | ✓ | ✓ |
| Single-Vendor SOX Surface | ✓ | ✗ | ✗ | ✗ |
| Automated Month-End Close | ✓ | ~ | ✗ | ✗ |
| Multi-Entity Portfolio View | ✓ | ✓ | ✓ | ~ |
| M&A Portfolio Scalability | ✓ | ~ | ~ | ✗ |
| Built-in Business Managers | ✓ | ✗ | ✗ | ✗ |

---

## Appendix B — ROI Model Assumptions

```
Direct software savings:    M3 + ProfitSword (estimated) vs Docyt ACV
Labor efficiency:           2 FTE redeployed from manual reconciliation work
                            Assumed at $70K/FTE = $140K/year
Revenue leakage recovery:   1% of gross revenue caught by daily reconciliation
                            Coury (15 props × $5M avg) = ~$750M portfolio × 1% = $150K+/yr
SOX simplification:         External audit cost reduction (2 fewer vendor SOX audits)
                            Estimated at $60K–$90K/year saved

M&A multiplier (Yr 2–3):    All scaling assumptions use Docyt entities already provisioned.
                            No re-implementation cost for acquired properties.
                            Per-property cost declines at scale (volume discount territory).
```

---

*Document maintained by Docyt Revenue Operations. Update pricing assumptions quarterly against `2026_Hotel_Pricing.xlsx`. Update competitive matrix as M3/ProfitSword/Actabl release new features.*

*For deal-specific questions: rahul@docyt.com | sid@docyt.com*
