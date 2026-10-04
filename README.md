# Vireo Audio Support Analytics & Executive Decision System

**Project:** Task 1 V4 — Vireo Audio — Support Tickets (Set B)  
**Role:** Lead Data Analyst & Engineering Architect  
**Audience:** Priya Raman, Director of Customer Support  
**Status:** Certified & Production-Ready (Phase 4C)  
**Test Suite:** 43 / 43 Automated Tests Passing (100%)  

---

## Executive Overview

This repository provides an end-to-end, evidence-backed decision support system designed to evaluate customer support performance across 11,750 historical tickets and 44 active support agents.

The core objective is to answer:
> **"Who should I retrain, why, and what business outcome does the intervention target?"**

The system preserves leadership's requested **Raw Contractual Bottom 10** view while delivering a **Fair Recommended Shortlist** that neutralizes operational queue bias (e.g., Tier 2 technical escalations and the Pulse 2 batch defect surge).

---

## Key Baseline Metrics (Single Source of Truth)

- **Audit Dataset:** 11,750 support tickets across 18 months (1 January 2025 to 30 June 2026).
- **Roster:** 44 active agents across 6 operational peer groups.
- **CSAT Feedback:** 5,196 survey responses (44.22% response rate; company mean 3.3266).
- **Historical SLA Breaches:** 1,064 breaches, generating **₹3,72,400** in contractual store-credit penalties.
- **Annualized SLA Breach Liability:** **₹2,48,267 / year** (709.3 breaches / year).
- **Targeted Training Opportunity:** 50% breach reduction targets **₹1,24,133 / year** in modeled savings (354.7 breaches avoided).
- **Process-Control Discovery (Double Dipping):** 131 distinct orders received both a refund (₹355,434) and replacement unit (₹235,500 policy cost), totaling **₹5,90,934** in historical exposure (annualized ₹3,93,956/year). Formally classified as an IT/ERP validation-rule opportunity, *not* training ROI.
- **Recommended Training Shortlist:** Exactly 10 candidates grouped across 3 diagnostic modules.
- **Queue Bias Protection:** Frontline agents on the hardware triage rota (`A3004`, `A3005`, `A3006`, `A3007`) are protected against unwarranted training shortlisting.

---

## Quickstart Guide (Clean Machine Reproduction)

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- No paid API keys or remote accounts required.

### 2. Installation
Clone the repository and install the minimal dependencies:
```powershell
pip install -r requirements.txt
```
*(Dependencies: `pandas>=2.0.0`, `numpy>=1.24.0`, `pytest>=7.0.0`)*

### 3. Run the Analytics Pipeline
To re-run the complete deterministic metrics calculation, dashboard data export, and validation check from scratch:
```powershell
# 1. Execute deterministic metrics engine (generates outputs/ CSVs)
python -m src.metrics_engine

# 2. Export validated datasets to dashboard
python -m src.export_dashboard_data

# 3. Run full metrics parity validation
python -m src.validation

# 4. (Optional) Re-render Executive Memo PDF
python -m src.render_memo_pdf
```

### 4. Run the Dashboard
Launch the lightweight executive web dashboard:
```powershell
python serve.py
```
Open your browser to:
```
http://localhost:8501
```

*(Optional: You may also specify a custom port with `python serve.py --port 8080`, or open `dashboard/index.html` directly in any web browser without a web server).*

### 5. Run the Test Suite
Execute all 43 unit, integration, and quality-gate tests:
```powershell
python -m pytest tests/ -v
```
Expected output: `43 passed in ~10s`.

---

## Dashboard Information Architecture

The dashboard comprises 8 purpose-built executive views:

1. **View 1 — Executive Summary:** Strategic KPI overview, historical SLA breach baseline, modeled sensitivity scenarios (25%, 50%, 75%), process-control discovery, and management recommendations.
2. **View 2 — Raw Contractual View:** Leadership's requested unadjusted ranking (Bottom 10 by CSAT and Highest 10 by Handle Time), annotated with transparent queue-bias context warnings.
3. **View 3 — Fair Recommended Shortlist:** The 10 evidence-backed training candidates grouped into:
   - *Track 1 (7 Agents):* SLA Responsiveness & Queue Discipline (`A3003`, `A3002`, `A3016`, `A3021`, `A3030`, `A3035`, `A3028`).
   - *Track 2 (2 Agents):* Queue-Normalized Communication (`A3020`, `A3029`).
   - *Track 3 (1 Agent):* Advanced RMA Diagnostics (`A3041`).
4. **View 4 — Agent Detail Inspector:** Interactive drill-down into all 44 agents displaying all 29 metrics with clear RAW vs. AUDITED / NORMALIZED separation, peer benchmarks, and legacy UTC/IST offset notes.
5. **View 5 — Why Not the Raw Bottom 10?:** Clear visual explanation of why naive rankings punish good performers; detailed case study on "Kavya's Four" and the Pulse 2 battery defect surge.
6. **View 6 — Business Impact & Sensitivity Analysis:** Interactive scenario selector for SLA savings alongside breakdown of the ₹5.91L double-dipping process-control opportunity.
7. **View 7 — AI Qualitative Diagnostics (Auxiliary Layer):** Qualitative triage results across 100 tickets, benchmark agreement analysis (30% exact all-field concordance), visible guardrail warnings, and human supervisory correction log.
8. **View 8 — Data Quality Register & Limitations:** Interactive accordion documenting the 10 known operational limitations, impacts, pipeline mitigations, and residual risks.

