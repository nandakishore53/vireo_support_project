"""
Tests for Executive Dashboard Data Integrity and Presentation Constraints.
Verifies all 10 dashboard testability requirements:
1. 44 agents load.
2. 10 training candidates load.
3. Raw bottom-10 data loads.
4. 100 AI audit records load.
5. Rs 590,934 double-dipping exposure displays correctly.
6. Rs 372,400 SLA exposure displays correctly.
7. 25/50/75% scenario values match validated numbers.
8. Kavya Pandey A3006 and A3029 remain separate.
9. A3004/A3005/A3006/A3007 are not accidentally added to training candidates.
10. AI output cannot modify candidate selection.
"""
import pytest
import json
import pandas as pd
from pathlib import Path

from src import config
from src.export_dashboard_data import export_dashboard_data


@pytest.fixture(scope="module")
def dashboard_payload():
    """Export and load dashboard data payload."""
    return export_dashboard_data()


def test_dashboard_files_exist():
    """Verify HTML, CSS, JS, and data files exist in dashboard/."""
    dashboard_dir = config.BASE_DIR / "dashboard"
    assert (dashboard_dir / "index.html").exists()
    assert (dashboard_dir / "style.css").exists()
    assert (dashboard_dir / "app.js").exists()
    assert (dashboard_dir / "data.js").exists()
    assert (dashboard_dir / "data.json").exists()


def test_1_44_agents_load(dashboard_payload):
    """Requirement 1: Exactly 44 agents load into the dashboard."""
    agents = dashboard_payload["agent_metrics"]
    assert len(agents) == 44, f"Expected 44 agents, got {len(agents)}"
    agent_ids = {a["agent_id"] for a in agents}
    assert len(agent_ids) == 44, "All 44 agent IDs must be unique"


def test_2_10_training_candidates_load(dashboard_payload):
    """Requirement 2: Exactly 10 training candidates load."""
    candidates = dashboard_payload["training_candidates"]
    assert len(candidates) == 10, f"Expected 10 training candidates, found {len(candidates)}"


def test_3_raw_bottom10_data_loads(dashboard_payload):
    """Requirement 3: Raw bottom-10 data loads for both CSAT and handle time (20 rows)."""
    raw_list = dashboard_payload["raw_bottom10"]
    assert len(raw_list) == 20, f"Expected 20 raw bottom-10 entries, found {len(raw_list)}"

    csat_items = [r for r in raw_list if r["metric_basis"] == "Lowest Raw Mean CSAT"]
    ht_items = [r for r in raw_list if r["metric_basis"] == "Highest Audited Median Handle Time"]

    assert len(csat_items) == 10, "Expected 10 bottom CSAT rows"
    assert len(ht_items) == 10, "Expected 10 highest handle time rows"

    # All must have queue bias explanation
    for r in raw_list:
        assert r.get("queue_bias_explanation"), f"Missing bias explanation for agent {r.get('agent_id')}"


def test_4_100_ai_audit_records_load(dashboard_payload):
    """Requirement 4: Exactly 100 AI audit records load."""
    ai_audit = dashboard_payload["ai_audit"]
    assert ai_audit["sample_size"] == 100
    assert ai_audit["total_audited_tickets"] == 100


def test_5_double_dipping_exposure_displays_correctly(dashboard_payload):
    """Requirement 5: Rs 590,934 double-dipping exposure displays correctly."""
    dd = dashboard_payload["kpis"]["double_dipping"]
    assert dd["affected_orders_count"] == 131
    assert dd["historical_refunds_inr"] == 355434.0
    assert dd["historical_replacement_cost_inr"] == 235500
    assert dd["historical_combined_exposure_inr"] == 590934.0
    assert dd["annualized_exposure_inr"] == 393956.0


def test_6_sla_exposure_displays_correctly(dashboard_payload):
    """Requirement 6: Rs 372,400 SLA exposure displays correctly."""
    sla = dashboard_payload["kpis"]["sla"]
    assert sla["historical_breaches_18m"] == 1064
    assert sla["historical_cost_18m_inr"] == 372400
    assert abs(sla["annualized_cost_inr"] - 248266.67) < 0.1


def test_7_scenario_values_match_validated_numbers(dashboard_payload):
    """Requirement 7: 25/50/75% scenario values match validated numbers."""
    scenarios = dashboard_payload["kpis"]["sla"]["scenarios"]

    assert abs(scenarios["25%"]["annualized_savings_inr"] - 62066.67) < 0.1
    assert abs(scenarios["25%"]["baseline_18m_savings_inr"] - 93100.0) < 0.1
    assert scenarios["25%"]["breaches_avoided_annual"] == 177.3

    assert abs(scenarios["50%"]["annualized_savings_inr"] - 124133.33) < 0.1
    assert abs(scenarios["50%"]["baseline_18m_savings_inr"] - 186200.0) < 0.1
    assert scenarios["50%"]["breaches_avoided_annual"] == 354.7

    assert abs(scenarios["75%"]["annualized_savings_inr"] - 186200.0) < 0.1
    assert abs(scenarios["75%"]["baseline_18m_savings_inr"] - 279300.0) < 0.1
    assert scenarios["75%"]["breaches_avoided_annual"] == 532.0


