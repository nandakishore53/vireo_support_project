# Vireo Audio Support Analytics — Pre-Dashboard Consistency Audit

**Audit Date:** October 2026  
**Audit Phase:** Phase 3C.1 Consistency Audit  
**Scope:** Dataset B (11,750 Tickets, 44 Agents, 18 Months)  
**Author:** Lead Data Analyst & Engineering Architect  

---

## 1. Audit Overview

Prior to commencing dashboard construction, a comprehensive repository-wide consistency audit was conducted to reconcile discrepancies between early discovery notes, Phase 3A deterministic engine outputs, Phase 3B AI auditor logs, and Phase 3C quality gate documentation. 

Every discrepancy was traced directly to the primary source CSVs:
- `data/tickets.csv` (11,750 rows)
- `data/agents.csv` (44 rows)
- `data/orders.csv` (10,000 rows)
- `data/products.csv` (7 SKUs)
- `reference/support-policy.pdf` (Version 3.2)

---

## 2. Itemized Discrepancy Register

### Item 1: CSAT Response Rate & Count
- **Metric:** CSAT Survey Response Count and Percentage
- **Value A:** 5,196 responses (44.22%) [Found in `data/tickets.csv`, `outputs/data_audit.md`, `src/validation.py`]
- **Value B:** 2,350 responses (20.0%) [Found in initial draft of `outputs/final_data_quality_register.md`]
- **Source:** Direct query on `data/tickets.csv`: `tickets['csat_score'].notnull().sum()`.
- **Root Cause:** A clerical transposition error during Phase 3C drafting conflated the 2,309 legacy negative handle-time tickets with CSAT responses, erroneously stating "2,350 (20.0%)".
- **Authoritative Value:** **5,196 responses (44.2213% $\approx$ 44.22%)** (6,554 null / 55.78%).
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`.

---

### Item 2: Category "Other" Ticket Count
- **Metric:** Total tickets categorized under "Other"
- **Value A:** 1,732 tickets (14.74%) [Found in `data/tickets.csv`, `outputs/data_audit.md`]
- **Value B:** 1,842 tickets (15.68%) [Found in initial draft of `outputs/final_data_quality_register.md`]
- **Source:** Direct query on `data/tickets.csv`: `(tickets['category'] == 'Other').sum()`.
- **Root Cause:** In Phase 3C drafting, the figure 1,842 was inadvertently introduced (likely an unverified transposition from ticket ID `TK-241842` or Delivery category volume 1,884). 
- **Authoritative Value:** **1,732 tickets (14.7404% $\approx$ 14.74%)**.
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`.

---

### Item 3: Agent Name Collision
- **Metric:** Duplicate Agent Display Name in Support Roster
- **Value A:** `Kavya Pandey` (`A3006` in Chat Frontline vs `A3029` in Logistics) [Found in `data/agents.csv`, `outputs/data_audit.md`]
- **Value B:** "Siddharth" collision (`A3004` vs `A3007`) [Found in initial draft of `outputs/final_data_quality_register.md`]
- **Source:** Direct query on `data/agents.csv`: `agents['name'].value_counts()`.
- **Root Cause:** `A3004` (Siddharth Kapoor) and `A3007` (Siddharth Trivedi) share only a first name, but have distinct surnames. The only exact identical full name collision in the roster is `Kavya Pandey` (shared by `A3006` and `A3029`).
- **Authoritative Value:** **Exact duplicate display name is `Kavya Pandey` (A3006 and A3029)**. Disambiguation requires binding all logic to immutable `agent_id`.
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`.

---

### Item 4: Missing Order ID Linkage
- **Metric:** Tickets lacking an associated `order_id`
- **Value A:** 4,107 tickets (34.95%) [Found in `data/tickets.csv`, `outputs/data_audit.md`, `outputs/methodology.md`]
- **Value B:** 3,745 tickets (31.87%) [Found in initial draft of `outputs/final_data_quality_register.md`]
- **Source:** Direct query on `data/tickets.csv`: `tickets['order_id'].isnull().sum()`.
- **Root Cause:** 3,745 was an informal estimate in exploratory drafting. The exact count of null `order_id` values in `tickets.csv` is 4,107, representing 34.9532% of 11,750 tickets. All remaining 7,643 non-null order IDs successfully match records in `data/orders.csv`.
- **Authoritative Value:** **4,107 tickets unlinked (34.9532% $\approx$ 34.95%)**; 7,643 tickets linked (65.05%).
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`.

---

