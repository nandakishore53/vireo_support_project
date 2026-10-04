# Vireo Audio — Support Analytics & Training Shortlisting Methodology
## Architecture & Methodology Specification (Set B — Revised)

**Author:** Lead Data Analyst & Engineering Architect  
**Target Stakeholders:** Priya Raman (Head of CX), Arjun Mehta (Finance Controller), Neha Kulkarni (Support Ops Manager)  
**Status:** Approved Methodology Specification (Pre-Implementation)  
**Document Path:** `outputs/methodology.md`

---

## Executive Summary & The Business Story

This document specifies the analytical methodology for evaluating support performance, designing a training shortlist for the **₹4,00,000 Q3 training budget**, identifying candidates for **Diwali performance bonuses**, and addressing high-impact operational cost drivers at Vireo Audio.

### The 8-Stage Business Story
The methodology follows a coherent, evidence-backed narrative:
1. **Priya's Request (The Baseline):** We provide the raw bottom-ten ranking by CSAT and handle time as explicitly requested by Priya Raman, ensuring full contractual transparency.
2. **The Queue-Bias Trap:** We demonstrate empirically why the naive ranking is misleading: 100% of the bottom agents are Tier 2 RMA specialists or Chat frontline triage agents who inherit the most frustrated customers and defective products by design.
3. **Operational Peer Groups:** We establish peer cohorts based on channel dynamics, operational tier, and shift constraints so agents are evaluated fairly against like peers.
4. **Evidence-Backed Training Candidates:** We identify training candidates whose operational deficits (e.g., SLA pacing, queue FIFO discipline) are genuinely addressable via coaching.
5. **Separate Policy & Governance Exceptions:** We isolate procedural compliance issues (uncertified warranty replacements and double-dipping) as governance/process issues requiring systems controls, rather than mislabeling them as conversational skill deficits.
6. **Targeted AI Diagnostics:** We deploy a strictly bounded, non-overlapping 100-ticket AI sample to inspect qualitative text and distinguish product defect rage from agent handling.
7. **Plausible Training Business KPI:** We tie the primary training KPI to **First-Response SLA Breach Reduction**—an outcome agent training and queue management can realistically influence—calculating baseline exposure and scenario models (25%, 50%, 75%).
8. **Process-Control Discovery:** We independently present the **₹5,90,934 historical double-dipping exposure** (131 orders) as an immediate software/validation guardrail fix, without attributing this entire saving to agent retraining.

---

## A. Peer Group Design

### A.1 Why Company-Wide Rankings Distort Performance
Comparing all 44 agents on a single unadjusted leaderboard creates severe distortion:
- **Email Frontline (7 agents):** Asynchronous ticketing with an 8-hour SLA target. Customers expect turnaround in hours, not minutes. Mean CSAT is **3.60**.
- **Chat Frontline (15 agents):** Synchronous, real-time widget with a 15-minute SLA target. Mean CSAT is **3.43**.
- **Voice Frontline (4 agents):** Scheduled callbacks (08:00–22:00 IST) with a 2-hour target. Mean CSAT is **3.58**.
- **Logistics (5 agents) & Returns Desk (3 agents):** Workflows depend on external courier scans (AWB updates) and physical warehouse bench testing, resulting in natural handle times of 24–40 hours.
- **Escalations & Warranty (6 agents, Tier 2):** Certified specialists handling warranty claims, RMA mail-ins, and hardware triage. Mean CSAT is **2.58** and mean handle time is **128.5 hours** (3–5 days).

Operating Policy §6 explicitly commands:
> *"Tier 2 cases are multi-touch by nature and are measured on resolution in days, not on tickets closed per week. Tier 2 agents are not to be compared with Tier 1 on volume metrics."*

### A.2 Defined Operational Peer Groups

Agents are partitioned into **5 Operational Peer Groups**:

