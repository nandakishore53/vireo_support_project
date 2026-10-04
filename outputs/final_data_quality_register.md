# Vireo Audio Support Analytics — Data Quality Register

**Document Version:** 1.1 (Pre-Dashboard Consistency Audit)  
**Phase:** 3C.1 Consistency Audit  
**Scope:** Dataset B (11,750 Support Tickets, 44 Agents, 18 Months)

---

## Executive Summary

This register systematically documents the 10 known data quality limitations, structural anomalies, and operational constraints identified during Discovery, Deterministic Metrics Modeling (Phase 3A), and AI Ticket Auditing (Phase 3B/3C). 

Every metric has been audited directly against the raw source CSVs (`data/tickets.csv`, `data/agents.csv`, `data/orders.csv`, `data/products.csv`). Each entry defines the root issue, business and analytical impact, engineering mitigation implemented in the pipeline, and residual risk for decision-makers.

---

## 1. Legacy Timestamp Reconstruction (Negative Handle Times)

- **Issue:** 2,309 legacy tickets migrated from Freshdesk prior to the 14 September 2025 cutover exhibited negative raw handle times (`resolved_at < created_at`), averaging approximately -330 minutes (-5.5 hours). This occurred during an uncoordinated platform migration where `resolved_at` was stored in UTC while `created_at` was stored in Indian Standard Time (IST, UTC+5:30).
- **Impact:** Naive calculation of handle times yields nonsensical negative durations, invalidating agent productivity metrics, SLA compliance calculations, and capacity planning.
- **Mitigation:** Implemented a deterministic 330-minute (+5.5 hour) adjustment in `src/metrics_engine.py` for all affected legacy tickets. Corrected 100% of negative values (`audited_handle_time_minutes >= 0`).
- **Remaining Risk:** Legacy tickets lack microsecond precision; resolution durations are reconstructed to nearest minute intervals. High-velocity frontline ticket durations (<2 minutes) carry minor reconstruction variance.

---

## 2. Voluntary CSAT Response Bias

- **Issue:** Exactly 5,196 out of 11,750 tickets (44.22%) contain customer satisfaction ratings, while 6,554 tickets (55.78%) lack CSAT feedback. Survey completion is voluntary, exhibiting bimodal polarization (customers with extreme frustration or exceptional delight are disproportionately represented).
- **Impact:** Raw arithmetic means over-penalize agents with low response counts. A single 1-star review can depress an agent's raw average by 0.5+ stars, creating false-positive underperformance signals.
- **Mitigation:** Applied Empirical Bayes shrinkage modeling ($M=25$). Agent CSAT estimates are shrunken toward their operational peer group baseline according to sample credibility.
- **Remaining Risk:** Unobserved sentiment among the 55.78% non-respondents cannot be recovered. CSAT measures satisfaction strictly among survey respondents, not total customer sentiment.

---

## 3. Premature CSAT on Open / Pending Tickets

- **Issue:** Exactly 249 tickets have recorded CSAT responses despite having ticket status set to `open` or `pending`.
- **Impact:** Surveys were triggered prematurely (e.g., following an intermediate reply or automated system notification) before customer issues were fully resolved.
- **Mitigation:** Included these responses in agent CSAT evaluations per business operating practice (as customer feedback was genuinely captured), but flagged them in ticket-level data tables.
- **Remaining Risk:** If an agent subsequently resolved the issue satisfactorily, the customer's premature mid-interaction rating may understate ultimate resolution quality.

---

## 4. Missing Order ID Linkage

