# Vireo Audio Support Analytics — Executive Dashboard Specification

**Document Version:** 1.0  
**Phase:** 4A Executive Dashboard Implementation  
**Audience:** Leadership (Priya Raman), Engineering, and Quality Auditors  
**Architecture:** Zero-Dependency Lightweight Vanilla Web Application  

---

## 1. Dashboard Architecture

The executive dashboard is implemented as a production-grade, zero-dependency client application powered by a deterministic metrics pipeline.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES (outputs/)                         │
│  agent_metrics.csv | peer_metrics.csv | training_candidates.csv       │
│  raw_bottom10.csv  | policy_exceptions.csv | ai_ticket_audit.json      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 EXPORTER / ENGINE (src/export_dashboard_data.py)        │
│  Serializes validated pipeline outputs into JSON & global JS payload   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
               dashboard/data.json     dashboard/data.js
                         │                     │
                         └──────────┬──────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND PRESENTATION LAYER                        │
│  dashboard/index.html (Semantic Structure, 8 Modular Views)            │
│  dashboard/style.css  (Executive Visual Hierarchy, Responsive Grid)    │
│  dashboard/app.js     (Client Controller, Dynamic State & Inspector)  │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Strengths:
1. **Zero External Dependencies:** Built with Vanilla HTML5, CSS3, and JavaScript. No Node.js, React, Webpack, Tailwind, or complex build toolchains required.
2. **Offline & Zero-CORS Resilient:** Data is provided via both `dashboard/data.js` (`window.VIREO_DATA`) and `dashboard/data.json`, allowing the application to run seamlessly either via a simple HTTP server (`python serve.py`) or by double-clicking `index.html` directly in any web browser.
3. **Strict Decoupling:** Business logic and mathematical derivations reside exclusively in `src/metrics_engine.py`. The frontend strictly presents pre-calculated, verified data and never invents ad-hoc scoring formulas.

---

## 2. Information Architecture & Screens

The dashboard delivers 8 purpose-built views accessible via the executive navigation bar:

### View 1: Executive Summary (Landing View)
- **Primary Business Target:** First-response SLA breach reduction.
- **Historical Baseline:** 1,064 breaches over 18 months; ₹3,72,400 store-credit penalty liability.
- **Modeled Savings Scenarios:**
  - Conservative (25% reduction): **₹62,067 / year** (177.3 breaches avoided)
  - Recommended (50% reduction): **₹1,24,133 / year** (354.7 breaches avoided)
  - Aggressive (75% reduction): **₹1,86,200 / year** (532.0 breaches avoided)
  - *Explicit Label:* `MODELED SCENARIOS — NOT GUARANTEED SAVINGS`
- **Process-Control Discovery:** 131 double-dipped orders, ₹5.91L historical exposure (clearly labeled `HISTORICAL PROCESS-CONTROL EXPOSURE`, not training ROI).
- **Executive Recommendation:** Prioritize the 10 evidence-backed training candidates across 3 targeted tracks.

### View 2: Priya's Requested Raw View ("Raw Contractual Ranking")
- Preserves leadership's requested contractual perspective:
  - **Table A:** Bottom 10 by Raw Mean CSAT (unadjusted).
  - **Table B:** Highest 10 by Audited Median Handle Time (unadjusted).
- **Mandatory Bias Callouts:** Every row displays a contextual queue-bias explanation explaining why raw metrics are structurally misleading.
- **Disclaimers:** Explicitly states that raw rankings are shown for transparency, but do not represent sound training decisions.

### View 3: Fair Recommended Shortlist (Decision View)
- Displays exactly the **10 candidates** from `outputs/training_candidates.csv`.
- Structured across 3 operational modules:
  - **Track 1 (7 Agents):** SLA Responsiveness & Queue Discipline (`A3003`, `A3002`, `A3016`, `A3021`, `A3030`, `A3035`, `A3028`).
  - **Track 2 (2 Agents):** Queue-Normalized Communication (`A3020`, `A3029`).
  - **Track 3 (1 Agent):** Advanced RMA Diagnostics & Turnaround (`A3041`).
- Columns include: Rank, Agent Name, ID, Team, Track, Primary Evidence, Peer Benchmark, Audit Rationale, Recommended Action.