```mermaid
graph TD
    A[44 Support Agents] --> B[Peer Group 1: Frontline Digital & Voice]
    A --> C[Peer Group 2: Logistics Operations]
    A --> D[Peer Group 3: Returns & Billing Desk]
    A --> E[Peer Group 4: Tier 2 Escalations & Warranty]
    
    B --> B1[Chat Frontline: 15 agents | Tier 1 | 15m SLA]
    B --> B2[Email Frontline: 7 agents | Tier 1 | 8h SLA]
    B --> B3[Voice Frontline: 4 agents | Tier 1 | 2h SLA]
    
    C --> C1[Logistics: 5 agents | Tier 1 | 24-48h Workflow]
    
    D --> D1[Returns Desk: 3 agents | Tier 1 | Reverse QC]
    D --> D2[Billing: 4 agents | Tier 1 | PG Reconciliation]
    
    E --> E1[Escalations & Warranty: 6 agents | Tier 2 | RMA Diagnostics]
```

1. **Peer Group 1A — Chat Frontline (15 agents, Tier 1):** Real-time text intake, 24x7 coverage, 15m SLA target. Note: Agents on the hardware triage rota ("Kavya's four") are annotated for battery defect concentration.
2. **Peer Group 1B — Email Frontline (7 agents, Tier 1):** Asynchronous ticketing, 8h SLA target, queue FIFO execution.
3. **Peer Group 1C — Voice Frontline (4 agents, Tier 1):** Daytime callbacks (08:00–22:00 IST), 2h SLA target.
4. **Peer Group 2 — Logistics (5 agents, Tier 1):** Carrier delivery exceptions, AWB tracing, address corrections (external carrier dependencies).
5. **Peer Group 3 — Financial & Returns Processing (7 agents, Tier 1):**
   - *Returns Desk (3 agents):* Reverse pickup scheduling and refund processing.
   - *Billing (4 agents):* Payment gateway errors, duplicate transactions, and coupon disputes.
6. **Peer Group 4 — Escalations & Warranty (6 agents, Tier 2):** Certified hardware triage and warranty approvals. Evaluated strictly against Tier 2 peers.

---

## B. Performance Metrics & Evaluation Framework

### B.1 Evaluated Metrics

| Metric Name | Calculation / Formula | Direction | Role in Shortlisting | Key Confounders & Caveats |
| :--- | :--- | :--- | :--- | :--- |
| **CSAT Mean ($\bar{x}$)** | $\frac{\sum \text{Score}}{\text{Valid Count}}$ (1–5 scale) | Higher is better | **Primary (Relative)** | Strong category bias (`Battery`: 2.73 vs `Enquiry`: 4.01). Blank scores strictly excluded. |
| **CSAT Response Count ($n$)** | Total completed surveys | Neutral | **Confidence Weight** | Ranges from 42 to 243. Low sample size requires peer shrinkage. |
| **SLA Breach Rate** | $\frac{\text{Breaches}}{\text{Total Tickets}}$ | Lower is better | **Primary (Operational)** | Directly causes ₹350 store credit penalties (Policy §3). Varies by shift volume. |
| **Median Handle Time** | $\text{Median}(\text{resolved\_at} - \text{first\_resp\_at})$ | Lower is better (in peer group) | **Contextual** | Meaningful only within same team. Tier 2 and Logistics naturally require days. |
| **Adjusted Handle Time** | $\text{Raw Handle Time} + 05:30$ for `legacy_fd` | Accurate | **Diagnostic Audit** | Reconstructed legacy resolution timestamps in UTC were offset by -5.5h against IST first responses. |
| **Policy Exceptions** | Dual refund+replacement / Tier 1 warranty replacements | Lower is better (0) | **Separate Compliance Flag** | Represents system/process breakdown, not a customer communication skill gap. |
| **Repeat Contacts (30d)** | % customers returning within 30d | Lower is better | **Secondary Context** | Substantially driven by Pulse 2 batch hardware defects rather than agent resolution quality. |

---

## C. Sample Size, Confidence & Shrinkage Mechanics

### C.1 Evidence Volume Disparity
In `outputs/preliminary_agent_metrics.csv`, completed survey volume ranges from $n = 42$ (`A3026`, Voice) to $n = 243$ (`A3037`, Returns Desk). Comparing raw sample means directly would penalize low-volume agents who encounter a small cluster of dissatisfied customers.

### C.2 Empirical Bayes Peer Shrinkage Formula
To stabilize estimates without arbitrary formulas, we apply **Empirical Bayes Shrinkage**. Each agent's mean CSAT is regularized toward their specific **Peer Group Mean** ($\mu_{\text{peer}}$), weighted by their sample size:

