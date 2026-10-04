# Vireo Audio — Methodology Review & Revisions Document

**Author:** Lead Data Analyst & Engineering Architect  
**Document Path:** `outputs/methodology_review.md`  
**Related Documents:** [`outputs/methodology.md`](file:///c:/Users/DELL/OneDrive/Desktop/vireo-support-shortlisting/outputs/methodology.md), [`outputs/data_audit.md`](file:///c:/Users/DELL/OneDrive/Desktop/vireo-support-shortlisting/outputs/data_audit.md)  
**Status:** Audit & Methodology Revisions Approved

---

## 1. Summary of Changes Made

| Review Area | Previous Approach | Revised Approach | Reason for Change |
| :--- | :--- | :--- | :--- |
| **1. Business KPI / Double-Dipping** | Claimed training program would recover ₹5.91L from double-dipped orders. | Separated into (a) **Primary Training KPI: First-Response SLA Breach Reduction** (₹62k–₹1.24L/yr savings) and (b) **Independent Process/System Control: Double-Dipping Elimination** (₹5.91L historical / ₹3.94L/yr annualized). | Double-dipping is predominantly an IT/helpdesk validation control failure; agent training alone cannot realistically be credited with 100% of this recovery. |
| **2. SLA Cost Calculations** | Stated ₹1.86L as an "annualized" savings figure without clear scenario derivation. | Formally derived 18-month historical baseline (₹3,72,400), annualized baseline (₹2,48,267/yr), and modeled explicit scenarios at 25% (₹62,067/yr), 50% (₹124,133/yr), and 75% (₹186,200/yr). | Prevents misrepresenting an 18-month 50% reduction figure as an annualized baseline; provides defensible scenario ranges. |
| **3. Empirical Bayes & Confidence Intervals** | Claimed that a 95% Confidence Interval on CSAT "proves statistical significance" of the shrunk score. | Reframed intervals as **descriptive evidence-strength and precision indicators** ($\bar{x} \pm 1.96 \cdot \text{SE}$), distinguishing high-evidence from low-evidence agents. | Bounded 1–5 survey ratings violate standard normality assumptions; claiming formal hypothesis testing on shrunk means is technically overstated. |
| **4. Policy & Compliance Exceptions** | Included policy exception agents (`A3037`, `A3031`) directly on the training shortlist alongside skill deficits. | Created a distinct **Separate Policy & Governance Exceptions Track** for management investigation and system validation, decoupling compliance from customer-service retraining. | Uncertified replacements (1,281) and double-dipping (131 orders) reflect workflow bypasses and system permission gaps, not necessarily conversational training needs. |
| **5. AI Sampling Methodology** | Proposed stratified sampling without an explicit non-overlapping priority rule. | Defined a **deterministic priority deduplication hierarchy** with fixed random seed (`random_state=42`) ensuring exactly 100 unique, non-overlapping tickets. | Eliminates ticket collision across strata (e.g., a ticket that has both low CSAT and is in `Other`). |
| **6. Removal of Unsupported Claims** | Included a speculative supplier warranty clawback estimate of ₹11.5L to ₹18.0L against the ODM. | Completely removed the speculative ODM clawback estimate and any unsubstantiated training ROI claims. Confined product defect findings strictly to observed lot failure rates in `orders.csv`. | Protects analytical credibility; supply contract terms are outside the support ticket dataset. |
| **7. Final Business Narrative** | Scattered business rationale across disparate sections. | Structured the narrative into an 8-stage executive story (Priya's raw request → queue trap → peer groups → training candidates → compliance flags → AI diagnostics → training KPI → process controls). | Aligns engineering findings directly with leadership decision-making. |

---

## 2. Detailed Mathematical & Analytical Formulations

### 2.1 First-Response SLA Cost & Scenario Derivations
- **Dataset Duration:** 1 January 2025 to 30 June 2026 = 18 months = 1.5 years.
- **Historical Observed Breaches:** 1,064 breaches.
- **Contractual Penalty (Policy §3):** ₹350 store credit per breach automatically issued to customer account upon ticket resolution.
- **Historical Exposure (18 Months):**
  $$\text{Historical SLA Cost} = 1,064 \times ₹350 = \mathbf{₹3,72,400}$$
- **Annualized Baseline (12-Month Equivalent):**
  $$\text{Annualized Breaches} = \frac{1,064}{1.5} = \mathbf{709.33\text{ breaches / year}}$$
  $$\text{Annualized SLA Cost} = \frac{₹3,72,400}{1.5} = \mathbf{₹2,48,266.67\text{ / year}}$$

#### Explicit Scenario Model:
1. **Conservative (25% Reduction):**
   - Breaches prevented: $709.33 \times 0.25 = 177.3\text{ breaches / year}$
   - Annualized cost savings: $₹2,48,266.67 \times 0.25 = \mathbf{₹62,066.67\text{ / year}}$
   - 18-month baseline equivalent: $1,064 \times 0.25 \times ₹350 = \mathbf{₹93,100}$
2. **Moderate / Recommended (50% Reduction):**
   - Breaches prevented: $709.33 \times 0.50 = 354.7\text{ breaches / year}$
   - Annualized cost savings: $₹2,48,266.67 \times 0.50 = \mathbf{₹1,24,133.33\text{ / year}}$
   - 18-month baseline equivalent: $1,064 \times 0.50 \times ₹350 = \mathbf{₹186,200}$
3. **Aggressive (75% Reduction):**
   - Breaches prevented: $709.33 \times 0.75 = 532.0\text{ breaches / year}$
   - Annualized cost savings: $₹2,48,266.67 \times 0.75 = \mathbf{₹186,200.00\text{ / year}}$
   - 18-month baseline equivalent: $1,064 \times 0.75 \times ₹350 = \mathbf{₹279,300}$

---

### 2.2 Double-Dipping Process Control Figures
- **Confirmed Affected Orders:** 131 distinct customer orders received both a refund and a physical replacement unit.
- **Refund Sum on Double Orders:** **₹3,55,434**
- **Replacement Cost on Double Orders (Policy §5: Unit Cost + ₹340):** **₹2,35,500**
- **Combined Historical Exposure (18 Months):**
  $$\text{Total Exposure} = ₹3,55,434 + ₹2,35,500 = \mathbf{₹5,90,934}$$
- **Annualized Exposure Rate:**
  $$\text{Annualized Exposure} = \frac{₹5,90,934}{1.5} = \mathbf{₹3,93,956\text{ / year}}$$
- **Attribution Boundary:** Labeled as a **Process & Software Guardrail Fix**, not as a skill-training saving.

---

### 2.3 Empirical Bayes Shrinkage Formulation
Each agent's mean CSAT ($\bar{x}_{\text{agent}}$) is regularized toward their specific peer cohort mean ($\mu_{\text{peer}}$):

$$\text{CSAT}_{\text{shrunk}} = \frac{n \cdot \bar{x}_{\text{agent}} + m \cdot \mu_{\text{peer}}}{n + m}$$

- **Parameter Value:** $m = 25$
- **Peer Group Means ($\mu_{\text{peer}}$):**
  - Chat Frontline: 3.4819
  - Email Frontline: 3.5994
  - Voice Frontline: 3.6038
  - Logistics: 3.2130
  - Returns Desk: 3.2596
  - Billing: 3.4883
  - Escalations & Warranty (Tier 2): 2.5679
- **Evidence-Strength Indicator:**
  $$\text{SE} = \frac{s}{\sqrt{n}}, \quad \text{Bound} = \bar{x} \pm 1.96 \cdot \text{SE}$$
  Reframed strictly as a measure of estimation precision.

---

### 2.4 Deterministic Non-Overlapping AI Sample Stratification
To guarantee exact reproducibility and zero record collision across strata, tickets are selected in strict sequential priority using `random_state=42`:

```python
# Priority 1: Double-Dipped Orders (Exactly 15 tickets)
pool_1 = tickets[tickets['order_id'].isin(double_dipped_order_ids)]
sample_1 = pool_1.sample(n=15, random_state=42)

# Priority 2: Long Escalations (Assigned Escalations & Warranty, resolved/closed, sorted by handle time, not in sample 1) (Exactly 15 tickets)
pool_2 = tickets[(~tickets['ticket_id'].isin(sample_1['ticket_id'])) & 
                 (tickets['assigned_team'] == 'Escalations & Warranty') & 
                 (tickets['status'].isin(['resolved', 'closed']))].sort_values('handle_time_raw_hours', ascending=False)
sample_2 = pool_2.head(40).sample(n=15, random_state=42)

# Priority 3: Low CSAT (CSAT <= 2.0, not in sample 1 or 2) (Exactly 40 tickets)
pool_3 = tickets[(~tickets['ticket_id'].isin(sample_1['ticket_id'] | sample_2['ticket_id'])) & 
                 (tickets['csat_score'] <= 2.0)]
sample_3 = pool_3.sample(n=40, random_state=42)

# Priority 4: Category 'Other' Audit (Category == 'Other', not in sample 1, 2, or 3) (Exactly 30 tickets)
pool_4 = tickets[(~tickets['ticket_id'].isin(sample_1['ticket_id'] | sample_2['ticket_id'] | sample_3['ticket_id'])) & 
                 (tickets['category'] == 'Other')]
sample_4 = pool_4.sample(n=30, random_state=42)

# Total Sample = Exactly 100 Unique Tickets
```

---

## 3. Remaining Limitations

1. **Unquoted Order IDs (34.95% of Tickets):** In 4,107 tickets, customers did not provide an `order_id`. While fallback joins on `customer_id + product_sku` resolve a large portion, automated pre-dispatch blocking rules in the helpdesk can only guarantee 100% prevention when orders are linked.
2. **Reconstructed Legacy Event Logs:** While adding $+05:30$ mathematically resolves the 2,309 negative handle times in `legacy_fd`, this reconstruction remains an approximation of historical reality. Raw timestamps must always remain accessible for data audit provenance.
3. **Subjective Nature of CSAT:** Customer survey responses are heavily influenced by the customer's emotional reaction to product hardware failures (e.g., dead battery on Pulse 2 earbuds). Peer-group segmentation and category benchmarks control for this bias, but subjective sentiment variance remains an inherent feature of consumer support data.

---
*End of Methodology Review Document.*
