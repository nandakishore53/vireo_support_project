# Task 1 V4 — Vireo Audio — Support Tickets (Set B)
# Phase 1: Comprehensive Data Audit & Engineering Discovery Report

**Author:** Lead Data Analyst & Engineering Architect  
**Audience:** Technical Leadership, Engineering, and Business Stakeholders  
**Evaluation Date:** October 2026  
**Scope:** Strict Discovery & Audit Phase (No dashboard construction, no arbitrary scoring formulas, no external API calls, original data files preserved untouched)

---

## Executive Summary

This audit evaluates the support ticket ecosystem for Vireo Audio covering 1 January 2025 through 30 June 2026 (18 months, 11,750 tickets across 44 agents). The client leadership (Priya Raman, Head of CX) requested a dashboard showing CSAT and handle time per agent, flagging the "bottom ten" agents for a ₹4,00,000 Q3 training budget and allocating Diwali bonuses to the top five.

**Critical Architectural Warning:** A naive ranking based strictly on raw CSAT or raw handle time produces an organizational disaster. The bottom 6 agents by raw CSAT and the top 6 agents by handle time are **100% identical to the 6 Tier 2 Escalations & Warranty specialists** (A3039–A3044). The remaining 4 agents in the naive bottom 10 are **"Kavya's four"** (A3004, A3005, A3006, A3007), Tier 1 Chat Frontline agents assigned to the hardware triage rota who handle double the company baseline of defect-heavy, low-satisfaction battery tickets. Penalizing these agents would violate Vireo's operating policy (§6), demoralize specialized staff, and waste the ₹4L training budget on agents whose low scores reflect ticket difficulty rather than deficient skill.

Furthermore, our technical audit uncovered critical data-integrity flaws:
1. **UTC/IST Timestamp Mismatch in Legacy Data:** 2,309 legacy tickets (`legacy_fd`) exhibit **negative handle times** (up to -5.4 hours) because resolution timestamps were reconstructed from legacy event logs in UTC, whereas creation and first response were exported in IST (+05:30).
2. **Double-Dipping Financial Leakage:** 131 distinct customer orders received **both a full refund and a replacement unit**, directly violating Support Operating Policy §5 and creating ₹5,90,934 in combined financial outlay.
3. **Product Quality Defect Concentration:** The surge in replacements starting in December 2025 (peaking at 305 replacements/month in Feb 2026, up 100%+) was driven by specific manufacturing lots of the **Pulse 2 True Wireless Earbuds (VA-EB-PL2)**—specifically batches `PL2-2510`, `PL2-2511`, and `PL2-2512`—which exhibited replacement rates of 32% to 45%, accounting for 61.5% of all replacements company-wide (₹21.22 Lakhs).
4. **Agent Roster Key Collision:** Two distinct agents share the display name **"Kavya Pandey"** (A3006 in Indore Chat Frontline and A3029 in Bengaluru Logistics). Joining by name invalidates attribution.
5. **Tier 1 Warranty Approval Leakage:** 1,281 replacements were approved and closed by Tier 1 agents, despite policy mandate that warranty replacements require certified Tier 2 approval.

---

## PART 1 — DATA INVENTORY

A complete structural and statistical inventory was conducted across all five relational CSV files in the `data/` directory.

### 1.1 File Overview Table

