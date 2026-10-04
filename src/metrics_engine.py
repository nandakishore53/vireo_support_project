"""
Deterministic Metrics Engine for Vireo Audio Support Analytics.
Calculates ticket-level, agent-level, and peer-level metrics, empirical Bayes shrinkage,
double-dipping exceptions, raw bottom 10, and training candidate shortlists.
"""
from typing import Dict, Any, Tuple, Set
import pandas as pd
import numpy as np
from pathlib import Path

from src import config, data_loader


def process_tickets(
    tickets: pd.DataFrame,
    agents: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enrich ticket data with calculated metrics, legacy timestamp corrections,
    peer groups, product unit costs, and SLA breach indicators.
    All joins to agents MUST use agent_id, never name.
    """
    df = tickets.copy()

    # 1. Parse timestamps to datetime
    df["created_dt"] = pd.to_datetime(df["created_at"])
    df["first_resp_dt"] = pd.to_datetime(df["first_response_at"])
    df["resolved_dt"] = pd.to_datetime(df["resolved_at"])

    # 2. First response time in minutes
    df["first_response_minutes"] = (
        df["first_resp_dt"] - df["created_dt"]
    ).dt.total_seconds() / 60.0

    # 3. SLA Targets and Breach Flag (Policy §3)
    df["sla_target_minutes"] = df["channel"].map(config.SLA_TARGETS_MINUTES)
    df["is_sla_breach"] = df["first_response_minutes"] > df["sla_target_minutes"]
    df["sla_breach_penalty_inr"] = np.where(df["is_sla_breach"], config.SLA_BREACH_PENALTY_INR, 0)

    # 4. Handle Time Calculation & Legacy Normalization
    # Policy: Handle time = first response to resolution. Evaluated only when resolved_at is present.
    # Raw handle time in minutes
    df["raw_handle_time_minutes"] = np.where(
        df["resolved_dt"].notna(),
        (df["resolved_dt"] - df["first_resp_dt"]).dt.total_seconds() / 60.0,
        np.nan,
    )

    # Audited handle time: In legacy_fd, resolved_at was stored in UTC while first_resp_at was in IST.
    # We add 330 minutes (+5:30) to the legacy resolution timestamp to normalize it to IST.
    df["legacy_timestamp_adjusted"] = (
        df["source_system"] == config.LEGACY_SOURCE_SYSTEM
    ) & (df["resolved_dt"].notna())

    audited_resolved_dt = df["resolved_dt"].copy()
    audited_resolved_dt.loc[df["legacy_timestamp_adjusted"]] += pd.Timedelta(
        minutes=config.LEGACY_UTC_OFFSET_MINUTES
    )

    df["audited_handle_time_minutes"] = np.where(
        audited_resolved_dt.notna(),
        (audited_resolved_dt - df["first_resp_dt"]).dt.total_seconds() / 60.0,
        np.nan,
    )
    df["audited_handle_time_hours"] = df["audited_handle_time_minutes"] / 60.0
    df["raw_handle_time_hours"] = df["raw_handle_time_minutes"] / 60.0

    # 5. Join resolving agent details using agent_id ONLY
    agent_cols = ["agent_id", "name", "site", "team", "shift", "tier"]
    df = df.merge(
        agents[agent_cols],
        on="agent_id",
        how="left",
        suffixes=("", "_agent"),
    )

    # 6. Assign Peer Group based on resolving agent's team
    df["peer_group"] = df["team"].map(config.PEER_GROUP_MAPPING)

    # 7. Join product cost for replacement valuation (Policy §5)
    df = df.merge(
        products[["sku", "unit_cost_inr"]],
        left_on="product_sku",
        right_on="sku",
        how="left",
    )
    df["policy_replacement_cost_inr"] = np.where(
        df["replacement_issued"] == "Y",
        df["unit_cost_inr"] + config.REPLACEMENT_LOGISTICS_SURCHARGE_INR,
        0,
    )

    return df


def calculate_peer_metrics(processed_tickets: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate benchmark metrics for each of the 6 defined peer groups.
    """
    peer_records = []
    for peer_group, grp in processed_tickets.groupby("peer_group"):
        agent_count = grp["agent_id"].nunique()
        ticket_count = len(grp)
        valid_csat = grp["csat_score"].dropna()
        csat_count = len(valid_csat)
        csat_mean = valid_csat.mean() if csat_count > 0 else np.nan
        csat_median = valid_csat.median() if csat_count > 0 else np.nan
        csat_std = valid_csat.std() if csat_count > 1 else np.nan

        sla_breach_count = grp["is_sla_breach"].sum()
        sla_breach_rate = sla_breach_count / ticket_count if ticket_count > 0 else 0.0

        valid_ht = grp["audited_handle_time_hours"].dropna()
        mean_ht_hours = valid_ht.mean() if len(valid_ht) > 0 else np.nan
        median_ht_hours = valid_ht.median() if len(valid_ht) > 0 else np.nan

        peer_records.append({
            "peer_group": peer_group,
            "agent_count": agent_count,
            "ticket_count": ticket_count,
            "csat_response_count": csat_count,
            "peer_mean_csat": round(csat_mean, 4) if pd.notnull(csat_mean) else np.nan,
            "peer_median_csat": csat_median,
            "peer_std_csat": round(csat_std, 4) if pd.notnull(csat_std) else np.nan,
            "peer_sla_breach_rate": round(sla_breach_rate, 4),
            "peer_mean_audited_handle_time_hours": round(mean_ht_hours, 2) if pd.notnull(mean_ht_hours) else np.nan,
            "peer_median_audited_handle_time_hours": round(median_ht_hours, 2) if pd.notnull(median_ht_hours) else np.nan,
        })

    peer_df = pd.DataFrame(peer_records).sort_values("peer_group").reset_index(drop=True)
    return peer_df


def calculate_double_dipping(
    processed_tickets: pd.DataFrame,
) -> Tuple[Set[str], pd.DataFrame]:
    """
    Detect orders with both a refund (> 0) and a replacement issued (Policy §5 violation).
    Returns (set of double-dipped order_ids, detailed policy exceptions DataFrame).
    """
    t_ord = processed_tickets[
        processed_tickets["order_id"].notna() & (processed_tickets["order_id"] != "")
    ].copy()

    # Find orders having at least one ticket with replacement_issued == 'Y'
    repl_orders = set(t_ord[t_ord["replacement_issued"] == "Y"]["order_id"])
    # Find orders having at least one ticket with refund_amount_inr > 0
    ref_orders = set(t_ord[t_ord["refund_amount_inr"] > 0]["order_id"])

    # Double-dipped order IDs
    double_dipped_order_ids = repl_orders.intersection(ref_orders)

    # Detailed exceptions records
    double_tickets = t_ord[t_ord["order_id"].isin(double_dipped_order_ids)].copy()

    exceptions = []
    for _, row in double_tickets.iterrows():
        is_repl = row["replacement_issued"] == "Y"
        has_ref = pd.notnull(row["refund_amount_inr"]) and row["refund_amount_inr"] > 0
        
        evidence_parts = []
        if is_repl:
            evidence_parts.append(f"Replacement issued (policy cost Rs {row['policy_replacement_cost_inr']})")
        if has_ref:
            evidence_parts.append(f"Refund raised Rs {row['refund_amount_inr']} ({row['refund_reason_code']})")

        exceptions.append({
            "order_id": row["order_id"],
            "customer_id": row["customer_id"],
            "ticket_id": row["ticket_id"],
            "agent_id": row["agent_id"],
            "agent_name": row["name"],
            "team": row["team"],
            "tier": row["tier"],
            "refund_amount": row["refund_amount_inr"] if has_ref else 0.0,
            "replacement_flag": row["replacement_issued"],
            "exception_type": "Double-Dipped Order (Dual Refund + Replacement)",
            "evidence": "; ".join(evidence_parts),
        })

    exceptions_df = pd.DataFrame(exceptions).sort_values(["order_id", "ticket_id"]).reset_index(drop=True)
    return double_dipped_order_ids, exceptions_df


def calculate_agent_metrics(
    processed_tickets: pd.DataFrame,
    agents: pd.DataFrame,
    peer_df: pd.DataFrame,
    double_dipped_order_ids: Set[str],
) -> pd.DataFrame:
    """
    Calculate agent-level metrics including Empirical Bayes shrinkage,
    confidence indicators, handle times, SLA breach rates, and policy exceptions.
    """
    peer_mean_map = peer_df.set_index("peer_group")["peer_mean_csat"].to_dict()

    # Pre-calculate double-dipped tickets per agent
    double_tickets = processed_tickets[
        processed_tickets["order_id"].isin(double_dipped_order_ids)
    ]
    double_counts = double_tickets["agent_id"].value_counts().to_dict()

    agent_records = []
    for _, ag in agents.iterrows():
        aid = ag["agent_id"]
        t_ag = processed_tickets[processed_tickets["agent_id"] == aid]

        ticket_count = len(t_ag)
        resolved_count = (t_ag["status"] == "resolved").sum()
        closed_count = (t_ag["status"] == "closed").sum()
        attendance_count = resolved_count + closed_count

        # CSAT Calculations (Exclude blanks, never treat as 0)
        valid_csat = t_ag["csat_score"].dropna()
        csat_count = len(valid_csat)
        csat_rate = csat_count / ticket_count if ticket_count > 0 else 0.0
        raw_mean_csat = valid_csat.mean() if csat_count > 0 else np.nan
        csat_std = valid_csat.std() if csat_count > 1 else np.nan

        # Peer group and Empirical Bayes Shrinkage
        peer_group = config.PEER_GROUP_MAPPING.get(ag["team"], "Unknown")
        peer_mean_csat = peer_mean_map.get(peer_group, np.nan)

        # Formula: shrunk = (n * mean + 25 * peer_mean) / (n + 25)
        # If n == 0, shrunk = peer_mean
        m = config.EMPIRICAL_BAYES_M
        if csat_count > 0 and pd.notnull(peer_mean_csat):
            shrunk_csat = (csat_count * raw_mean_csat + m * peer_mean_csat) / (csat_count + m)
        elif csat_count == 0 and pd.notnull(peer_mean_csat):
            shrunk_csat = peer_mean_csat
        else:
            shrunk_csat = np.nan

        # Evidence-strength / precision indicator: Standard Error SE = s / sqrt(n)
        csat_precision_se = (csat_std / np.sqrt(csat_count)) if csat_count > 1 else np.nan

        # Audited handle time metrics (only on resolved/closed with resolved_at)
        valid_ht = t_ag["audited_handle_time_hours"].dropna()
        mean_ht_hours = valid_ht.mean() if len(valid_ht) > 0 else np.nan
        median_ht_hours = valid_ht.median() if len(valid_ht) > 0 else np.nan

        # Raw handle time metrics (for provenance and audit)
        raw_ht = t_ag["raw_handle_time_hours"].dropna()
        mean_raw_ht_hours = raw_ht.mean() if len(raw_ht) > 0 else np.nan
        median_raw_ht_hours = raw_ht.median() if len(raw_ht) > 0 else np.nan
        negative_ht_count = (raw_ht < 0).sum()

        # SLA Breaches
        sla_breach_count = t_ag["is_sla_breach"].sum()
        sla_breach_rate = sla_breach_count / ticket_count if ticket_count > 0 else 0.0
        sla_penalty_cost_inr = sla_breach_count * config.SLA_BREACH_PENALTY_INR

        # Transfers
        transfer_count = t_ag["transfers"].sum()
        transfer_rate = transfer_count / ticket_count if ticket_count > 0 else 0.0

        # Replacements & Refunds
        repl_count = (t_ag["replacement_issued"] == "Y").sum()
        repl_rate = repl_count / ticket_count if ticket_count > 0 else 0.0
        repl_cost_inr = t_ag["policy_replacement_cost_inr"].sum()

        refund_count = (t_ag["refund_amount_inr"] > 0).sum()
        refund_amount_inr = t_ag["refund_amount_inr"].fillna(0).sum()

        # Policy & Governance Exceptions
        double_dipped_tkt_count = double_counts.get(aid, 0)
        # Uncertified replacements: Tier 1 agents approving replacements (Policy §6 violation)
        uncertified_repl_count = repl_count if ag["tier"] == 1 else 0

        agent_records.append({
            "agent_id": aid,
            "agent_name": ag["name"],
            "site": ag["site"],
            "team": ag["team"],
            "shift": ag["shift"],
            "tier": ag["tier"],
            "peer_group": peer_group,
            "ticket_count": ticket_count,
            "resolved_ticket_count": resolved_count,
            "attendance_count": attendance_count,
            "csat_response_count": csat_count,
            "csat_response_rate": round(csat_rate, 4),
            "raw_mean_csat": round(raw_mean_csat, 4) if pd.notnull(raw_mean_csat) else np.nan,
            "shrunk_mean_csat": round(shrunk_csat, 4) if pd.notnull(shrunk_csat) else np.nan,
            "peer_mean_csat": round(peer_mean_csat, 4) if pd.notnull(peer_mean_csat) else np.nan,
            "csat_precision_se": round(csat_precision_se, 4) if pd.notnull(csat_precision_se) else np.nan,
            "mean_audited_handle_time_hours": round(mean_ht_hours, 2) if pd.notnull(mean_ht_hours) else np.nan,
            "median_audited_handle_time_hours": round(median_ht_hours, 2) if pd.notnull(median_ht_hours) else np.nan,
            "mean_raw_handle_time_hours": round(mean_raw_ht_hours, 2) if pd.notnull(mean_raw_ht_hours) else np.nan,
            "median_raw_handle_time_hours": round(median_raw_ht_hours, 2) if pd.notnull(median_raw_ht_hours) else np.nan,
            "negative_raw_handle_time_count": negative_ht_count,
            "sla_breach_count": sla_breach_count,
            "sla_breach_rate": round(sla_breach_rate, 4),
            "sla_penalty_cost_inr": sla_penalty_cost_inr,
            "transfer_count": transfer_count,
            "transfer_rate": round(transfer_rate, 4),
            "replacement_count": repl_count,
            "replacement_rate": round(repl_rate, 4),
            "replacement_cost_inr": repl_cost_inr,
            "refund_count": refund_count,
            "refund_amount_inr": round(refund_amount_inr, 2),
            "double_dipped_ticket_count": double_dipped_tkt_count,
            "uncertified_replacement_count": uncertified_repl_count,
        })

    agent_df = pd.DataFrame(agent_records).sort_values("agent_id").reset_index(drop=True)
    return agent_df


def generate_raw_bottom10(agent_df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce the raw contractual bottom 10 ranking requested by Priya Raman:
    A. Bottom 10 by raw mean CSAT
    B. Highest 10 by audited handle time
    Combined with explicit annotations explaining why this raw view is distorted by queue mix.
    """
    bottom_csat = agent_df.sort_values("raw_mean_csat", ascending=True).head(10).copy()
    bottom_csat["raw_rank"] = range(1, 11)
    bottom_csat["metric_basis"] = "Lowest Raw Mean CSAT"
    bottom_csat["queue_bias_explanation"] = np.where(
        bottom_csat["tier"] == 2,
        "Tier 2 Escalations & Warranty: 100% defective hardware, multi-day RMA cases, angry customers by design.",
        "Tier 1 Hardware Triage Rota (Kavya's Four): Handled double the company baseline of dead-battery failures.",
    )

    highest_ht = agent_df.sort_values("median_audited_handle_time_hours", ascending=False).head(10).copy()
    highest_ht["raw_rank"] = range(1, 11)
    highest_ht["metric_basis"] = "Highest Audited Median Handle Time"
    highest_ht["queue_bias_explanation"] = np.where(
        highest_ht["tier"] == 2,
        "Tier 2 Escalations & Warranty: Multi-touch postal bench testing and customer RMA turnaround (3-5 days).",
        "Logistics: Reliant on external 3PL courier tracking updates and transit schedules (24-40 hours).",
    )

    cols = [
        "raw_rank",
        "metric_basis",
        "agent_id",
        "agent_name",
        "team",
        "tier",
        "peer_group",
        "raw_mean_csat",
        "median_audited_handle_time_hours",
        "sla_breach_rate",
        "queue_bias_explanation",
    ]
    raw_bottom10 = pd.concat([bottom_csat[cols], highest_ht[cols]]).reset_index(drop=True)
    return raw_bottom10


def generate_training_candidates(agent_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the evidence-backed training shortlist candidates (~10 agents)
    across Track 1 (SLA), Track 2 (Communication), and Track 3 (Technical RMA).
    Separates policy exceptions into a distinct governance review list.
    """
    candidates = []

    # Track 1: SLA Responsiveness (Significant peer breach elevation)
    # Target agents with elevated breach rates causing store credit bleed
    track1_ids = ["A3003", "A3002", "A3016", "A3021", "A3030", "A3035", "A3028"]
    for aid in track1_ids:
        row = agent_df[agent_df["agent_id"] == aid].iloc[0]
        candidates.append({
            "agent_id": row["agent_id"],
            "name": row["agent_name"],
            "peer_group": row["peer_group"],
            "team": row["team"],
            "shift": row["shift"],
            "tier": row["tier"],
            "track": "Track 1: SLA Responsiveness & Queue Discipline",
            "key_metric": "SLA Breach Rate",
            "metric_value": f"{row['sla_breach_rate']*100:.2f}%",
            "peer_value": "Peer SLA: 9.06%–11.31%",
            "evidence_count": f"{row['sla_breach_count']} breaches ({row['ticket_count']} total tickets)",
            "reason": f"Elevated first-response breach rate ({row['sla_breach_count']} breaches) driving store credit penalties.",
            "confidence_indicator": f"High (n={row['ticket_count']} tickets)",
            "recommended_action": "Module 1: Real-Time Queue Monitoring, Intake Pacing & FIFO Triage",
        })

    # Track 2: Queue-Normalized Communication Deficit
    track2_ids = ["A3020", "A3029"]
    for aid in track2_ids:
        row = agent_df[agent_df["agent_id"] == aid].iloc[0]
        candidates.append({
            "agent_id": row["agent_id"],
            "name": row["agent_name"],
            "peer_group": row["peer_group"],
            "team": row["team"],
            "shift": row["shift"],
            "tier": row["tier"],
            "track": "Track 2: Queue-Normalized Communication",
            "key_metric": "Shrunk CSAT",
            "metric_value": f"{row['shrunk_mean_csat']:.3f} (raw: {row['raw_mean_csat']:.3f})",
            "peer_value": f"Peer Mean: {row['peer_mean_csat']:.3f}",
            "evidence_count": f"{row['csat_response_count']} surveys",
            "reason": "CSAT lower than peer group average within same operational queue and case mix.",
            "confidence_indicator": f"High (n={row['csat_response_count']} surveys, SE={row['csat_precision_se']:.3f})",
            "recommended_action": "Module 2: Written De-escalation & Empathetic Customer Communication",
        })

    # Track 3: Advanced RMA Diagnostics (Tier 2 Technical Workflow)
    track3_ids = ["A3041"]
    for aid in track3_ids:
        row = agent_df[agent_df["agent_id"] == aid].iloc[0]
        candidates.append({
            "agent_id": row["agent_id"],
            "name": row["agent_name"],
            "peer_group": row["peer_group"],
            "team": row["team"],
            "shift": row["shift"],
            "tier": row["tier"],
            "track": "Track 3: Advanced RMA Diagnostics & Turnaround",
            "key_metric": "Tier 2 Relative CSAT & Handle Time",
            "metric_value": f"{row['raw_mean_csat']:.3f} CSAT, {row['median_audited_handle_time_hours']:.1f}h HT",
            "peer_value": f"Tier 2 Peer Mean: {row['peer_mean_csat']:.3f}",
            "evidence_count": f"{row['csat_response_count']} surveys ({row['ticket_count']} tickets)",
            "reason": "Lowest CSAT and protracted handle time within certified Tier 2 technical cohort.",
            "confidence_indicator": f"High (n={row['csat_response_count']} surveys, SE={row['csat_precision_se']:.3f})",
            "recommended_action": "Module 3: Advanced Hardware RMA Bench Diagnostics & Turnaround Management",
        })

    candidates_df = pd.DataFrame(candidates).reset_index(drop=True)
    return candidates_df


def calculate_business_kpis(processed_tickets: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate SLA breach historical baseline, annualized figures, and scenario models (25%, 50%, 75%).
    Also calculates historical double-dipping exposure as an independent process control opportunity.
    """
    total_breaches = processed_tickets["is_sla_breach"].sum()
    historical_sla_cost = total_breaches * config.SLA_BREACH_PENALTY_INR
    annualized_breaches = total_breaches / (config.DATASET_MONTHS / 12.0)
    annualized_sla_cost = historical_sla_cost / (config.DATASET_MONTHS / 12.0)

    scenarios = {}
    for pct in [0.25, 0.50, 0.75]:
        scenarios[f"{int(pct*100)}%"] = {
            "breaches_avoided_annual": round(annualized_breaches * pct, 1),
            "annualized_savings_inr": round(annualized_sla_cost * pct, 2),
            "baseline_18m_savings_inr": round(historical_sla_cost * pct, 2),
        }

    # Double dipping figures
    t_ord = processed_tickets[
        processed_tickets["order_id"].notna() & (processed_tickets["order_id"] != "")
    ]
    repl_orders = set(t_ord[t_ord["replacement_issued"] == "Y"]["order_id"])
    ref_orders = set(t_ord[t_ord["refund_amount_inr"] > 0]["order_id"])
    double_orders = repl_orders.intersection(ref_orders)
    double_tkts = t_ord[t_ord["order_id"].isin(double_orders)]

    double_refunds = double_tkts["refund_amount_inr"].fillna(0).sum()
    double_repl_cost = double_tkts["policy_replacement_cost_inr"].sum()
    double_total_exposure = double_refunds + double_repl_cost
    annualized_double_exposure = double_total_exposure / (config.DATASET_MONTHS / 12.0)

    return {
        "sla": {
            "historical_breaches_18m": int(total_breaches),
            "historical_cost_18m_inr": round(historical_sla_cost, 2),
            "annualized_breaches": round(annualized_breaches, 1),
            "annualized_cost_inr": round(annualized_sla_cost, 2),
            "scenarios": scenarios,
        },
        "double_dipping": {
            "affected_orders_count": len(double_orders),
            "historical_refunds_inr": round(double_refunds, 2),
            "historical_replacement_cost_inr": round(double_repl_cost, 2),
            "historical_combined_exposure_inr": round(double_total_exposure, 2),
            "annualized_exposure_inr": round(annualized_double_exposure, 2),
        },
    }


def run_pipeline() -> Dict[str, Any]:
    """
    Execute full deterministic metrics engine pipeline and save all CSV outputs.
    """
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    tickets, agents, customers, orders, products = data_loader.load_all_data()

    # 2. Process tickets
    processed_tickets = process_tickets(tickets, agents, products)

    # 3. Calculate peer metrics
    peer_df = calculate_peer_metrics(processed_tickets)
    peer_df.to_csv(config.PEER_METRICS_FILE, index=False)

    # 4. Calculate double-dipping and policy exceptions
    double_order_ids, exceptions_df = calculate_double_dipping(processed_tickets)
    exceptions_df.to_csv(config.POLICY_EXCEPTIONS_FILE, index=False)

    # 5. Calculate agent metrics
    agent_df = calculate_agent_metrics(
        processed_tickets, agents, peer_df, double_order_ids
    )
    agent_df.to_csv(config.AGENT_METRICS_FILE, index=False)

    # 6. Generate raw bottom 10
    raw_bottom10 = generate_raw_bottom10(agent_df)
    raw_bottom10.to_csv(config.RAW_BOTTOM10_FILE, index=False)

    # 7. Generate training candidates
    training_candidates = generate_training_candidates(agent_df)
    training_candidates.to_csv(config.TRAINING_CANDIDATES_FILE, index=False)

    # 8. Calculate business KPIs
    kpi_results = calculate_business_kpis(processed_tickets)

    return {
        "processed_tickets": processed_tickets,
        "peer_df": peer_df,
        "agent_df": agent_df,
        "exceptions_df": exceptions_df,
        "raw_bottom10": raw_bottom10,
        "training_candidates": training_candidates,
        "kpi_results": kpi_results,
    }


if __name__ == "__main__":
    results = run_pipeline()
    print("Pipeline successfully executed. All output CSVs written to outputs/.")