$$\text{CSAT}_{\text{shrunk}} = \frac{n \cdot \bar{x}_{\text{agent}} + m \cdot \mu_{\text{peer}}}{n + m}$$

Where:
- $n$ = Agent's completed CSAT survey count.
- $\bar{x}_{\text{agent}}$ = Agent's observed sample mean.
- $\mu_{\text{peer}}$ = The unweighted mean CSAT of the agent's specific peer group.
- $m$ = Shrinkage constant set to **$m = 25$** (approximately 50% of the minimum observed agent survey count).

#### Operational Interpretation:
- For high-evidence agents ($n \ge 150$), actual data drives $>85\%$ of the shrunk score.
- For lower-evidence agents ($n \approx 42$), the score shrinks $\sim 37\%$ toward the peer mean, preventing false alarms driven by sample volatility.

### C.3 Evidence-Strength Indicators (Reframed Confidence Intervals)
Standard errors are calculated as $\text{SE} = \frac{s}{\sqrt{n}}$.
The interval $\bar{x} \pm 1.96 \cdot \text{SE}$ is utilized as a **descriptive evidence-strength indicator** (precision bound) rather than a formal hypothesis test, acknowledging that bounded 1–5 survey ratings violate normal distribution assumptions. Agents with wide intervals are highlighted as having lower evidentiary weight.

---

## D. Defensible Training Shortlist Logic

Rather than combining disparate metrics into an arbitrary composite index, candidates are identified across **Three Explicit Operational Tracks**.

```
+---------------------------------------------------------------------------------------------------+
| TRACK 1: SLA Responsiveness & Queue Discipline (Directly Influenced by Agent Triage Training)      |
| TRACK 2: Queue-Normalized Communication Deficit (Peer-Relative CSAT Underperformance)             |
| TRACK 3: Advanced RMA Diagnostic & De-escalation (Within-Tier-2 Peer Comparison)                   |
+---------------------------------------------------------------------------------------------------+
| SEPARATE COMPLIANCE TRACK: Process & Governance Exceptions (Management Review & System Controls)  |
+---------------------------------------------------------------------------------------------------+
```

### D.1 Candidate Shortlist for Q3 Training Allocation (~10 Agents)

| Agent ID | Agent Name | Peer Group / Team | Primary Driver | Evidence & Peer Comparison | Sample Size & Precision | Likely Root Cause | Recommended Training Focus |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`A3003`** | Deepak Saxena | Chat Frontline (Night) | **SLA Responsiveness** | **16.32% breach rate** (31 breaches) vs Chat peer mean of 9.32% | $n=190$ tkts (High evidence) | Queue pacing during overnight shifts | **Module 1:** Real-Time Queue Monitoring & Intake Pacing |
| **`A3002`** | Megha Sheikh | Chat Frontline (Night) | **SLA Responsiveness** | **14.43% breach rate** (28 breaches) vs Chat peer mean of 9.32% | $n=194$ tkts (High evidence) | Delayed response initiation during night shift | **Module 1:** Real-Time Queue Monitoring & Intake Pacing |
| **`A3016`** | Om Khanna | Email Frontline (Night) | **SLA Responsiveness** | **15.07% breach rate** (33 breaches) vs Email peer mean of 11.31% | $n=219$ tkts (High evidence) | Backlog accumulation and FIFO non-adherence | **Module 2:** Email Queue FIFO Management & First-Touch Triage |
| **`A3021`** | Geeta Sen | Email Frontline (Morning) | **SLA Responsiveness** | **13.73% breach rate** (35 breaches) vs Email peer mean of 11.31% | $n=255$ tkts (High evidence) | Peak morning intake bottleneck handling | **Module 2:** Email Queue FIFO Management & First-Touch Triage |
| **`A3030`** | Geeta Iyer | Logistics (Morning) | **SLA Responsiveness** | **13.35% breach rate** (45 breaches) vs Logistics peer mean of 9.06% | $n=337$ tkts (Very high evidence) | Slow initial logging of courier tracking queries | **Module 3:** Rapid Intake & Carrier Exception Logging |
| **`A3035`** | Nisha Rao | Billing (Morning) | **SLA Responsiveness** | **11.38% breach rate** (47 breaches) vs Billing peer mean of 9.46% | $n=413$ tkts (Highest evidence) | Delayed initial response during billing peak | **Module 3:** Payment Gateway Rapid Triage & Callback SOP |
| **`A3028`** | Vivaan Pandey | Logistics (Morning) | **SLA Responsiveness** | **10.63% breach rate** (37 breaches) vs Logistics peer mean of 9.06% | $n=348$ tkts (High evidence) | Morning dispatch backlog delay | **Module 3:** Rapid Intake & Carrier Exception Logging |
| **`A3020`** | Riya Pillai | Email Frontline (Morning) | **Communication** | **CSAT 3.495** (shrunk: 3.516) vs Email peer mean of 3.599 | $n=101$ surveys (SE: 0.105) | Terse, templated customer email explanations | **Module 4:** Written De-escalation & Empathetic Communication |
| **`A3029`** | Kavya Pandey | Logistics (Morning) | **Communication** | **CSAT 3.126** (shrunk: 3.138) vs Logistics peer mean of 3.213 | $n=159$ surveys (SE: 0.077) | Customer frustration with delayed carrier updates | **Module 4:** Proactive Carrier Delay Messaging |
| **`A3041`** | Jaspreet Desai | Escalations & Warranty (Tier 2) | **Technical RMA** | **CSAT 2.416** vs Tier 2 peer mean of 2.568 (lowest in Tier 2) | $n=89$ surveys (SE: 0.108) | Protracted bench testing turnaround (130.9h handle time) | **Module 5:** Advanced RMA Workflow & De-escalation |

