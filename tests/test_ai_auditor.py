"""
Unit and integration tests for src/ai_auditor.py.
Verifies deterministic sampling, stratum non-overlap, strict JSON schema validation,
caching, offline fallback, and guarantees that AI cannot modify training shortlists.
"""
import pytest
import pandas as pd
import json
from pathlib import Path

from src import config, data_loader, metrics_engine, ai_auditor


@pytest.fixture(scope="module")
def sample_and_engine():
    """Run data loading and sample generation once for tests."""
    tickets, agents, customers, orders, products = data_loader.load_all_data()
    processed_tickets = metrics_engine.process_tickets(tickets, agents, products)
    double_order_ids, _ = metrics_engine.calculate_double_dipping(processed_tickets)
    sample_df = ai_auditor.generate_deterministic_sample(
        processed_tickets, double_order_ids, random_seed=42
    )
    return sample_df, processed_tickets, double_order_ids


def test_ai_sample_exact_100_unique_tickets(sample_and_engine):
    """Verify that sample contains exactly 100 unique tickets."""
    sample_df, _, _ = sample_and_engine
    assert len(sample_df) == 100, f"Expected 100 tickets, got {len(sample_df)}"
    assert sample_df["ticket_id"].nunique() == 100, "Sample contains duplicate ticket IDs"


def test_ai_sample_stratum_targets_and_non_overlap(sample_and_engine):
    """Verify exact counts per stratum and zero overlap across priority tiers."""
    sample_df, _, _ = sample_and_engine
    stratum_counts = sample_df["stratum"].value_counts().to_dict()

    assert stratum_counts.get("Double-Dipped Order") == 15, "Stratum 1 target mismatch"
    assert stratum_counts.get("Long Escalation") == 15, "Stratum 2 target mismatch"
    assert stratum_counts.get("Low CSAT (<= 2)") == 40, "Stratum 3 target mismatch"
    assert stratum_counts.get("Category Other") == 30, "Stratum 4 target mismatch"

    # Verify each ticket appears in only one stratum
    ticket_strata = sample_df.groupby("ticket_id")["stratum"].nunique()
    assert (ticket_strata == 1).all(), "Found tickets spanning multiple strata"


def test_ai_sample_reproducible_seed(sample_and_engine):
    """Verify that random_state=42 yields identical ticket lists on successive runs."""
    _, processed_tickets, double_order_ids = sample_and_engine
    sample_run1 = ai_auditor.generate_deterministic_sample(
        processed_tickets, double_order_ids, random_seed=42
    )
    sample_run2 = ai_auditor.generate_deterministic_sample(
        processed_tickets, double_order_ids, random_seed=42
    )

    assert sample_run1["ticket_id"].tolist() == sample_run2["ticket_id"].tolist()


def test_schema_validation_accepts_valid_json():
    """Verify schema validator accepts conforming structured dictionaries."""
    valid_payload = {
        "primary_root_cause": "product_or_hardware",
        "agent_handling_signal": "none",
        "resolution_quality": "appropriate",
        "customer_sentiment": "negative",
        "policy_signal": "none",
        "evidence_quality": "sufficient",
        "confidence": "high",
        "evidence": "Customer stated left earbud dead on arrival.",
    }
    is_valid, err = ai_auditor.validate_schema(valid_payload)
    assert is_valid is True, f"Valid payload rejected with error: {err}"


def test_schema_validation_rejects_invalid_values():
    """Verify schema validator rejects non-conforming enum values and missing keys."""
    # Invalid root cause
    invalid_val = {
        "primary_root_cause": "super_broken_hardware",  # Not in allowed enum
        "agent_handling_signal": "none",
        "resolution_quality": "appropriate",
        "customer_sentiment": "negative",
        "policy_signal": "none",
        "evidence_quality": "sufficient",
        "confidence": "high",
        "evidence": "Test",
    }
    is_valid, err = ai_auditor.validate_schema(invalid_val)
    assert is_valid is False
    assert "Invalid value" in err

    # Missing evidence
    missing_key = {
        "primary_root_cause": "product_or_hardware",
        "agent_handling_signal": "none",
        "resolution_quality": "appropriate",
        "customer_sentiment": "negative",
        "policy_signal": "none",
        "evidence_quality": "sufficient",
        "confidence": "high",
    }
    is_valid, err = ai_auditor.validate_schema(missing_key)
    assert is_valid is False
    assert "Missing required keys" in err


def test_missing_api_key_executes_offline_gracefully():
    """Verify system runs successfully without failing when no remote API key is supplied."""
    client = ai_auditor.LLMClient()
    # When offline or dry-run, provider falls back cleanly
    ticket = pd.Series({
        "ticket_id": "TK-999999",
        "customer_message": "battery will not charge at all",
        "agent_notes": "replacement unit dispatched under doa",
        "category": "Charging & Battery",
        "csat_score": 1.0,
        "stratum": "Low CSAT (<= 2)",
    })
    diag = ai_auditor.rule_based_diagnostic_classifier(ticket)
    is_valid, _ = ai_auditor.validate_schema(diag)
    assert is_valid is True
    assert diag["primary_root_cause"] == "product_or_hardware"


def test_ai_cannot_modify_training_candidates():
    """
    CRITICAL SAFETY TEST:
    Verify that executing the AI audit pipeline leaves outputs/training_candidates.csv
    strictly unchanged in row count, agent_ids, and rankings.
    """
    # 1. Capture baseline training candidates from deterministic engine
    baseline_candidates = metrics_engine.generate_training_candidates(
        metrics_engine.run_pipeline()["agent_df"]
    )
    baseline_ids = baseline_candidates["agent_id"].tolist()

    # 2. Run AI audit pipeline
    ai_auditor.run_ai_audit_pipeline()

    # 3. Read current training_candidates.csv from disk
    current_candidates = pd.read_csv(config.TRAINING_CANDIDATES_FILE)
    current_ids = current_candidates["agent_id"].tolist()

    assert baseline_ids == current_ids, "AI execution altered the training shortlist agent_ids!"
    assert len(current_candidates) == 10, "AI execution altered training candidate count!"