### Item 5: Replacement Cost Terminology & Formula
- **Metric:** Valuation of warranty replacement units in double-dipping exposure
- **Value A:** "Replacement unit cost: ₹235,500" [Ambiguous terminology suggesting pure manufacturing cost]
- **Value B:** "Replacement policy-cost exposure: ₹235,500" [Audited regulatory terminology]
- **Source:** `reference/support-policy.pdf` (Section 5.1), `data/products.csv`, and `src/metrics_engine.py` line 88–92.
- **Root Cause:** ₹235,500 is not the bare manufacturing unit cost. It represents 136 replacement units across the 131 double-dipped orders, calculated as:
  $$\text{Product Unit Cost (₹189,260)} + \text{Logistics Surcharge (136} \times \text{₹340 = ₹46,240)}$$
- **Authoritative Value & Formula:** **Replacement policy-cost exposure: ₹235,500**.
  $$\text{Formula: } \sum_{\text{replacements}} \left(\text{unit\_cost\_inr} + 340\right)$$
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`, `outputs/ai_validation_report.md`.

---

### Item 6: AI Diagnostic Auditor Role & Cost Accounting
- **Metric:** Incurred AI execution cost and operational authority
- **Value A:** Actual cost: ₹0.00 (offline heuristic `deterministic_v1`)
- **Value B:** Hypothetical commercial API cost estimates ($0.075 / 1M tokens)
- **Source:** `outputs/ai_cost_log.json`
- **Root Cause:** The project strictly adhered to zero-cost, offline execution guidelines without remote API keys. Any commercial LLM figures are purely hypothetical external pricing estimates.
- **Authoritative Value:** **Actual incurred cost: ₹0.00**. Cost per analyzed ticket: ₹0.00. The AI is strictly auxiliary diagnostic evidence across 100 tickets, with zero authority to alter agent rankings, training shortlists, CSAT, handle time, or financial metrics.
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`, `outputs/ai_cost_log.json`.

---

### Item 7: AI Benchmark 30% Agreement Metric
- **Metric:** Interpretation of AI vs. Gold Standard agreement
- **Value A:** "30% AI accuracy" [Misleading colloquial phrasing]
- **Value B:** "6/20 exact all-field agreement (30.0%)" [Precise multi-dimensional benchmark]
- **Source:** `outputs/ai_gold_standard.csv` and `outputs/ai_validation_report.md`
- **Root Cause:** Evaluating 5 multi-class categorical dimensions simultaneously results in compound probabilities. While exact all-field agreement is 6/20 (30.0%), underlying field-level agreements are high: Policy Signal 20/20 (100.0%), Agent Handling Signal 16/20 (80.0%), Resolution Quality 13/20 (65.0%), Evidence Quality 13/20 (65.0%), Primary Root Cause 9/20 (45.0%).
- **Authoritative Interpretation:** Must be presented with numerator/denominator as **6/20 exact all-field agreement (30.0%)**, alongside individual field metrics.
- **Files Corrected:** `outputs/ai_validation_report.md`, `outputs/final_validation_report.md`, `outputs/final_data_quality_register.md`.

---

### Item 8: Double-Dipping Business Presentation
- **Metric:** ₹590,934 combined historical exposure
- **Value A:** "Recoverable training ROI / guaranteed savings" [Incorrect causal framing]
- **Value B:** "Confirmed historical financial exposure / process-control opportunity" [Governance-compliant framing]
- **Source:** `src/metrics_engine.py` and `reference/support-policy.pdf` Section 5.
- **Root Cause:** Double-dipping occurred due to a cross-ticket CRM/ERP system gap allowing concurrent refunds and replacements on the same order. Training agents cannot fix a missing database validation constraint.
- **Authoritative Calculation & Framing:**
  - Affected Orders: **131**
  - Historical Refunds: **₹355,434**
  - Replacement Policy-Cost Exposure: **₹235,500**
  - Combined Exposure: **₹590,934**
  - Annualized Exposure: **₹393,956 / year** ($₹590,934 \times \frac{12}{18}$)
  - Presentation: Formally presented as an **IT process-control opportunity**, NOT training ROI.
- **Files Corrected:** `outputs/final_data_quality_register.md`, `outputs/final_validation_report.md`.

---

## 3. Summary of Files Corrected

1. `outputs/final_data_quality_register.md` — Updated CSAT response rate to 44.22% (5,196), missing orders to 34.95% (4,107), Category Other to 14.74% (1,732), clarified Kavya Pandey name collision, and standardized replacement policy cost terminology.
2. `outputs/final_validation_report.md` — Fully synchronized with authoritative figures; reaffirmed PASS WITH LIMITATIONS.
3. `outputs/ai_validation_report.md` — Standardized 6/20 exact all-field agreement and auxiliary diagnostic role.
4. `tests/test_quality_gate.py` — Updated test assertions to validate exact source CSV benchmarks.

---

## 4. Final Quality Gate Readiness

All discrepancies have been resolved to their verifiable ground truth in the source data. The test suite passes 100%.

**Pre-Dashboard Readiness Status:** **READY FOR DASHBOARD**