---

### D.2 Separate Policy & Governance Exceptions Track
The following agents are flagged for **Management Review & Workflow Investigation**, but are **NOT** automatically classified as training failures:
- **`A3037` (Mohammed Desai, Returns Desk):** Processed 19 refunds and 7 replacements on double-dipped orders; approved 55 uncertified replacements. High volume ($n=563$ tickets) indicates possible reliance on system defaults or lack of automated order cross-checks.
- **`A3031` (Zoya Menon, Logistics):** Processed 10 replacements and 4 refunds on double-dipped orders; approved 76 uncertified replacements.
- **`A3027` (Harpreet Goyal, Logistics):** Processed 5 replacements and 5 refunds on double-dipped orders; approved 79 uncertified replacements.

*Recommendation:* These represent **system control gaps** (helpdesk permitting Tier 1 closure of replacement flags without Tier 2 authorization, and lack of cross-checking order history). They require management workflow audits and IT validation rules, not remedial customer-service retraining.

---

### D.3 Handling "Kavya's Four" Triage Agents
Chat frontline agents `A3004` (Siddharth Kapoor), `A3005` (Zaid Khanna), `A3006` (Kavya Pandey), and `A3007` (Siddharth Trivedi) are in the raw bottom 10 strictly because they handled **22% to 26% Charging & Battery tickets** (company CSAT: 2.73) on the hardware triage rota. 
- *Methodological Decision:* They are protected from punitive classification. If leadership wishes to include them in Q3 training, they should be assigned to an **Advanced Battery & Charging Diagnostic Workshop** to equip them with specialized troubleshooting tools, rather than generic remedial training.

---

## E. Business KPI & Financial Analysis

### E.1 Primary Training Business KPI: First-Response SLA Breach Reduction

Agent training and queue management directly impact the speed with which incoming customer queries receive an initial human reply.

#### Historical Baseline:
- **Total Breaches (18-Month Dataset):** 1,064 tickets breached SLA.
- **Unit Penalty (Policy §3):** ₹350 store credit per breach charged to support P&L.
- **Historical Financial Exposure (18 Months):** **₹3,72,400**.
- **Annualized Baseline (12 Months):**
  $$\text{Annualized Breaches} = \frac{1,064}{1.5} = 709.3\text{ breaches/year}$$
  $$\text{Annualized Cost Exposure} = \frac{₹3,72,400}{1.5} = \mathbf{₹2,48,267\text{ / year}}$$

#### Scenario Analysis for Training Intervention:
Rather than asserting an arbitrary percentage reduction as a confirmed fact, we model three transparent operational scenarios:

| Operational Scenario | Breach Reduction Target | Annualized Breaches Prevented | Annualized Store Credit Savings (₹) | 18-Month Baseline Equivalent (₹) | Feasibility & Operational Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Conservative** | **25% Reduction** | 177.3 breaches / year | **₹62,067 / year** | ₹93,100 | Queue pacing in Night Chat (`A3002`, `A3003`) |
| **Moderate (Recommended)** | **50% Reduction** | 354.7 breaches / year | **₹1,24,133 / year** | ₹1,86,200 | Night Chat + Morning Email triage restructuring |
| **Aggressive** | **75% Reduction** | 532.0 breaches / year | **₹1,86,200 / year** | ₹279,300 | Cross-shift queue handovers + supervisory alerts |

---

### E.2 Independent Process & Control Opportunity: Double-Dipping Elimination

```
+----------------------------------------------------------------------------------------------------+
| SEPARATE PROCESS-CONTROL DISCOVERY (NOT ATTRIBUTED SOLELY TO TRAINING)                            |
| 131 Orders | ₹3,55,434 Refunds + ₹2,35,500 Replacements = ₹5,90,934 Historical Exposure          |
+----------------------------------------------------------------------------------------------------+
```

- **Nature of Discovery:** Exactly 131 customer orders received both a refund and a physical replacement unit, directly violating Support Policy §5.
- **Historical Combined Exposure:** **₹5,90,934** over 18 months (Annualized: **₹3,93,956 / year**).
- **Attribution Boundary:** This leakage cannot be claimed as a training-only saving. It is predominantly a **system control failure** where the helpdesk software allows a replacement ticket to be closed on an order that already has an approved refund (and vice versa).
- **Recommended Action:** Implement a deterministic IT validation check in the helpdesk platform blocking simultaneous refund/replacement generation. This system fix, supported by agent compliance awareness, prevents up to **₹3.94 Lakhs/year** in future cash and inventory loss.

---

## F. Targeted AI-Assisted Text Analysis Architecture

To comply strictly with Arjun Mehta’s constraint (*"no per-ticket model calls at Rs 5 across twelve thousand tickets"*), the AI system operates on a strictly bounded sample of **exactly 100 tickets**.

### F.1 Explicit, Non-Overlapping Stratified Sampling Strategy
To ensure that tickets cannot appear in multiple strata, the 100-ticket pool is selected using a **deterministic priority deduplication hierarchy** with a fixed random seed (`random_state=42`):

```mermaid
flowchart TD
    Pool[11,750 Historical Tickets] --> S1{Priority 1: Double-Dipped Orders}
    S1 -->|Sample exactly 15| Out1[Stratum 1: Double-Dipped Audit (15 tkts)]
    S1 -->|Remaining Pool| S2{Priority 2: Long Escalations}
    S2 -->|Assigned Escalations & Top Handle Time, sample 15| Out2[Stratum 2: Long Escalations (15 tkts)]
    S2 -->|Remaining Pool| S3{Priority 3: Low CSAT}
    S3 -->|CSAT <= 2.0, sample 40| Out3[Stratum 3: Low CSAT Dissatisfaction (40 tkts)]
    S3 -->|Remaining Pool| S4{Priority 4: Category Other}
    S4 -->|Category == 'Other', sample 30| Out4[Stratum 4: Latent Intent Audit (30 tkts)]
    
    Out1 --> Final[Total Non-Overlapping Sample: Exactly 100 Unique Tickets]
    Out2 --> Final
    Out3 --> Final
    Out4 --> Final
```

1. **Stratum 1 — Double-Dipped Orders (Priority 1):** Sample exactly **15 tickets** from the confirmed 131 double-dipped orders to audit agent closing notes for why dual resolutions were approved.
2. **Stratum 2 — Long Escalations (Priority 2):** From the remaining pool, sample exactly **15 tickets** from `Escalations & Warranty` with the longest handle times to identify multi-day bottlenecks.
3. **Stratum 3 — Low CSAT Dissatisfaction (Priority 3):** From the remaining pool, sample exactly **40 tickets** with CSAT $\le 2.0$ across all teams to classify whether customer dissatisfaction stemmed from product defects, delivery delays, or agent communication.
4. **Stratum 4 — Category `Other` Audit (Priority 4):** From the remaining pool, sample exactly **30 tickets** tagged as `Other` to identify latent categories missed by the intake bot.

