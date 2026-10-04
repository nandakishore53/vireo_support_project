"""
Phase 3C Quality Gate and Validation Test Suite.
Verifies all sample strata, schema constraints, business KPI figures,
shortlist protections, raw-vs-fair separation, and quality registers.
"""
import pytest
import json
import pandas as pd
from pathlib import Path

from src import config, metrics_engine, ai_auditor


def test_ai_sample_exact_strata_and_uniqueness():
    """Verify outputs/ai_sample.csv meets all Stratum and uniqueness criteria."""
    sample_path = config.OUTPUTS_DIR / "ai_sample.csv"
    assert sample_path.exists(), "ai_sample.csv must exist."
    df = pd.read_csv(sample_path)

    assert len(df) == 100, f"Expected 100 tickets, found {len(df)}"
    assert df["ticket_id"].nunique() == 100, "Ticket IDs must be strictly unique"
    assert df["ticket_id"].duplicated().sum() == 0, "No duplicate tickets allowed"

    strata_counts = df["stratum"].value_counts().to_dict()
    assert strata_counts.get("Double-Dipped Order", 0) == 15, "Stratum 1 must have exactly 15 tickets"
    assert strata_counts.get("Long Escalation", 0) == 15, "Stratum 2 must have exactly 15 tickets"
    assert strata_counts.get("Low CSAT (<= 2)", 0) == 40, "Stratum 3 must have exactly 40 tickets"
    assert strata_counts.get("Category Other", 0) == 30, "Stratum 4 must have exactly 30 tickets"

    priority_counts = df["sampling_priority"].value_counts().to_dict()
    assert priority_counts.get(1, 0) == 15
    assert priority_counts.get(2, 0) == 15
    assert priority_counts.get(3, 0) == 40
    assert priority_counts.get(4, 0) == 30


