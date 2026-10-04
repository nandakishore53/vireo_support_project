# Vireo Audio Support Analytics — Data & Metric Parity Validation Report

**Status:** PASSED (100% Metric Parity)  
**Module Tested:** `src.data_loader`, `src.metrics_engine`, `src.config`  
**Benchmark Baseline:** Phase 1 Data Audit (`outputs/data_audit.md`) & Support Policy v3.2  

---

## 1. Executive Summary & Parity Matrix

| Validation Check | Expected Baseline | Actual Engine Output | Status |
| :--- | :--- | :--- | :--- |
| **Row Counts Parity** | Tickets: 11,750 | Agents: 44 | Customers: 9,500 | Orders: 15,500 | Products: 14 | Tickets: 11,750 | Agents: 44 | Customers: 9,500 | Orders: 15,500 | Products: 14 | **[PASS]** |
| **Agent Join & Kavya Pandey Disambiguation** | 0 unmatched IDs; Kavya Pandey A3006 (Indore Chat: 281) & A3029 (BLR Logistics: 340) | Unmatched: 0; A3006: 281, A3029: 340 | **[PASS]** |
| **Legacy Handle Time Normalization (+05:30 UTC Correction)** | Raw negative HT: 2,309 | Audited negative HT: 0 | Raw negative HT: 2309 | Audited negative HT: 0 | **[PASS]** |
| **SLA First-Response Breaches & Penalty Cost** | 1,064 breaches | Rs 372,400 store credits | 1,064 breaches | Rs 372,400.00 | **[PASS]** |
| **Double-Dipped Orders Detection (Refund + Replacement)** | 131 distinct orders | Rs 590,934 combined exposure | 131 orders | Rs 590,934.00 | **[PASS]** |
| **Total Inter-Team Transfers Count** | 1,215 transfers | 1,215 transfers | **[PASS]** |
| **Operational Replacements & Refunds Volume** | Replacements: 1,896 | Refunds: 1,869 | Refund Sum: Rs 5,350,871.00 | Replacements: 1,896 | Refunds: 1,869 | Refund Sum: Rs 5,350,871.00 | **[PASS]** |
| **CSAT Survey Response Count & Mean (Nulls Excluded)** | 5,196 responses (44.22% response rate) | Mean: 3.3266 | 5,196 responses | Mean: 3.3266 | **[PASS]** |
| **Peer Groups Hierarchy** | 6 defined peer groups (Chat, Email, Voice, Logistics, Returns & Billing, Escalations & Warranty) | 6 peer groups: ['Chat Frontline', 'Email Frontline', 'Escalations & Warranty', 'Logistics', 'Returns & Billing', 'Voice Frontline'] | **[PASS]** |
| **Training Candidates & Policy Exceptions Separation** | 10 training candidates | Policy exceptions isolated in separate table | 10 training candidates | 343 exception records | **[PASS]** |

---

## 2. Key Findings & Metric Verifications

### 2.1 Referential Join Integrity & Disambiguation
- **Agent Joins:** 100% of all 11,750 tickets joined to `agents.csv` strictly via `agent_id`. Zero broken foreign keys.
- **Kavya Pandey Disambiguation:** The two distinct agents sharing the name 'Kavya Pandey' were independently verified:
  - `A3006`: Indore, Chat Frontline, Tier 1, Morning shift -> Exactly 281 tickets handled.
  - `A3029`: Bengaluru, Logistics, Tier 1, Morning shift -> Exactly 340 tickets handled.
- **Customer & Product Joins:** 100% referential integrity with zero orphan keys.

### 2.2 Legacy Timestamp Normalization (`legacy_fd`)
- **Raw Data Anomaly:** Exactly 2,309 tickets in `legacy_fd` had negative raw handle times down to -5.42 hours because reconstructed resolution timestamps were recorded in UTC while first-response timestamps were in IST.
- **Audited Normalization:** Adding the documented $+05:30$ (+330 minutes) UTC-to-IST offset resolved **100% of negative handle times** to valid positive durations (median audited handle time: 26.0 minutes).
- **Provenance:** Raw handle time remains completely preserved in `raw_handle_time_minutes` for audit trail transparency.

### 2.3 SLA Breach Liabilities & Scenario Models
- **Historical Total (18 Months):** 1,064 breaches -> **Rs 372,400.00** in automatic store credit liabilities (Rs 350/breach).
- **Annualized Baseline (12-Month Equivalent):** 709.3 breaches/year -> **Rs 248,266.67 / year**.
- **Scenario Models:**
  - **25% Reduction:** 177.3 fewer breaches/year -> **Rs 62,066.67 / year** (Rs 93,100 over 18m).
  - **50% Reduction:** 354.7 fewer breaches/year -> **Rs 124,133.33 / year** (Rs 186,200 over 18m).
  - **75% Reduction:** 532.0 fewer breaches/year -> **Rs 186,200.00 / year** (Rs 279,300 over 18m).

### 2.4 Double-Dipping Process Control Discovery
- **Affected Orders:** Exactly 131 customer orders received both a refund and a physical replacement unit.
- **Historical Financial Exposure:** Rs 355,434.00 refunds + Rs 235,500.00 replacements = **Rs 590,934.00** total exposure (Annualized: **Rs 393,956.00 / year**).
- **Separation:** Isolated into `outputs/policy_exceptions.csv` as an independent IT/process control opportunity rather than being misattributed to agent training.

### 2.5 Training Shortlist Candidates (~10 Agents)
- Exactly 10 candidates selected across Track 1 (SLA), Track 2 (Communication), and Track 3 (Technical RMA):
  - `A3003` (Deepak Saxena, Chat Night): 16.32% SLA breach rate.
  - `A3002` (Megha Sheikh, Chat Night): 14.43% SLA breach rate.
  - `A3016` (Om Khanna, Email Night): 15.07% SLA breach rate.
  - `A3021` (Geeta Sen, Email Morning): 13.73% SLA breach rate.
  - `A3030` (Geeta Iyer, Logistics Morning): 13.35% SLA breach rate.
  - `A3035` (Nisha Rao, Billing Morning): 11.38% SLA breach rate.
  - `A3028` (Vivaan Pandey, Logistics Morning): 10.63% SLA breach rate.
  - `A3020` (Riya Pillai, Email Morning): CSAT 3.495 (peer 3.599).
  - `A3029` (Kavya Pandey, Logistics Morning): CSAT 3.126 (peer 3.213).
  - `A3041` (Jaspreet Desai, Escalations Tier 2): CSAT 2.416 (Tier 2 peer 2.568).

---

## 3. Verified Artifact Outputs

| Artifact File | Description | Row Count | Column Count |
| :--- | :--- | :--- | :--- |
| `outputs/agent_metrics.csv` | Full metrics for all 44 agents with shrinkage & SLA stats | 44 | 29 |
| `outputs/peer_metrics.csv` | Benchmark statistics for 6 operational peer groups | 6 | 10 |
| `outputs/raw_bottom10.csv` | Priya Raman's contractual raw bottom 10 (CSAT & Handle Time) | 20 | 11 |
| `outputs/training_candidates.csv` | Evidence-backed training shortlist candidates | 10 | 11 |
| `outputs/policy_exceptions.csv` | Detailed audit records for double-dipped orders | 262 | 9 |

---
*Report automatically generated by `src/validation.py`.*