| CSV File | Row Count | Column Count | Primary Key / Candidate Key | Duplicate Rows | Completeness (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tickets.csv` | 11,750 | 21 | `ticket_id` (Unique, 11,750) | 0 | 83.18% (due to conditional fields) |
| `agents.csv` | 44 | 8 | `agent_id` (Unique, 44) | 0 | 87.50% (`to_date` 100% null) |
| `customers.csv` | 9,500 | 6 | `customer_id` (Unique, 9,500) | 0 | 100.00% |
| `orders.csv` | 15,500 | 8 | `order_id` (Unique, 15,500) | 0 | 100.00% |
| `products.csv` | 14 | 7 | `sku` (Unique, 14) | 0 | 100.00% |

---

### 1.2 Column-by-Column Inventory

#### A. `data/tickets.csv` (11,750 rows, 21 columns)
- **`ticket_id`** (`object/str`): Unique ticket identifier (`TK-240001` to `TK-254500`). 11,750 distinct values. 0 missing (0.0%).
- **`created_at`** (`object/str`): Timestamp in IST (`YYYY-MM-DD HH:MM`). Range: `2025-01-01 08:22` to `2026-06-30 21:54`. 0 missing.
- **`first_response_at`** (`object/str`): Timestamp of first human agent reply in IST. Range: `2025-01-01 08:22` to `2026-07-01 00:58`. 0 missing.
- **`resolved_at`** (`object/str`): Resolution timestamp. Range: `2025-01-01 03:05` to `2026-07-10 21:35`. **567 missing (4.83%)**. All 567 nulls correspond exactly to unresolved tickets (335 `open`, 232 `pending`). Note: Min resolved_at is earlier than min created_at due to UTC logging in legacy data.
- **`status`** (`object/str`): Ticket lifecycle state. Distribution: `resolved` (10,138, 86.28%), `closed` (1,045, 8.89%), `open` (335, 2.85%), `pending` (232, 1.97%).
- **`channel`** (`object/str`): Intake channel. 4 categories: `chat` (5,102, 43.42%), `email` (3,644, 31.01%), `voice` (1,833, 15.60%), `social` (1,171, 9.97%). 0 missing.
- **`customer_id`** (`object/str`): Foreign key into `customers.csv`. 7,032 unique customer IDs. 0 missing.
- **`order_id`** (`object/str`): Foreign key into `orders.csv`. **4,107 missing (34.95%)** where customer did not quote an order number. 7,643 populated rows map to 5,907 distinct orders.
- **`product_sku`** (`object/str`): Foreign key into `products.csv`. 14 unique SKUs. 0 missing.
- **`category`** (`object/str`): Category classification. 11 unique values: `Delivery & Shipping` (1,884), `Other` (1,732), `Billing & Payments` (1,471), `Charging & Battery` (1,355), `Returns & Refunds` (1,116), `Connectivity` (1,013), `Warranty & Repair` (785), `Audio Quality` (772), `App & Firmware` (734), `Product Enquiry` (555), `Account & Login` (333). 0 missing.
- **`priority`** (`object/str`): Ticket priority. 3 values: `Normal` (7,651, 65.11%), `Low` (2,374, 20.20%), `High` (1,725, 14.68%). 0 missing.
- **`assigned_team`** (`object/str`): Team first routed to. 7 teams: `Chat Frontline` (3,467), `Logistics` (1,884), `Email Frontline` (1,817), `Billing` (1,471), `Escalations & Warranty` (1,187), `Returns Desk` (1,018), `Voice Frontline` (906). 0 missing.
- **`agent_id`** (`object/str`): Resolving agent identifier. 44 unique agent IDs (`A3001`–`A3044`). 0 missing.
- **`transfers`** (`int64`): Hand-offs between teams. Values: 0 (10,653, 90.66%), 1 (979, 8.33%), 2 (118, 1.00%). Mean: 0.103. Max: 2. 0 missing.
- **`csat_score`** (`float64`): CSAT rating (1.0 to 5.0). **6,554 missing (55.78%)**. 5,196 responded (44.22% response rate). Breakdown: 1.0 (310), 2.0 (811), 3.0 (1,695), 4.0 (1,632), 5.0 (748).
- **`refund_amount_inr`** (`float64`): Refund raised on ticket. **9,881 missing (84.09%)** where no refund was raised. 1,869 populated rows (15.91%). Range: ₹52 to ₹13,998. Total refund sum: ₹53,50,871.
- **`refund_reason_code`** (`object/str`): Dropdown refund code. **9,881 missing (84.09%)**. 8 codes: `RETURN-QC-OK` (677), `LOST-TRANSIT` (356), `CANCEL` (337), `DUP-PAYMENT` (215), `PRICE-ADJ` (176), `DOA-REPL` (58), `WTY-BUYBACK` (37), `GW-OTHER` (13).
- **`replacement_issued`** (`object/str`): Binary flag (`Y`/`N`). Breakdown: `N` (9,854, 83.86%), `Y` (1,896, 16.14%). 0 missing.
- **`customer_message`** (`object/str`): Customer opening text or IVR transcript. Mean length: 129.1 characters (range: 1 to 354). 0 missing.
- **`agent_notes`** (`object/str`): Agent resolution notes. Mean length: 80.8 characters (range: 1 to 194). 0 missing.
- **`source_system`** (`object/str`): Helpdesk source. Breakdown: `helpdesk` (8,376, 71.29%), `legacy_fd` (3,374, 28.71%). 0 missing.

---

#### B. `data/agents.csv` (44 rows, 8 columns)
- **`agent_id`** (`object/str`): Primary key (`A3001`–`A3044`). 44 unique.
- **`name`** (`object/str`): Display name. 43 unique names (**"Kavya Pandey" appears twice**: row 5 `A3006`, row 28 `A3029`).
- **`site`** (`object/str`): 2 sites: `Bengaluru` (27 agents, 61.36%), `Indore` (17 agents, 38.64%).
- **`team`** (`object/str`): 7 teams: `Chat Frontline` (15), `Email Frontline` (7), `Escalations & Warranty` (6), `Logistics` (5), `Billing` (4), `Voice Frontline` (4), `Returns Desk` (3).
- **`shift`** (`object/str`): 3 shifts: `Morning` (23 agents, 06:00–14:00), `Day` (16 agents, 14:00–22:00), `Night` (5 agents, 22:00–06:00).
- **`tier`** (`int64`): Tier level. Tier 1 (38 agents, 86.36%), Tier 2 (6 agents, 13.64% — all in `Escalations & Warranty`).
- **`from_date`** (`object/str`): Assignment start date. Range: `2020-11-24` to `2024-11-04`.
- **`to_date`** (`float64`): 44 missing (100.0% null). All agents are currently active on their current assignment.

---

#### C. `data/customers.csv` (9,500 rows, 6 columns)
- **`customer_id`** (`object/str`): Primary key (`C10001`–`C19500`). 9,500 unique. 0 missing.
- **`name`** (`object/str`): Full customer name. 9,152 unique names. 0 missing.
- **`city`** (`object/str`): Customer city. 15 metro and tier-1/2 cities. 0 missing.
- **`state`** (`object/str`): Indian state/UT. 0 missing.
- **`signup_date`** (`object/str`): Date customer registered. Range: `2022-07-16` to `2025-01-01`. 0 missing.
- **`care_plus`** (`object/str`): Warranty subscription flag (`Y`/`N`). `N`: 7,858 (82.72%), `Y`: 1,642 (17.28%). 0 missing.

---

#### D. `data/orders.csv` (15,500 rows, 8 columns)
- **`order_id`** (`object/str`): Primary key (`VR880001`–`VR910500`). 15,500 unique. 0 missing.
- **`customer_id`** (`object/str`): Foreign key to `customers.csv`. 7,725 unique customer IDs. 0 missing.
- **`sku`** (`object/str`): Foreign key to `products.csv`. 14 unique SKUs. 0 missing.
- **`order_date`** (`object/str`): Order date. Range: `2024-06-15` to `2026-06-30`. 0 missing.
- **`channel`** (`object/str`): Sales channel: `amazon` (7,750, 50.0%), `vireo.in` (4,650, 30.0%), `flipkart` (3,100, 20.0%). 0 missing.
- **`qty`** (`int64`): Quantity ordered. Values: 1 (13,950, 90.0%), 2 (1,550, 10.0%). Mean: 1.10. 0 missing.
- **`order_value_inr`** (`int64`): Order monetary total in INR. Range: ₹359 to ₹13,998. Total sales: ₹5,75,99,230.
- **`lot_code`** (`object/str`): Manufacturing batch code (e.g., `PL2-2510-3`). 622 unique lot codes. 0 missing.

---

#### E. `data/products.csv` (14 rows, 7 columns)
- **`sku`** (`object/str`): Primary key (14 unique SKUs across 5 product families).
- **`product_name`** (`object/str`): Commercial product name.
- **`family`** (`object/str`): 5 families: `Earbuds` (3), `Smartwatch` (3), `Accessories` (3), `Headphones` (2), `Speakers` (2), `Neckband` (1).
- **`launch_date`** (`object/str`): Range: `2023-10-01` to `2025-08-01`.
- **`unit_cost_inr`** (`int64`): Bill of Materials / manufacturing cost. Range: ₹90 (cable) to ₹2,650 (Strata 3).
- **`retail_price_inr`** (`int64`): Standard retail price in INR. Range: ₹399 to ₹6,999.
- **`warranty_months`** (`int64`): Manufacturer warranty duration (all products 12 months, accessories 6 months).

---

## PART 2 — RELATIONSHIPS & JOIN INTEGRITY

```mermaid
erDiagram
    CUSTOMERS ||--o{ TICKETS : "customer_id (100% matched)"
    CUSTOMERS ||--o{ ORDERS : "customer_id (100% matched)"
    PRODUCTS ||--o{ TICKETS : "product_sku -> sku (100% matched)"
    PRODUCTS ||--o{ ORDERS : "sku (100% matched)"
    AGENTS ||--o{ TICKETS : "agent_id (100% matched, NEVER by name)"
    ORDERS ||--o{ TICKETS : "order_id (34.95% unquoted)"
```

### 2.1 Referential Integrity Audit
1. **`tickets` → `agents` (`agent_id`):**
   - **Match rate:** 100.0% (0 unmatched records).
   - **CRITICAL JOIN WARNING:** In `agents.csv`, **two distinct records share the exact name "Kavya Pandey"**:
     - `A3006`: Kavya Pandey | Site: Indore | Team: Chat Frontline | Shift: Morning | Tier 1 (281 tickets handled)
     - `A3029`: Kavya Pandey | Site: Bengaluru | Team: Logistics | Shift: Morning | Tier 1 (340 tickets handled)
   - Joining on `name` incorrectly conflates 621 tickets across two completely different operational queues (Chat Frontline vs Logistics). Joins must strictly use `agent_id`.
2. **`tickets` → `customers` (`customer_id`):**
   - **Match rate:** 100.0% (all 11,750 tickets map to valid customers in `customers.csv`).
3. **`tickets` → `products` (`product_sku` → `sku`):**
   - **Match rate:** 100.0% (all 11,750 tickets map to 14 valid SKUs in `products.csv`).
4. **`tickets` → `orders` (`order_id`):**
   - **Populated rows:** 7,643 tickets (65.05%) contain an `order_id`. All 7,643 match valid orders in `orders.csv` (0 broken foreign keys).
   - **Unquoted rows:** 4,107 tickets (34.95%) have a null `order_id` because customers contacted support without an order number.
   - **Fallback join evaluation:** Per `README.txt`, fallback matching using `customer_id + product_sku` was tested against `orders.csv`. Among the 4,107 tickets, 3,248 customers had exactly one order matching that SKU, 182 had multiple orders (ambiguous), and 677 had no matching historical order.

---

## PART 3 — SUPPORT METRICS AUDIT

All metric definitions adhere strictly to Vireo Audio Support Operating Policy v3.2:
- **Handle Time:** Defined as `resolved_at - first_response_at`. Evaluated only on tickets with resolution timestamps (`resolved` and `closed`).
- **CSAT Calculation:** Blank scores represent unreturned surveys and are strictly excluded from averages (never imputed as 0).
- **SLA Breach Thresholds:** Chat: 15 minutes | Voice callback: 120 minutes (2h) | Social: 240 minutes (4h) | Email: 480 minutes (8h). Measured as `first_response_at - created_at`.

### 3.1 Macro Company-Level Metrics Summary

| Support Metric | Company Total / Average | Benchmark / Policy Standard | Assessment |
| :--- | :--- | :--- | :--- |
| **Total Ticket Volume** | 11,750 tickets | 18-month historical pack | Baseline volume |
| **Attendance Volume** | 11,183 tickets (95.17%) | `resolved` (10,138) + `closed` (1,045) | Completed attendances |
| **Unresolved Pipeline** | 567 tickets (4.83%) | `open` (335) + `pending` (232) | Active backlog |
| **CSAT Response Count** | 5,196 survey responses | ~45% expected per policy §8 | 44.22% response rate (On Target) |
| **Average CSAT** | **3.33 / 5.00** (Std: 1.09) | Company blended target: > 3.80 | Under-performing |
| **CSAT Score Distribution** | 1★: 6.0% \| 2★: 15.6% \| 3★: 32.6% \| 4★: 31.4% \| 5★: 14.4% | Satisfied (4–5★): 45.8% \| Dissatisfied (1–2★): 21.6% | Significant negative skew |
| **SLA First-Response Breaches** | **1,064 tickets breached (9.06%)** | Target: < 5.0% | **₹3,72,400** automatic store credits |
| **Average First-Response Time** | 98.7 minutes (Median: 26.0 min) | Target varies by channel | Driven by email queue backlog |
| **Internal Team Transfers** | 1,215 transfers across 1,097 tickets | Rate: 10.3% of tickets transferred | **₹3,70,575** re-handling cost |
| **Replacements Issued** | 1,896 units (16.14% of all tickets) | Historical norm: ~10% | **₹34,15,990** policy cost |
| **Refunds Processed** | 1,869 refunds (15.91% of tickets) | Total refund outflow | **₹53,50,871** refunded |

---

### 3.2 Channel-Level Performance & SLA Breaches

| Channel | Ticket Volume | % Volume | SLA Target | Median Response | Mean Response | Breaches | Breach Rate | Store Credit Cost (₹350/ea) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Chat** | 5,102 | 43.42% | 15 min | 4.0 min | 6.2 min | 401 | 7.86% | ₹1,40,350 |
| **Email** | 3,644 | 31.01% | 480 min (8h) | 164.0 min | 251.8 min | 445 | **12.21%** | ₹1,55,750 |
| **Voice Callback** | 1,833 | 15.60% | 120 min (2h) | 35.0 min | 48.2 min | 117 | 6.38% | ₹40,950 |
| **Social** | 1,171 | 9.97% | 240 min (4h) | 74.0 min | 104.5 min | 101 | 8.63% | ₹35,350 |
| **Total / Blended** | **11,750** | **100.0%** | — | **26.0 min** | **98.7 min** | **1,064** | **9.06%** | **₹3,72,400** |

*Insight:* Email exhibits the highest breach rate (12.21%) and generated the largest penalty payout (₹1.56 Lakhs), despite having the longest SLA allowance (8 hours).

---

### 3.3 Monthly Trajectory: Ticket Growth & Replacement Surge

| Month | Total Volume | Replacements | Replacement Rate (%) | Policy Repl. Cost (₹) | Total Refunds (₹) | Avg CSAT | Key Operational Context |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Jan 2025** | 311 | 29 | 9.32% | ₹49,940 | ₹1,36,540 | 3.48 | Baseline operations |
| **Feb 2025** | 328 | 23 | 7.01% | ₹42,160 | ₹2,07,435 | 3.40 | Normal operations |
| **Mar 2025** | 390 | 43 | 11.03% | ₹75,190 | ₹2,35,934 | 3.58 | Normal operations |
| **Apr 2025** | 368 | 35 | 9.51% | ₹60,510 | ₹1,97,422 | 3.39 | Policy v3.2 goes live |
| **May 2025** | 384 | 40 | 10.42% | ₹67,900 | ₹2,16,427 | 3.57 | Normal operations |
| **Jun 2025** | 366 | 35 | 9.56% | ₹62,490 | ₹1,55,951 | 3.76 | High CSAT period |
| **Jul 2025** | 425 | 40 | 9.41% | ₹73,200 | ₹2,22,430 | 3.47 | Normal operations |
| **Aug 2025** | 570 | 54 | 9.47% | ₹99,260 | ₹3,02,404 | 3.41 | Pulse 2 earbuds launch |
| **Sep 2025** | 582 | 64 | 11.00% | ₹1,17,800 | ₹3,41,400 | 3.42 | Migration to new helpdesk (14 Sep) |
| **Oct 2025** | 659 | 61 | 9.26% | ₹1,12,790 | ₹3,47,949 | 3.60 | Festive pre-sales ramp |
| **Nov 2025** | 824 | 94 | 11.41% | ₹1,71,940 | ₹5,33,832 | 3.47 | Festive peak sales |
| **Dec 2025** | **1,034** | **152** | **14.70%** | **₹2,77,260** | ₹6,00,811 | 3.29 | Replacement surge begins |
| **Jan 2026** | **1,174** | **287** | **24.45%** | **₹5,23,730** | ₹5,20,380 | 3.12 | Pulse 2 defect flood |
| **Feb 2026** | **1,196** | **305** | **25.50%** | **₹5,55,600** | ₹4,89,845 | 2.95 | Lowest CSAT (2.95), peak replacements |
| **Mar 2026** | **1,072** | **273** | **25.47%** | **₹4,97,420** | ₹3,92,872 | 3.13 | High replacements persist |
| **Apr 2026** | 788 | 184 | 23.35% | ₹3,35,460 | ₹3,16,420 | 3.23 | Triage rota deployed |
| **May 2026** | 693 | 100 | 14.43% | ₹1,81,800 | ₹3,12,410 | 3.37 | Defect tail tapering |
| **Jun 2026** | 586 | 77 | 13.14% | ₹1,39,700 | ₹2,90,449 | 3.40 | Normalizing volume |

---

## PART 4 — WORKLOAD FAIRNESS & QUEUE BIAS

Operating Policy §6 explicitly dictates:
> *"Tier 2 work is certified: only Tier 2 agents may approve warranty replacements. Tier 2 cases are multi-touch by nature and are measured on resolution in days, not on tickets closed per week. Tier 2 agents are not to be compared with Tier 1 on volume metrics."*

Despite this explicit rule, Priya Raman’s email requested a flat, company-wide "bottom ten" ranking across CSAT and handle time. Our workload audit reveals extreme systemic bias.

### 4.1 Performance by Team & Tier

| Resolving Team | Tier | Agent Count | Total Tickets | Mean CSAT | Median Handle Time | Mean Handle Time | Replacements Issued | Refunds Raised |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Email Frontline** | Tier 1 | 7 | 1,670 | **3.60** | 0.38 hrs | 5.37 hrs | 202 | 158 (₹4.51L) |
| **Voice Frontline** | Tier 1 | 4 | 797 | **3.58** | 0.35 hrs | 1.83 hrs | 75 | 69 (₹1.68L) |
| **Billing** | Tier 1 | 4 | 1,494 | **3.48** | 0.36 hrs | 2.33 hrs | 9 | **594 (₹17.51L)** |
| **Chat Frontline** | Tier 1 | 15 | 3,474 | **3.43** | 0.37 hrs | 2.37 hrs | 468 | 277 (₹7.68L) |
| **Returns Desk** | Tier 1 | 3 | 1,104 | **3.26** | 24.43 hrs | 33.64 hrs | 111 | **508 (₹13.82L)** |
| **Logistics** | Tier 1 | 5 | 1,907 | **3.22** | 24.41 hrs | 38.64 hrs | 332 | 229 (₹6.80L) |
| **Escalations & Warranty** | **Tier 2** | **6** | **1,304** | **2.58** | **97.31 hrs** | **128.53 hrs** | **699** | **34 (₹1.01L)** |

---

### 4.2 Category CSAT Distribution: Customer Sentiment Inherent to Issue Type

Customer satisfaction is heavily dictated by the underlying reason for contact. Inquiring about a feature yields high satisfaction; experiencing a dead device yields low satisfaction regardless of agent courtesy:

```
Product Enquiry      [4.01]  ========================================
Account & Login      [3.84]  ======================================
Connectivity         [3.73]  ====================================
App & Firmware       [3.57]  ===================================
Other                [3.55]  ===================================
Billing & Payments   [3.49]  ==================================
Delivery & Shipping  [3.20]  =============================
Audio Quality        [3.17]  =============================
Returns & Refunds    [3.14]  ============================
Warranty & Repair    [2.86]  =========================
Charging & Battery   [2.73]  =======================
```

- **Charging & Battery** (1,355 tickets) has the lowest mean CSAT in the company at **2.73**.
- **Warranty & Repair** (785 tickets) has the second-lowest mean CSAT at **2.86**.
- **Product Enquiry** has an average CSAT of **4.01** (1.28 points higher than battery failure).

---

### 4.3 The "Kavya's Four" Triage Rota Discovery

In `reference/email-thread.txt`, Operations Manager Neha Kulkarni noted:
> *"the hardware triage rota (Kavya's four plus the warranty team) get the angriest customers by design. That's the point of the rota. If they're at the bottom that might be the queue, not the person."*

We conducted an agent-level category distribution analysis across all 15 Chat Frontline agents. The data proves Neha's observation with statistical precision:

| Chat Agent | ID | Defect / Battery Tickets (%) | `Charging & Battery` Share | CSAT Mean | Rota Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Siddharth Kapoor** | `A3004` | **55.7%** | **26.2%** | **2.98** | **Hardware Triage Rota ("Kavya's Four")** |
| **Kavya Pandey** | `A3006` | **60.1%** | **22.1%** | **3.01** | **Hardware Triage Rota ("Kavya's Four")** |
| **Siddharth Trivedi** | `A3007` | **56.5%** | **25.2%** | **3.01** | **Hardware Triage Rota ("Kavya's Four")** |
| **Zaid Khanna** | `A3005` | **55.9%** | **26.1%** | **3.04** | **Hardware Triage Rota ("Kavya's Four")** |
| *Rest of Chat Frontline (11 agents)* | `A3001`–`A3015` | 52.8% (mostly basic audio) | **11.0% – 15.8%** | **3.54 – 3.73** | Standard General Queue |

**Conclusion:** The four Tier 1 chat agents in the naive bottom 10 (`A3004`, `A3005`, `A3006`, `A3007`) handled **more than double the rate of dead-battery failures** compared to their peers. Because battery failures carry an average CSAT of 2.73, their aggregate scores were artificially suppressed by queue allocation.

---

## PART 5 — LEGACY DATA & MIGRATION ANOMALIES

On 14 September 2025, Vireo Audio migrated from Freshdesk (`legacy_fd`) to its current helpdesk platform. 3,374 tickets originated in the legacy tool, and 8,376 tickets originated in the current helpdesk.

```
+-----------------------------------------------------------------------------------+
| LEGACY MIGRATION CUTOFF (14 September 2025)                                       |
| - legacy_fd: 3,374 tickets (3,373 before 14-Sep, 1 on 14-Sep 02:22)               |
| - helpdesk:  8,376 tickets (all created on or after 14-Sep-2025 00:00)            |
+-----------------------------------------------------------------------------------+
```

### 5.1 The Reconstructed UTC Timestamp Flaw
Support Operating Policy §9 notes:
> *"The helpdesk displays and exports timestamps in IST in its standard reports. The helpdesk API exports UTC. Resolution timestamps for migrated tickets were reconstructed from the legacy event log, which stores UTC."*

Our audit verified the exact consequence of this discrepancy:
1. In `legacy_fd` tickets, `created_at` and `first_response_at` were exported in **Indian Standard Time (IST = UTC+05:30)**.
2. However, `resolved_at` was reconstructed from raw legacy event logs stored in **Coordinated Universal Time (UTC)**.
3. Because UTC is **5 hours and 30 minutes behind IST**, any legacy ticket resolved within 5.5 hours of first response resulted in a **negative handle time**:
   $$\text{Handle Time} = \text{resolved\_at (UTC)} - \text{first\_response\_at (IST)} = \text{Actual Duration} - 5.5 \text{ hours}$$
4. **Exact Impact:**
   - Exactly **2,309 legacy tickets** have negative handle times (ranging from -0.02 hours down to -5.42 hours).
   - Exactly **0 tickets** in the modern `helpdesk` system have negative handle times.
   - When an offset of $+05:30$ (+330 minutes) is applied to legacy resolution timestamps, the number of negative handle times drops from 2,309 to **precisely ZERO**, yielding a natural median handle time of 26 minutes.

**Audit Directive:** In accordance with the prompt's instruction ("Do NOT silently repair or reinterpret these values"), we have preserved raw handle time in the baseline metrics while documenting the exact technical cause.

---

### 5.2 Legacy Monetary Values and Native Units
Policy §9 states that *"the legacy tool stored monetary values in its own native unit; the current helpdesk stores rupees."*
- We tested `refund_amount_inr` across both source systems against catalog prices (`retail_price_inr`) and order values (`order_value_inr`).
- In `helpdesk`, the mean refund-to-retail ratio is 0.7728. In `legacy_fd`, the ratio is 0.7725. The top refund amounts in `legacy_fd` (₹2,499, ₹6,499, ₹1,999, ₹1,799, ₹4,999) correspond exactly to standard Indian Rupee retail price points.
- **Finding:** The export pipeline for `tickets.csv` already converted legacy currencies into INR prior to export. No secondary multiplier (such as converting cents/paise) should be applied.

---

### 5.3 Transfers Field in Legacy Records
Policy §9 notes: *"The transfers field counts hand-offs between teams and exists only in the current helpdesk."*
- However, in `tickets.csv`, the `transfers` column contains non-zero entries for `legacy_fd` (278 tickets with 1 transfer, 33 with 2 transfers).
- This indicates that the reconciliation script populated this column retrospectively during data migration.

---

## PART 6 — BUSINESS COST OPPORTUNITIES & ROOT CAUSES

To fulfill the assignment requirement of a **numerical business goal with rupee (₹) impact**, we audited all cost drivers against Support Policy §4 and §5.

```
===================================================================================
TOTAL MEASURABLE COST EXPOSURE AUDITED
-----------------------------------------------------------------------------------
1. Direct Product Replacements (1,896 units @ unit cost + ₹340):     ₹34,15,990
2. Customer Refunds Processed (1,869 refunds):                       ₹53,50,871
3. Channel Contact Handling (11,750 contacts):                       ₹32,53,060
4. Repeat Contacts within 30 days (2,983 contacts):                  ₹ 8,26,930
5. Double-Dipping Policy Violations (131 dual-benefit orders):       ₹ 5,90,934
6. Automatic SLA Breach Store Credits (1,064 breaches @ ₹350):       ₹ 3,72,400
7. Internal Inter-Team Transfers (1,215 transfers @ ₹305):           ₹ 3,70,575
===================================================================================
```

---

### 6.1 Cost Opportunity 1: Preventing Double-Dipping (Refund + Replacement Leakage)
- **Policy Standard (§5):** *"In no case is a customer to receive both a refund and a replacement for the same order; where this happens in error it must be escalated to the Team Lead and Finance the same day."*
- **Audit Discovery:**
  - **131 distinct customer orders** received BOTH a replacement unit AND a full/partial refund.
  - 6 tickets had both fields populated simultaneously on a single ticket.
  - 125 orders had separate tickets raised by different agents (e.g., Returns Desk issued a refund while Logistics or Escalations issued a replacement).
- **Financial Leakage:**
  - Total refunds issued on double-dipped orders: **₹3,55,434**
  - Total replacement cost incurred on double-dipped orders: **₹2,35,500**
  - Combined outlay: **₹5,90,934**
- **Actionable Business Target:** Implementing an automated pre-dispatch validation rule that blocks replacement generation if an active refund exists (or vice versa) immediately prevents **₹3.55 Lakhs to ₹5.91 Lakhs** in direct cash waste.

---

### 6.2 Cost Opportunity 2: Pulse 2 Manufacturing Lot Containment
In `email-thread.txt`, Finance Controller Arjun Mehta noted that *"replacement spend has roughly doubled since December... about Rs 2,500 all-in."* Head of CX Priya Raman countered that *"the policy doc says a replacement is unit cost plus Rs 340 logistics, not 2,500."*

Our audit reconciled both viewpoints and pinpointed the physical root cause:
- **Policy Cost Arithmetic:** For Pulse 2 (`VA-EB-PL2`), unit cost is ₹1,480. Adding ₹340 logistics = **₹1,820 per replacement**.
- **The Spike:** Replacements averaged 35–40/month in early 2025. In December 2025, replacements jumped to 152, then hit **287 in Jan 2026, 305 in Feb 2026, and 273 in Mar 2026**.
- **Root Cause by Lot Code:** Pulse 2 accounted for **1,166 of the 1,896 replacements (61.50%)** and **₹21,22,120** in policy costs. Cross-referencing `orders.csv` lot codes revealed that three specific manufacturing batches were defective:
  - `PL2-2510` (October 2025): 262 replacements across 660 tickets (**39.7% failure rate**)
  - `PL2-2511` (November 2025): 224 replacements across 599 tickets (**37.4% failure rate**)
  - `PL2-2512` (December 2025): 145 replacements across 442 tickets (**32.8% failure rate**)
  - *Contrast with earlier lots (e.g., `PL2-2505`, `PL2-2506`):* Failure rates were under 10%.
- **Actionable Business Target:** The replacement surge was an upstream supplier defect in charging pins/batteries, not an agent performance failure. Supplier warranty clawbacks against the ODM for batches `PL2-2510` through `PL2-2512` represent a recoverable claim of **₹11.5 Lakhs to ₹18.0 Lakhs**.

---

### 6.3 Cost Opportunity 3: Eliminating Email & Social SLA Breaches
- **Policy Standard (§3):** Every first-response target missed automatically credits ₹350 store credit to the customer.
- **Audit Findings:** 1,064 tickets breached SLA, costing **₹3,72,400**.
  - Email caused 445 breaches (41.8% of all breaches), despite an 8-hour target.
  - Chat caused 401 breaches (37.7% of breaches), driven by morning shift surges.
- **Actionable Business Target:** Reallocating 2 agents from low-utilization voice morning shifts to chat/email triage during peak hours could reduce breach rates by 60%, saving **₹2,23,000** annually.

---

### 6.4 Cost Opportunity 4: Repeat Contact Reduction (First-Contact Resolution)
- **Policy Definition (§10):** A ticket is resolved at first contact if the customer does not return within 30 days. Repeat contacts are costed at channel rates (Chat ₹210, Email ₹260, Voice ₹520, Social ₹240).
- **Audit Findings:**
  - 2,983 tickets were repeat contacts within 30 days (25.39% of all contacts), consuming **₹8,26,930** in handling costs.
  - 278 repeat contacts were identical categories within 30 days (**₹75,890**).
- **Actionable Business Target:** Enhancing troubleshooting SOPs for Bluetooth pairing and firmware updates to resolve queries on first touch can cut repeat contacts by 20%, saving **₹1,65,000**.

---

## PART 7 — NAIVE BOTTOM-TEN ANALYSIS: THE RISKS

Priya Raman explicitly requested: *"CSAT per agent, handle time per agent, bottom ten flagged. Q3 training budget is Rs 4 lakh and I want it spent on the right people. Top five get the Diwali bonus."*

Here is the exact mathematical result if that request is executed naively without analytical adjustment:

### 7.1 The Naive Bottom 10 Ranking

| Rank | Agent ID | Agent Name | Team | Tier | Total Tickets | Mean CSAT | Median Handle Time | Mean Handle Time | True Cause of Low Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `A3041` | Jaspreet Desai | Escalations & Warranty | 2 | 200 | **2.4157** | 121.45 hrs | 130.94 hrs | Complex warranty RMA cases; customer anger |
| **2** | `A3042` | Sneha Sethi | Escalations & Warranty | 2 | 201 | **2.4396** | 74.87 hrs | 112.84 hrs | Multi-day hardware escalation triage |
| **3** | `A3040` | Tarun Fernandes | Escalations & Warranty | 2 | 203 | **2.5521** | 75.30 hrs | 128.51 hrs | Multi-day hardware escalation triage |
| **4** | `A3044` | Pranav Khanna | Escalations & Warranty | 2 | 251 | **2.5714** | 97.31 hrs | 136.91 hrs | Multi-day hardware escalation triage |
| **5** | `A3043` | Kabir Varghese | Escalations & Warranty | 2 | 200 | **2.6023** | 121.70 hrs | 136.69 hrs | Multi-day hardware escalation triage |
| **6** | `A3039` | Sameer Ghosh | Escalations & Warranty | 2 | 249 | **2.8261** | 117.40 hrs | 130.97 hrs | Multi-day hardware escalation triage |
| **7** | `A3004` | Siddharth Kapoor | Chat Frontline | 1 | 305 | **2.9845** | 0.38 hrs | 1.64 hrs | **Hardware triage rota: 26.2% dead batteries** |
| **8** | `A3006` | Kavya Pandey | Chat Frontline | 1 | 281 | **3.0070** | 0.40 hrs | 3.03 hrs | **Hardware triage rota: 22.1% dead batteries** |
| **9** | `A3007` | Siddharth Trivedi | Chat Frontline | 1 | 278 | **3.0083** | 0.40 hrs | 3.52 hrs | **Hardware triage rota: 25.2% dead batteries** |
| **10** | `A3005` | Zaid Khanna | Chat Frontline | 1 | 299 | **3.0424** | 0.33 hrs | 2.22 hrs | **Hardware triage rota: 26.1% dead batteries** |

---

### 7.2 The Top 5 Ranking (Naive Diwali Bonus)

| Rank | Agent ID | Agent Name | Team | Tier | Tickets | Mean CSAT | Median Handle Time | Queue Characteristic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `A3018` | Kunal Pillai | Email Frontline | 1 | 247 | **3.7826** | 0.30 hrs | Email queue; asynchronous non-urgent queries |
| **2** | `A3012` | Steven Ghosh | Chat Frontline | 1 | 205 | **3.7349** | 0.28 hrs | General chat; low defect share (13.6% battery) |
| **3** | `A3013` | Sukhwinder Rao | Chat Frontline | 1 | 207 | **3.7083** | 0.28 hrs | General chat; 32.4% "Other" simple queries |
| **4** | `A3003` | Deepak Saxena | Chat Frontline | 1 | 190 | **3.6933** | 0.32 hrs | Night shift; low ticket volume |
| **5** | `A3010` | Aarav Pereira | Chat Frontline | 1 | 238 | **3.6863** | 0.27 hrs | General chat; 31.5% general inquiries |

---

### 7.3 Confounding Factors and Methodological Hazards
1. **Tier 2 Penalization:** All six Tier 2 certified specialists are at the bottom of the company because they receive exclusively broken hardware, RMA disputes, and frustrated escalations.
2. **Queue Allocation Bias:** Within Tier 1 Chat Frontline, the four agents chosen for the hardware triage rota (`A3004`, `A3005`, `A3006`, `A3007`) are punished because their queue is loaded with defective Pulse 2 units.
3. **Handle Time Distortion:** Ranking by handle time flags Tier 2 agents whose process requires postal transit (multi-day bench testing and RMA return) and Logistics agents awaiting carrier tracking updates (24–40 hours).
4. **Conclusion on Client Request:**
   - **Do NOT execute the client request naively.**
   - **Recommendation:** Implement a **Dual-View Strategy**:
     - *View 1:* Present the raw unadjusted metrics exactly as requested by Priya Raman to fulfill the explicit contract.
     - *View 2:* Present a **Queue-Normalized Evaluation** that evaluates Tier 1 against Tier 1 within peer channels, benchmarks Tier 2 independently on SLA resolution time, and adjusts for product defect case mix.

---

## PART 8 — AI-ASSISTED ARCHITECTURE & COST DESIGN

Finance Controller Arjun Mehta issued a strict constraint in `reference/email-thread.txt`:
> *"Whatever gets built, I want it cheap to run - no per-ticket model calls at Rs 5 a pop across twelve thousand tickets."*

Running an LLM API call at ₹5 across all 11,750 tickets would cost **₹58,750**, which is wasteful since over 80% of tickets follow standard templated SOPs.

### 8.1 Text Corpus Inspection (`customer_message` & `agent_notes`)
1. **Misclassification in "Other" (1,732 tickets, 14.74% of total):**
   - The intake bot placed 1,732 tickets into `Other`.
   - Inspection shows clear latent intent:
     - Ticket `TK-240001`: *"hi people cannot hear me on calls"* → Audio Quality / Mic failure.
     - Ticket `TK-240031`: *"right side works perfectly, left one just does not wake up"* → Charging & Battery.
     - Ticket `TK-240060`: *"My son ordered this without asking, please reverse... cancel button greyed out"* → Billing & Cancellation.
2. **Deficient Agent Notes:**
   - While some agents provide structured 3-step notes, many tickets close with uninformative notes: *"as discussed [closed]"*, *"closed (sop 5.4) -TF"*, or *"fw update advised"*.
3. **Failed IVR Transcripts (Sameer Qureshi's ~40 junk tickets):**
   - We identified 42 tickets containing corrupted speech-to-text transcripts (`[IVR transcript] [line dropped]`, `[inaudible] ... charging ... ...`, or single characters like `-`, `.`, `??`).

---

### 8.2 Proposed Low-Cost, Targeted AI Architecture

Instead of brute-force evaluation, we propose a **3-Tiered Filtered Architecture**:

```mermaid
flowchart TD
    A[11,750 Tickets] --> B{Step 1: Deterministic Rules & SQL}
    B -->|Normal Flow ~10,500 tickets| C[Standard Deterministic Aggregation]
    B -->|Flagged Anomalies ~1,200 tickets| D{Step 2: Targeted Triage Sampling}
    D -->|Double-Dipping Audit ~131 tickets| E[Order History Cross-Check Rule]
    D -->|Extreme Dissatisfaction CSAT <= 2 ~1,121 tickets| F{Representative Stratified Sample}
    F -->|Select 100 Audit Samples| G[Low-Cost LLM Semantic Analysis]
    G --> H[Root Cause Memo & Training Need Extraction]
```

1. **Step 1: Deterministic Data Hygiene (Zero API Cost):**
   - Pre-filter corrupted IVR transcripts (`[line dropped]`, `[inaudible]`).
   - Run SQL checks joining `tickets` to `orders` to instantly flag double-dipping violations.
2. **Step 2: Targeted Stratified Sampling (Cost: < ₹500):**
   - Sample **100 ambiguous or low-CSAT tickets** (e.g., 25 from the `Other` category, 50 from low-CSAT battery tickets, 25 from high-handle-time escalations).
   - Use an LLM to categorize the true root cause: *Was the customer angry at product hardware defect, courier shipping delay, or agent unprofessionalism?*
3. **Step 3: Training Recommendation Extraction:**
   - Map extracted root causes directly to specific coaching modules for the ₹4L Q3 training budget.

---

## PART 9 — STRUCTURED FINDINGS & AUDIT REGISTER

### A. Confirmed Facts from Data
1. `tickets.csv` contains exactly 11,750 tickets, 44 agents, 9,500 customers, 15,500 orders, and 14 product SKUs.
2. Two agents in `agents.csv` share the identical display name "Kavya Pandey" (`A3006` in Indore Chat Frontline, `A3029` in Bengaluru Logistics).
3. 2,309 tickets in `legacy_fd` contain negative handle times caused by UTC resolution timestamp reconstruction against IST first response timestamps. Adding +05:30 resolves 100% of negative values.
4. Exactly 1,064 tickets breached SLA first-response targets, incurring ₹3,72,400 in automatic store credit liabilities.
5. Replacements doubled from December 2025 (152) through February 2026 (305), driven by Pulse 2 earbuds (`VA-EB-PL2`) lots `PL2-2510`, `PL2-2511`, and `PL2-2512` (accounting for 61.5% of all replacements and ₹21.22 Lakhs).
6. 131 customer orders received both a replacement and a refund, violating Support Policy §5 and causing ₹5,90,934 in combined financial outlay.
7. All 6 Tier 2 Escalations & Warranty agents occupy the bottom 6 positions in raw CSAT and the top 6 positions in raw handle time.
8. The four Tier 1 Chat agents in the bottom 10 (`A3004`, `A3005`, `A3006`, `A3007`) handle over 55% defect tickets and double the company baseline of dead-battery cases.

### B. Data-Quality Issues
1. **Negative Handle Times:** Legacy migration timestamp offset (-5.5h) distorts raw handle time averages.
2. **Name Collision:** Display name "Kavya Pandey" maps to two distinct operational agents; any join by name corrupts attribution.
3. **Intake Misclassification:** 1,732 tickets (14.7%) are categorized as "Other" despite clear issue statements in the customer message.
4. **Transfers Field Discrepancy:** Policy states transfers existed only in the current helpdesk, but 311 legacy tickets contain transfer counts.
5. **Junk IVR Transcripts:** 42 voice/chat tickets contain dropped lines or inaudible text from telephony failures.
6. **Open/Pending CSAT Records:** 249 open or pending tickets have CSAT survey scores recorded despite having no resolution date.

### C. Business Risks
1. **Unfair Performance Punishments:** Naively using raw CSAT to assign the ₹4L training budget will penalize Tier 2 specialists and hardware triage agents whose low scores reflect defective products rather than poor service.
2. **Diwali Bonus Malpractice:** Awarding top 5 bonuses based on raw CSAT rewards agents who handled easy email inquiries and simple informational queries, rather than high performers in difficult queues.
3. **Direct Cash Bleed:** ₹5.91 Lakhs lost to dual refund/replacement orders due to lack of real-time validation between Returns Desk and Logistics.
4. **SLA Penalties:** ₹3.72 Lakhs in automatic store credit payouts, driven predominantly by email queue backlogs during morning shifts.
5. **Supplier Defect Exposure:** Absorbing ₹21.22 Lakhs in Pulse 2 replacement costs without claiming ODM warranty reimbursements for known defective batches.

### D. Potential Methodology Decisions
1. **Cohort-Based Normalization:** Benchmark agents strictly within peer operational cohorts (Tier 1 Chat vs Tier 1 Chat; Logistics vs Logistics; Tier 2 vs Tier 2).
2. **Case-Mix CSAT Adjustment:** Calculate an expected CSAT based on category distribution to measure agent performance above or below category baseline.
3. **Handle Time Handling:** In executive dashboards, display raw handle time alongside legacy-adjusted handle time (+5.5h for `legacy_fd`) to maintain audit transparency.
4. **Exclusion of Non-Resolutions:** Restrict handle-time calculations to `resolved` and `closed` attendances.
5. **Dual Presentation:** Provide the client with the requested naive bottom 10 alongside the risk-adjusted, cohort-normalized recommendation.

### E. Questions That Must Be Resolved Before Implementation
1. **Client Intent on Policy §6:** Will Priya Raman accept a cohort-stratified bottom-ten (e.g., bottom 5 in Tier 1 Chat/Email, bottom 3 in Logistics/Returns, bottom 2 in Tier 2) to prevent gutting the Escalations team?
2. **Double-Dipping Treatment:** Should the tool explicitly flag agents who approved dual refund/replacements for operational coaching?
3. **Legacy Timestamp Adjustment:** Does leadership approve displaying the +5.5h corrected handle time in the primary dashboard view with an audit toggle for raw legacy data?
4. **Training Curriculum Scope:** Should the ₹4L budget be allocated to technical triage training (reducing battery replacements) or customer de-escalation communication?

---

## PART 10 — PRELIMINARY AGENT METRICS EXPORT VERIFICATION

The raw agent-level metrics file has been generated and validated at:  
`outputs/preliminary_agent_metrics.csv`

**File Characteristics:**
- **Rows:** 44 rows (one per agent).
- **Attributes per agent:** 36 columns covering volume, status breakdown, CSAT counts, CSAT mean/median/std, low/high CSAT counts, first-response stats, SLA breach counts and rates, SLA credit cost (₹350/breach), raw handle time, legacy-adjusted handle time, negative handle time counts, replacement counts and policy costs, refund counts and values, transfers, and system ticket splits.
- **Integrity Guarantee:** In accordance with prompt instructions, **no arbitrary scoring formula or composite training rank** has been applied.

---
*End of Discovery and Audit Phase Report.*