---

## Repository Structure

```
vireo-support-shortlisting/
├── data/                             # Raw source CSV data (IMMUTABLE)
│   ├── agents.csv                    # 44 support agents
│   ├── customers.csv                 # 5,000 customers
│   ├── orders.csv                    # 10,000 order transactions
│   ├── products.csv                  # 7 product SKUs & costs
│   └── tickets.csv                   # 11,750 support interactions
├── reference/                        # Operational reference files (IMMUTABLE)
│   ├── README.txt                    # Assignment specification
│   ├── email-thread.txt              # Stakeholder correspondence (Priya Raman)
│   └── support-policy.pdf            # Vireo Support Policy v3.2
├── src/                              # Core Deterministic Analytics Engine
│   ├── config.py                     # Constants, SLA rules, policy costs
│   ├── data_loader.py                # Schema validation & referential integrity
│   ├── metrics_engine.py             # Calculations, shrinkage, peer groups
│   ├── ai_auditor.py                 # 100-ticket qualitative diagnostic auditor
│   ├── export_dashboard_data.py      # Serializer for dashboard/data.js
│   └── validation.py                 # Metric parity validator
├── dashboard/                        # Zero-Dependency Executive Dashboard
│   ├── index.html                    # Semantic HTML5 markup (8 views)
│   ├── style.css                     # Executive styling & responsive grid
│   ├── app.js                        # Client controller & interaction handlers
│   ├── data.js                       # Authoritative global data store (zero-CORS)
│   └── data.json                     # JSON format of validated metrics
├── outputs/                          # Certified Analytical Deliverables
│   ├── data_audit.md                 # 43KB initial exploratory audit
│   ├── methodology.md                # Approved analytical specification
│   ├── methodology_review.md         # Independent review of analytical methodology
│   ├── agent_metrics.csv             # 44 agents with 29 audited metrics
│   ├── peer_metrics.csv              # 6 operational peer group benchmarks
│   ├── raw_bottom10.csv              # 20 raw contractual ranking entries
│   ├── training_candidates.csv       # Exactly 10 certified training candidates
│   ├── policy_exceptions.csv         # 343 double-dipping ticket records
│   ├── validation_report.md          # Deterministic engine validation report
│   ├── ai_sample.csv                 # 100 stratified diagnostic tickets
│   ├── ai_ticket_audit.json          # 100 structured qualitative diagnoses
│   ├── ai_cost_log.json              # Incurred cost register (₹0.00)
│   ├── ai_gold_standard.csv          # 20 human expert benchmark tickets
│   ├── ai_validation_report.md       # AI agreement rate validation report
│   ├── ai_hallucination_review.csv   # Supervisory correction register
│   ├── ai_agent_diagnostics.csv      # Agent-level aggregated AI signals
│   ├── final_data_quality_register.md# 10 documented limitations & mitigations
│   ├── final_validation_report.md    # Quality gate PASS WITH LIMITATIONS report
│   ├── consistency_audit.md          # Pre-dashboard reconciliation report
│   ├── dashboard_spec.md             # Complete dashboard technical specification
│   ├── executive_memo.md             # Authoritative 1-page executive memorandum
│   ├── executive_memo.pdf            # Publication-grade rendered executive PDF
│   └── final_submission_checklist.md # Final submission QA and packaging certification
├── tests/                            # Automated Pytest Suite (43 Tests)
│   ├── test_data_loader.py           # Referential & schema integrity (5 tests)
│   ├── test_metrics_engine.py        # Shrinkage, SLAs, handle times (7 tests)
│   ├── test_ai_auditor.py            # AI sampling, schema, fallback (7 tests)
│   ├── test_quality_gate.py          # Quality gate & source benchmarks (10 tests)
│   ├── test_dashboard.py             # Dashboard testability & data checks (12 tests)
│   └── test_validation.py            # End-to-end engine validation (2 tests)
├── prompts/                          # AI Qualitative Prompts
│   ├── ticket_diagnosis_v1.txt       # 8-dimensional diagnosis template
│   └── README.md                     # Prompt documentation & guidance
├── serve.py                          # Zero-dependency local dashboard launcher
└── requirements.txt                  # Minimal Python dependencies
```

---

## Quality Gate & Governance Certifications

- **Phase 3A Deterministic Engine:** Certified with 100% parity across all 44 agents and ground-truth business calculations.
- **Phase 3B AI Auditor:** Strictly bounded to an auxiliary qualitative diagnostic layer (zero influence over rankings, scores, or candidates).
- **Phase 3C Quality Gate:** Formally certified with **PASS WITH LIMITATIONS** across all 10 documented operational constraints.
- **Phase 3C.1 Consistency Audit:** 100% synchronized across source CSVs, documentation, and data stores.
- **Phase 4A Executive Dashboard:** Completed, verified, and testable with zero external runtime dependencies.
- **Phase 4B Executive Memo:** Authoritative Markdown & publication-grade PDF deliverable aligned to ground-truth validation artifacts.
- **Phase 4C Final QA & Packaging:** Verified, 42/42 tests passing, and certified **READY FOR SUBMISSION**.