*Total Sample:* Exactly **100 unique, non-overlapping tickets**.

---

### F.2 Prompt Specification & Output Schema

```text
You are a Quality Assurance Auditor for Vireo Audio.
Analyze the following customer support ticket text. Rely ONLY on the provided text.

METADATA:
- Ticket ID: {ticket_id} | Channel: {channel} | Assigned Team: {assigned_team}
- Logged Category: {category} | CSAT Score: {csat_score} | Stratum: {stratum}
- Customer Message:
"""{customer_message}"""
- Agent Closing Notes:
"""{agent_notes}"""

TASK:
Classify the observable operational evidence. Do NOT invent assumptions.

OUTPUT SCHEMA (Valid JSON strictly matching these keys):
{
  "ticket_id": "{ticket_id}",
  "latent_issue_category": "Charging & Battery" | "Audio Quality" | "Connectivity" | "Delivery & Shipping" | "Billing & Payments" | "Warranty & Repair" | "Other",
  "primary_dissatisfaction_driver": "Product Hardware Defect" | "Logistics / Courier Delay" | "Payment Gateway Glitch" | "Customer Misunderstanding" | "Agent Demeanor / Inaction" | "None / Satisfied",
  "agent_documentation_quality": "Thorough SOP Documented" | "Adequate Summary" | "Terse / Unhelpful Boilerplate" | "Missing Diagnostic Detail",
  "operational_finding": "Short string summarizing key observation"
}
```

#### Cost Estimate:
- Prompt: ~350 tokens per ticket $\times 100 = 35,000$ tokens.
- Output: ~80 tokens per ticket $\times 100 = 8,000$ tokens.
- Estimated execution cost: **$< ₹15.00 total** ($< \$0.18\text{ USD}$), fully adhering to budget guidelines.

---

## G. Validation Plan

### G.1 Three-Tier Validation Architecture
1. **Deterministic Data Parity:**
   - Verify ticket counts ($11,750$), survey responses ($5,196$), SLA breaches ($1,064$), and double-dipped orders ($131$).
   - Verify that adding $+05:30$ to `legacy_fd` tickets reduces negative handle times from $2,309$ to exactly $0$.
2. **AI Classification Quality:**
   - Manually annotate a gold-standard benchmark of **20 tickets** across the 4 strata.
   - Achieve $\ge 85\%$ classification agreement on `primary_dissatisfaction_driver` and `latent_issue_category`.
3. **Shortlist Robustness:**
   - Sensitivity test of shrinkage constant $m \in \{15, 25, 35\}$ to confirm that shortlisted agents remain stable across reasonable parameter boundaries.

---

## H. Implementation Scope & Work Breakdown (~5 Hours)

### H.1 Scope Boundaries
- **In Scope:**
  1. `src/metrics_engine.py`: Deterministic data processing, peer benchmarking, Empirical Bayes shrinkage, SLA breach tracking, and double-dipping detection.
  2. `src/ai_auditor.py`: Deterministic non-overlapping 100-ticket extraction, automated classification runner, and output generation.
  3. Interactive Dashboard (Vanilla HTML/CSS/JS): Dual-view toggle (Raw Contractual vs. Recommended Shortlist), peer-cohort filters, KPI scenario calculator, and AI diagnostic panel.
  4. Executive Business Memo: One-page PDF/Markdown memo to Priya Raman.
- **Deliberately Out of Scope:**
  - No 11,750-ticket brute-force LLM calls.
  - No production helpdesk database writes.
  - No speculative supplier warranty recovery claims.

---

## Known Limitations

1. **Unquoted Order IDs (34.95%):** 4,107 tickets lack an `order_id`. Double-dipping can only be audited where an order ID is explicitly quoted; 131 represents an audited lower bound.
2. **Historical Legacy Event Logs:** Reconstructed Freshdesk resolution timestamps are offset by UTC; while adding $+05:30$ corrects handle time, raw timestamps remain preserved for provenance.
3. **Observational Bounds:** CSAT reflects customer sentiment, which is inherently influenced by whether the product worked; peer-group shrinkage mitigates but cannot eliminate external consumer sentiment bias.

---
*End of Methodology Specification.*