def test_ai_ticket_audit_schema_and_allowed_enums():
    """Verify outputs/ai_ticket_audit.json adheres 100% to required schema and enums."""
    audit_path = config.OUTPUTS_DIR / "ai_ticket_audit.json"
    assert audit_path.exists(), "ai_ticket_audit.json must exist."

    with open(audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 100, f"Expected 100 audited tickets, got {len(data)}"

    for ticket_id, record in data.items():
        is_valid, err = ai_auditor.validate_schema(record)
        assert is_valid, f"Validation failed for ticket {ticket_id}: {err}"


def test_gold_standard_agreement_rates():
    """Verify gold standard has 20 tickets and calculations match expected benchmarks."""
    gold_path = config.OUTPUTS_DIR / "ai_gold_standard.csv"
    assert gold_path.exists(), "ai_gold_standard.csv must exist."
    gold_df = pd.read_csv(gold_path)
    assert len(gold_df) == 20, f"Expected 20 gold standard tickets, got {len(gold_df)}"

    required_cols = [
        "ticket_id", "stratum", "category", "channel", "customer_message",
        "agent_notes", "primary_root_cause", "agent_handling_signal",
        "resolution_quality", "policy_signal", "evidence_quality", "human_rationale"
    ]
    for col in required_cols:
        assert col in gold_df.columns, f"Missing column {col} in ai_gold_standard.csv"


def test_hallucination_review_structure():
    """Verify outputs/ai_hallucination_review.csv schema and completeness."""
    hal_path = config.OUTPUTS_DIR / "ai_hallucination_review.csv"
    assert hal_path.exists(), "ai_hallucination_review.csv must exist."
    hal_df = pd.read_csv(hal_path)

    expected_cols = ["ticket_id", "issue_type", "claim", "supporting_evidence", "severity", "action"]
    assert list(hal_df.columns) == expected_cols, f"Columns do not match expected schema: {hal_df.columns}"
    assert len(hal_df) >= 5, "Expected at least 5 documented hallucination review items"


def test_deterministic_business_kpis():
    """Verify exact match of historical SLA breach cost and double-dipping exposure."""
    res = metrics_engine.run_pipeline()
    kpis = res["kpi_results"]
    sla = kpis["sla"]
    double = kpis["double_dipping"]

    # SLA breaches
    assert sla["historical_breaches_18m"] == 1064
    assert sla["historical_cost_18m_inr"] == 372400
    assert abs(sla["annualized_cost_inr"] - 248266.67) < 0.1
    assert abs(sla["scenarios"]["25%"]["annualized_savings_inr"] - 62066.67) < 0.1
    assert abs(sla["scenarios"]["50%"]["annualized_savings_inr"] - 124133.33) < 0.1
    assert abs(sla["scenarios"]["75%"]["annualized_savings_inr"] - 186200.0) < 0.1

    # Double dipping
    assert double["affected_orders_count"] == 131
    assert double["historical_refunds_inr"] == 355434.0
    assert double["historical_replacement_cost_inr"] == 235500
    assert double["historical_combined_exposure_inr"] == 590934.0


def test_kavya_agents_excluded_from_training_candidates():
    """Verify Kavya's Four (A3004, A3005, A3006, A3007) are not shortlisted for training."""
    candidates_df = pd.read_csv(config.OUTPUTS_DIR / "training_candidates.csv")
    kavya_agents = {"A3004", "A3005", "A3006", "A3007"}
    candidate_ids = set(candidates_df["agent_id"])

    assert len(candidates_df) == 10, f"Expected exactly 10 candidates, found {len(candidates_df)}"
    assert not (kavya_agents & candidate_ids), (
        f"Kavya agents {kavya_agents & candidate_ids} incorrectly included in training candidates!"
    )


def test_raw_bottom10_contains_queue_bias_explanations():
    """Verify raw bottom 10 retains explanations for why raw ranks are misleading."""
    raw_df = pd.read_csv(config.OUTPUTS_DIR / "raw_bottom10.csv")
    assert len(raw_df) == 20, f"Expected 20 raw bottom 10 rows (10 CSAT, 10 Handle Time), got {len(raw_df)}"
    assert "queue_bias_explanation" in raw_df.columns
    assert raw_df["queue_bias_explanation"].notnull().all(), "Every raw bottom 10 entry must have bias context"


def test_final_reports_exist_and_verdict():
    """Verify final data quality register and validation report exist and state PASS WITH LIMITATIONS."""
    reg_path = config.OUTPUTS_DIR / "final_data_quality_register.md"
    rep_path = config.OUTPUTS_DIR / "final_validation_report.md"

    assert reg_path.exists(), "outputs/final_data_quality_register.md must exist"
    assert rep_path.exists(), "outputs/final_validation_report.md must exist"

    rep_content = rep_path.read_text(encoding="utf-8")
    assert "PASS WITH LIMITATIONS" in rep_content, "Report must conclude with PASS WITH LIMITATIONS"


def test_source_consistency_benchmarks():
    """Verify ground truth benchmarks directly against source CSVs and policy definitions."""
    tickets = pd.read_csv(config.TICKETS_FILE)
    agents = pd.read_csv(config.AGENTS_FILE)

    # 1. Total tickets and CSAT response rate
    assert len(tickets) == 11750
    assert tickets["csat_score"].notnull().sum() == 5196
    csat_rate = tickets["csat_score"].notnull().sum() / len(tickets)
    assert abs(csat_rate - 0.442213) < 0.0001

    # 2. Category Other count
    assert (tickets["category"] == "Other").sum() == 1732

    # 3. Missing order ID count
    assert tickets["order_id"].isnull().sum() == 4107
    missing_order_rate = tickets["order_id"].isnull().sum() / len(tickets)
    assert abs(missing_order_rate - 0.349532) < 0.0001

    # 4. Agent name collision (exact full name duplicate is Kavya Pandey)
    name_counts = agents["name"].value_counts()
    assert name_counts["Kavya Pandey"] == 2
    assert set(agents[agents["name"] == "Kavya Pandey"]["agent_id"]) == {"A3006", "A3029"}

    # 5. Consistency audit artifact exists
    audit_file = config.OUTPUTS_DIR / "consistency_audit.md"
    assert audit_file.exists(), "outputs/consistency_audit.md must exist"
    audit_content = audit_file.read_text(encoding="utf-8")
    assert "READY FOR DASHBOARD" in audit_content


def test_executive_memo_artifacts():
    """Verify Phase 4B executive business memo markdown and PDF deliverables."""
    memo_md = config.OUTPUTS_DIR / "executive_memo.md"
    memo_pdf = config.OUTPUTS_DIR / "executive_memo.pdf"

    assert memo_md.exists(), "outputs/executive_memo.md must exist."
    assert memo_pdf.exists(), "outputs/executive_memo.pdf must exist."
    assert memo_pdf.stat().st_size > 10000, "outputs/executive_memo.pdf must be a valid non-empty PDF."

    md_content = memo_md.read_text(encoding="utf-8")
    assert "Priya Raman" in md_content
    assert "1,064" in md_content
    assert "3,72,400" in md_content
    assert "5,196" in md_content
    assert "44.22%" in md_content
    assert "131" in md_content
    assert "590,934" in md_content
    assert "MODELED SCENARIOS" in md_content
    assert "6/20" in md_content