- **Issue:** Exactly 4,107 tickets (34.95%) contain null or missing `order_id` fields, while 7,643 tickets (65.05%) possess valid order IDs. These unlinked tickets encompass general pre-sales inquiries, compatibility questions, warranty queries where the customer did not provide an invoice, or phone contacts without CRM order lookups.
- **Impact:** These tickets cannot be deterministically matched to product SKUs, purchase values, delivery timelines, or order financial records.
- **Mitigation:** The metrics engine isolates order-dependent analyses (such as double-dipping detection and warranty replacement costing) strictly to tickets with validated `order_id` values. All 7,643 non-null order IDs successfully match records in `data/orders.csv` (0 orphans).
- **Remaining Risk:** Secondary warranty replacements or manual offline refunds initiated on unlinked tickets cannot be tracked in cross-channel financial leakage calculations.

---

## 5. Agent Name Collision

- **Issue:** Exact duplicate full name collision exists in `data/agents.csv`:
  - `A3006` — **Kavya Pandey** (Chat Frontline, Morning shift, Tier 1)
  - `A3029` — **Kavya Pandey** (Logistics, Morning shift, Tier 1)  
  *(Note: A3004 Siddharth Kapoor and A3007 Siddharth Trivedi share a first name but have distinct surnames).*
- **Impact:** Grouping metrics by agent display name aggregates two separate individuals across different teams into a single synthetic entity, corrupting individual performance tracking.
- **Mitigation:** Enforced strict primary-key integrity across the codebase (`agent_id` is the immutable identifier). All joins, aggregations, and display labels combine ID and name (e.g., `A3006 (Kavya Pandey)` vs `A3029 (Kavya Pandey)`).
- **Remaining Risk:** Referential integrity is 100% resolved in code and data. Operational risk remains if supervisors conduct offline verbal coaching without referencing unique agent IDs.

---

## 6. Voice IVR Transcription Artifacts

- **Issue:** Voice channel interactions contain automated speech-to-text transcripts with phonetic errors, acoustic truncations, missing punctuation, and absent speaker separation tags.
- **Impact:** Automated keyword matching or NLP models can misinterpret customer emotion, miss product references, or misclassify root causes.
- **Mitigation:** Diagnostic prompts explicitly incorporate noise-tolerance rules. The deterministic metrics engine relies on audited operational timestamps and structured fields rather than unstructured voice transcript text.
- **Remaining Risk:** Qualitative AI diagnosis of voice tickets carries higher error bounds and lower confidence scores than text-native email or chat interactions.

---

## 7. Category "Other" Miscategorization

- **Issue:** Exactly 1,732 tickets (14.74%) are categorized under generic "Other", obscuring the real operational issue (including Pulse 2 hardware defects, delayed courier shipments, and accidental orders).
- **Impact:** Distorts category-level volume distributions and hides critical product defect clusters from departmental dashboards.
- **Mitigation:** Stratified 30 "Other" tickets into the targeted AI qualitative audit sample (Stratum 4) to diagnose latent topics and operational drivers.
- **Remaining Risk:** Full historical re-tagging of all 1,732 tickets requires full-scale NLP processing, which exceeds the approved 100-ticket diagnostic scope.

---

## 8. Transfer-Field Migration Discrepancy

- **Issue:** Legacy ticket transfers across tiers were tracked inconsistently during the Zendesk-to-Freshdesk migration, with some multi-tier handoffs overwriting initial queue attributes.
- **Impact:** Agents closing transferred tickets can inherit handle time accumulated in earlier queues.
- **Mitigation:** Tier 2 Escalations & Warranty agents are isolated into an independent peer group, comparing their handle times and CSAT strictly against peers handling escalated tickets.
- **Remaining Risk:** Precise first-contact resolution (FCR) cannot be computed with 100% certainty for multi-touch tickets without access to raw event logs.

---

## 9. Queue / Case-Mix Selection Effects