### View 4: Agent Inspector
- Allows deep-dive inspection into all **44 support agents**.
- Full 29-metric profile with clear separation of **RAW** vs. **AUDITED / NORMALIZED**:
  - Raw CSAT vs. Peer Mean CSAT vs. Empirical Bayes Shrunk CSAT.
  - Raw Handle Time vs. Audited Handle Time (+5:30 offset corrected).
  - SLA breaches, breach rate, contractual penalty liability.
  - Operational touchpoints: transfers, replacements, refunds, double-dipped tickets touched.
- Dynamic legacy offset notice highlighting agents affected by the Freshdesk UTC/IST migration issue.

### View 5: Why Not the Raw Bottom 10?
- Visual and structural breakdown explaining why naive rankings punish good agents.
- **Focus on Kavya's Four (`A3004`, `A3005`, `A3006`, `A3007`):** Explains that their raw CSAT (~2.98–3.04) was depressed by the Pulse 2 batch battery defect flood (lots `PL2-2508-2` to `PL2-2511-3`) where they handled double the baseline rate of dead earbuds.
- **Tier 2 Escalations Context:** Explains why comparing 75–120 hour bench repair turnarounds with 15-minute chat resets is statistically invalid.

### View 6: Business Impact & Sensitivity Analysis
- **Card A (Training / SLA Opportunity):** Interactive scenario toggle (25%, 50%, 75%) recalculating annual modeled savings and avoided breaches.
- **Card B (Process Control):** Breakdown of ₹590,934 historical double-dipping exposure (₹355,434 cash refunds + ₹235,500 replacement policy cost). Clearly framed as an IT system control opportunity.

### View 7: AI Qualitative Diagnostics (Auxiliary Layer)
- Evaluates the 100-ticket qualitative audit.
- Agreement breakdown against independent 20-ticket human expert gold standard:
  - Policy signal: **100.0%** (20/20)
  - Agent handling signal: **80.0%** (16/20)
  - Resolution quality: **65.0%** (13/20)
  - Evidence quality: **65.0%** (13/20)
  - Primary root cause: **45.0%** (9/20)
  - Exact all-field concordance: **30.0%** (6/20) across all 5 dimensions simultaneously.
- Visible guardrail warning: *"AI diagnostics do not determine agent ranking, training selection, CSAT, handle time, or financial calculations."*
- Hallucination and correction table displaying cases where human audit adjusted AI inferences.

### View 8: Data Quality Register & Limitations
- Concise interactive accordion detailing all 10 documented limitations:
  1. Legacy Timestamp Reconstruction (+5:30 offset).
  2. Voluntary CSAT Response Bias (44.22% response rate).
  3. Premature CSAT on Open/Pending Tickets (249 tickets).
  4. Missing Order ID Linkage (4,107 tickets / 34.95%).
  5. Agent Name Collision (`Kavya Pandey` across A3006 & A3029).
  6. Voice IVR Speech-to-Text Transcription Artifacts.
  7. Category "Other" Miscategorization (1,732 tickets / 14.74%).
  8. Transfer-Field Migration Discrepancy.
  9. Queue / Case-Mix Selection Effects.
  10. AI Qualitative Uncertainty (30% exact all-field agreement).

---

## 3. How to Run the Dashboard

### Method 1: Using `serve.py` (Recommended)
From the project root:
```powershell
python serve.py
```
This automatically updates `dashboard/data.js` and launches the dashboard at `http://localhost:8501`.

To run on a custom port:
```powershell
python serve.py --port 8080
```

### Method 2: Standard Python HTTP Server
```powershell
python -m src.export_dashboard_data
python -m http.server 8501 --directory dashboard
```

### Method 3: Direct Browser Launch (Zero-Server Offline)
Double-click `dashboard/index.html` or open it directly in Google Chrome, Microsoft Edge, Firefox, or Safari. The included `dashboard/data.js` provides immediate data availability without CORS restrictions.

---

## 4. How to Test

Run the full automated test suite:
```powershell
python -m pytest tests/ -v
```

All 41 tests will execute across:
- Data loader integrity (`tests/test_data_loader.py`)
- Metrics engine & formulas (`tests/test_metrics_engine.py`)
- AI auditor & prompt constraints (`tests/test_ai_auditor.py`)
- Quality gate & consistency benchmarks (`tests/test_quality_gate.py`)
- Dashboard testability & data integrity (`tests/test_dashboard.py`)
- Full validation pipeline (`tests/test_validation.py`)
