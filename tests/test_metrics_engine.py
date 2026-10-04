"""
Unit tests for src/metrics_engine.py.
Verifies metric calculations, legacy timestamp corrections, shrinkage,
peer group benchmarks, double-dipping detection, and shortlist generation.
"""
import pytest
import pandas as pd
import numpy as np

from src import config, data_loader, metrics_engine


@pytest.fixture(scope="module")
def pipeline_results():
    """Run metrics engine pipeline once for all tests."""
    return metrics_engine.run_pipeline()


def test_legacy_handle_time_correction(pipeline_results):
    """Verify that legacy UTC-to-IST offset resolves all 2,309 negative handle times to 0."""
    df = pipeline_results["processed_tickets"]

    raw_neg_count = (df["raw_handle_time_minutes"] < 0).sum()
    audited_neg_count = (df["audited_handle_time_minutes"] < 0).sum()

    assert raw_neg_count == 2309, f"Expected 2,309 negative raw handle times, found {raw_neg_count}"
    assert audited_neg_count == 0, f"Expected 0 negative audited handle times, found {audited_neg_count}"


def test_sla_breach_metrics(pipeline_results):
    """Verify SLA breach counts and store credit penalty liabilities."""
    df = pipeline_results["processed_tickets"]

    total_breaches = df["is_sla_breach"].sum()
    total_cost = df["sla_breach_penalty_inr"].sum()

    assert total_breaches == 1064, f"Expected 1,064 SLA breaches, got {total_breaches}"
    assert total_cost == 372400, f"Expected Rs 372,400 penalty cost, got {total_cost}"


def test_double_dipping_detection(pipeline_results):
    """Verify that deterministic double-dipping detection finds exactly 131 affected orders."""
    kpi_results = pipeline_results["kpi_results"]
    double_info = kpi_results["double_dipping"]

    assert double_info["affected_orders_count"] == 131, (
        f"Expected 131 double-dipped orders, found {double_info['affected_orders_count']}"
    )
    assert double_info["historical_combined_exposure_inr"] == 590934.0, (
        f"Expected Rs 590,934 combined exposure, found {double_info['historical_combined_exposure_inr']}"
    )


def test_empirical_bayes_shrinkage(pipeline_results):
    """Verify mathematical correctness of Empirical Bayes shrinkage for each agent."""
    agent_df = pipeline_results["agent_df"]

    for _, row in agent_df.iterrows():
        n = row["csat_response_count"]
        raw = row["raw_mean_csat"]
        peer = row["peer_mean_csat"]
        shrunk = row["shrunk_mean_csat"]

        if n > 0:
            expected_shrunk = (n * raw + 25 * peer) / (n + 25)
            assert np.isclose(shrunk, expected_shrunk, atol=1e-4), (
                f"Shrinkage mismatch for {row['agent_id']}: expected {expected_shrunk}, got {shrunk}"
            )
        else:
            assert np.isclose(shrunk, peer, atol=1e-4), (
                f"Zero-response agent {row['agent_id']} should equal peer mean {peer}, got {shrunk}"
            )


def test_peer_groups_structure(pipeline_results):
    """Verify that exactly 6 peer groups exist and Returns & Billing merges Returns Desk and Billing."""
    peer_df = pipeline_results["peer_df"]
    agent_df = pipeline_results["agent_df"]

    expected_peer_groups = {
        "Chat Frontline",
        "Email Frontline",
        "Voice Frontline",
        "Logistics",
        "Returns & Billing",
        "Escalations & Warranty",
    }
    actual_peer_groups = set(peer_df["peer_group"])
    assert actual_peer_groups == expected_peer_groups, f"Peer groups mismatch: {actual_peer_groups}"

    # Verify agent count in Returns & Billing is 3 (Returns) + 4 (Billing) = 7
    rb_agents = agent_df[agent_df["peer_group"] == "Returns & Billing"]
    assert len(rb_agents) == 7, f"Expected 7 agents in Returns & Billing, found {len(rb_agents)}"


def test_raw_bottom10_separation(pipeline_results):
    """Verify raw bottom 10 is generated with explicit explanations and contains 20 rows (10 CSAT, 10 HT)."""
    raw_bottom10 = pipeline_results["raw_bottom10"]
    assert len(raw_bottom10) == 20

    csat_part = raw_bottom10[raw_bottom10["metric_basis"] == "Lowest Raw Mean CSAT"]
    ht_part = raw_bottom10[raw_bottom10["metric_basis"] == "Highest Audited Median Handle Time"]

    assert len(csat_part) == 10
    assert len(ht_part) == 10
    assert "queue_bias_explanation" in raw_bottom10.columns


def test_training_candidates_structure(pipeline_results):
    """Verify training shortlist contains 10 candidates with structured human-readable reasons."""
    candidates = pipeline_results["training_candidates"]

    assert len(candidates) == 10, f"Expected 10 training candidates, found {len(candidates)}"
    required_candidate_cols = {
        "agent_id",
        "name",
        "peer_group",
        "track",
        "key_metric",
        "metric_value",
        "peer_value",
        "evidence_count",
        "reason",
        "confidence_indicator",
        "recommended_action",
    }
    assert required_candidate_cols.issubset(set(candidates.columns))