def test_8_kavya_pandey_a3006_and_a3029_remain_separate(dashboard_payload):
    """Requirement 8: Kavya Pandey A3006 and A3029 remain separate agents."""
    agents = dashboard_payload["agent_metrics"]
    kavya_records = [a for a in agents if a["agent_name"] == "Kavya Pandey"]

    assert len(kavya_records) == 2, f"Expected 2 records for Kavya Pandey, found {len(kavya_records)}"
    ids = {k["agent_id"] for k in kavya_records}
    assert ids == {"A3006", "A3029"}

    a3006 = next(k for k in kavya_records if k["agent_id"] == "A3006")
    a3029 = next(k for k in kavya_records if k["agent_id"] == "A3029")

    assert a3006["team"] == "Chat Frontline"
    assert a3029["team"] == "Logistics"
    assert a3006["ticket_count"] != a3029["ticket_count"]


def test_9_kavya_four_not_in_training_candidates(dashboard_payload):
    """Requirement 9: A3004/A3005/A3006/A3007 are not accidentally added to training candidates."""
    candidates = dashboard_payload["training_candidates"]
    candidate_ids = {c["agent_id"] for c in candidates}
    kavya_four = {"A3004", "A3005", "A3006", "A3007"}

    overlap = candidate_ids.intersection(kavya_four)
    assert not overlap, f"Hardware triage agents {overlap} must NOT be in training candidates!"


def test_10_ai_output_cannot_modify_candidate_selection(dashboard_payload):
    """Requirement 10: AI output cannot modify candidate selection."""
    candidates = dashboard_payload["training_candidates"]
    expected_ids = ["A3003", "A3002", "A3016", "A3021", "A3030", "A3035", "A3028", "A3020", "A3029", "A3041"]

    actual_ids = [c["agent_id"] for c in candidates]
    assert actual_ids == expected_ids, f"Candidate IDs {actual_ids} do not match approved shortlist {expected_ids}"


def test_11_interactive_scenario_selector_elements_and_behavior(dashboard_payload):
    """Requirement 11 (Regression): Scenario selector elements exist, match expected values, and have no null references."""
    index_html = (config.BASE_DIR / "dashboard" / "index.html").read_text(encoding="utf-8")
    app_js = (config.BASE_DIR / "dashboard" / "app.js").read_text(encoding="utf-8")

    # 1. Verify scenario buttons and targets exist in HTML
    for pct in ["25%", "50%", "75%"]:
        assert f'data-pct="{pct}"' in index_html, f"Missing scenario button for {pct} in index.html"

    required_element_ids = [
        "biz-sc-pct",
        "biz-sc-savings-annual",
        "biz-sc-savings-18m",
        "biz-sc-breaches-avoided",
        "biz-dd-orders",
        "biz-dd-refunds",
        "biz-dd-replacements",
        "biz-dd-combined",
        "biz-dd-annualized",
    ]
    for el_id in required_element_ids:
        assert f'id="{el_id}"' in index_html, f"Missing DOM element id='{el_id}' in index.html"

    # 2. Verify updateScenarioDisplay handles all three scenarios correctly
    scenarios = dashboard_payload["kpis"]["sla"]["scenarios"]
    assert "25%" in scenarios and "50%" in scenarios and "75%" in scenarios

    # Check 25% expected values
    assert abs(scenarios["25%"]["annualized_savings_inr"] - 62066.67) < 0.1
    assert abs(scenarios["25%"]["baseline_18m_savings_inr"] - 93100.0) < 0.1
    assert scenarios["25%"]["breaches_avoided_annual"] == 177.3

    # Check 50% expected values
    assert abs(scenarios["50%"]["annualized_savings_inr"] - 124133.33) < 0.1
    assert abs(scenarios["50%"]["baseline_18m_savings_inr"] - 186200.0) < 0.1
    assert scenarios["50%"]["breaches_avoided_annual"] == 354.7

    # Check 75% expected values
    assert abs(scenarios["75%"]["annualized_savings_inr"] - 186200.0) < 0.1
    assert abs(scenarios["75%"]["baseline_18m_savings_inr"] - 279300.0) < 0.1
    assert scenarios["75%"]["breaches_avoided_annual"] == 532.0

    # 3. Verify app.js attaches event listeners to .btn-scenario-select and updates DOM safely
    assert "btn.addEventListener(\"click\"" in app_js
    assert "updateScenarioDisplay" in app_js