- **Issue:** Inherent ticket difficulty varies dramatically across support queues. Tier 2 agents handle 100% defective hardware, while Frontline Chat agents handle quick navigational queries. Frontline agents assigned to the Hardware Triage rota (Kavya's Four: A3004, A3005, A3006, A3007) absorbed double the baseline volume of defective Pulse 2 units.
- **Impact:** Unadjusted company-wide rankings create severe structural bias, punishing agents assigned to difficult queues or defective product lines.
- **Mitigation:** Established 6 operational peer groups; evaluated performance strictly within peer baselines; explicitly contextualized Kavya's Four to prevent unwarranted punitive shortlisting.
- **Remaining Risk:** Minor intra-peer group variance (such as weekend versus weekday shift volume) remains unadjusted.

---

## 10. AI Qualitative Diagnostic Role & Uncertainty

- **Issue:** The targeted AI diagnostic layer achieved 30.0% (6/20) exact all-field agreement across 5 simultaneous multi-class dimensions against the human expert gold standard, with primary root cause agreement at 45.0% (9/20) and agent handling signal agreement at 80.0% (16/20). Discrepancies stem from terse agent notes (`cx ok -TF`), courier transit vs warehouse fulfillment distinctions, and service-center bench delays.
- **Impact:** AI ticket audit outputs are probabilistic qualitative diagnostic estimates, not deterministic compliance facts.
- **Mitigation:** The AI auditor is strictly bounded as an auxiliary diagnostic tool across 100 tickets. It is prohibited from modifying performance metrics, agent rankings, CSAT, handle times, or training shortlists.
- **Remaining Risk:** Supervisors must review AI diagnostic tags as decision-support suggestions rather than definitive compliance verdicts.

---

## 11. Financial Governance & Terminology Register

- **Historical SLA Breach Penalty Liability:**
  - Formula: $1,064\text{ breaches} \times ₹350 = ₹372,400$
  - Annualized baseline: $709.3\text{ breaches/year} \times ₹350 = ₹248,267\text{/year}$
  - Scenarios: 25% (₹62,067/yr), 50% (₹124,133/yr), 75% (₹186,200/yr). Presented strictly as modeled sensitivity scenarios, not guaranteed outcomes.
- **Double-Dipping Financial Exposure (Process-Control Opportunity):**
  - Confirmed affected orders: 131 distinct orders
  - Historical cash refunds issued: ₹355,434
  - Replacement policy-cost exposure: ₹235,500 (calculated as $\sum (\text{Product Unit Cost} + ₹340\text{ logistics surcharge per Policy §5})$ = ₹189,260 product cost + ₹46,240 logistics surcharge)
  - Combined historical exposure: ₹590,934 (annualized over 18m: $₹590,934 \times \frac{12}{18} = ₹393,956\text{/year}$)
  - Governance rule: Presented strictly as historical financial exposure and an IT/CRM process-control validation opportunity. Never described as "guaranteed savings" or "training ROI."

---

## Quality Gate Sign-Off Matrix

| Dimension | Source Truth | Audit Status | Severity | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **Timestamps / Handle Time** | 2,309 corrected | Fully Mitigated | Low (Post-Fix) | Safe for Production |
| **CSAT Response Rate** | 5,196 / 11,750 (44.22%) | Fully Audited | Low | Safe for Production |
| **Missing Order ID** | 4,107 / 11,750 (34.95%) | Fully Audited | Low | Safe for Production |
| **Agent Name Collision** | Kavya Pandey (A3006/A3029)| Primary-Key Bound| None | Safe for Production |
| **Category "Other"** | 1,732 / 11,750 (14.74%) | Stratified Audit | Low | Safe for Production |
| **Financial KPIs** | ₹3.72L SLA, ₹5.91L DD | Verified to Source | None | Safe for Production |
| **Queue Bias Neutralization**| 6 Peer Groups | Fully Isolated | Low (Post-Fix) | Safe for Production |
| **AI Qualitative Layer** | Auxiliary Diagnostic | Bounded | Medium | Decision Support Only |

**Quality Gate Conclusion:** **PASS WITH LIMITATIONS**  
The dataset and metrics engine are certified for decision-support dashboard implementation under the documented operational guardrails.
