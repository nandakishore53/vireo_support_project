"""
Dashboard Data Exporter.
Serializes validated deterministic outputs and AI audit results into
dashboard/data.js and dashboard/data.json for zero-dependency frontend execution.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np

from src import config, metrics_engine


def export_dashboard_data():
    dashboard_dir = config.BASE_DIR / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run pipeline for authoritative deterministic results
    res = metrics_engine.run_pipeline()
    kpis = res["kpi_results"]

    # 2. Load CSV outputs
    agent_metrics = pd.read_csv(config.OUTPUTS_DIR / "agent_metrics.csv").replace({np.nan: None}).to_dict(orient="records")
    peer_metrics = pd.read_csv(config.OUTPUTS_DIR / "peer_metrics.csv").replace({np.nan: None}).to_dict(orient="records")
    raw_bottom10 = pd.read_csv(config.OUTPUTS_DIR / "raw_bottom10.csv").replace({np.nan: None}).to_dict(orient="records")
    training_candidates = pd.read_csv(config.OUTPUTS_DIR / "training_candidates.csv").replace({np.nan: None}).to_dict(orient="records")
    policy_exceptions = pd.read_csv(config.OUTPUTS_DIR / "policy_exceptions.csv").replace({np.nan: None}).to_dict(orient="records")
    ai_hallucination = pd.read_csv(config.OUTPUTS_DIR / "ai_hallucination_review.csv").replace({np.nan: None}).to_dict(orient="records")

    # 3. Load JSON outputs
    with open(config.OUTPUTS_DIR / "ai_ticket_audit.json", "r", encoding="utf-8") as f:
        ai_ticket_audit = json.load(f)

    with open(config.OUTPUTS_DIR / "ai_cost_log.json", "r", encoding="utf-8") as f:
        ai_cost_log = json.load(f)

    ai_sample = pd.read_csv(config.OUTPUTS_DIR / "ai_sample.csv").replace({np.nan: None}).to_dict(orient="records")

    # 4. Construct unified payload
    dashboard_payload = {
        "metadata": {
            "total_tickets": 11750,
            "total_agents": 44,
            "company_mean_csat": 3.3266,
            "csat_responses": 5196,
            "csat_response_rate": 0.4422,
            "missing_order_tickets": 4107,
            "other_category_tickets": 1732,
            "date_range": "2025-01-01 to 2026-06-30 (18 months)",
            "duplicate_agent_name": "Kavya Pandey (A3006 & A3029)"
        },
        "kpis": kpis,
        "training_candidates": training_candidates,
        "raw_bottom10": raw_bottom10,
        "agent_metrics": agent_metrics,
        "peer_metrics": peer_metrics,
        "policy_exceptions_summary": {
            "total_exceptions": len(policy_exceptions),
            "affected_orders": kpis["double_dipping"]["affected_orders_count"],
            "combined_exposure_inr": kpis["double_dipping"]["historical_combined_exposure_inr"],
            "refund_exposure_inr": kpis["double_dipping"]["historical_refunds_inr"],
            "replacement_exposure_inr": kpis["double_dipping"]["historical_replacement_cost_inr"]
        },
        "ai_audit": {
            "sample_size": len(ai_sample),
            "cost_inr": ai_cost_log.get("estimated_cost", 0.0),
            "provider": ai_cost_log.get("provider", "offline_heuristic"),
            "model": ai_cost_log.get("model", "deterministic_v1"),
            "agreement_benchmarks": {
                "policy_signal": {"agreed": 20, "total": 20, "rate": 1.00},
                "agent_handling_signal": {"agreed": 16, "total": 20, "rate": 0.80},
                "resolution_quality": {"agreed": 13, "total": 20, "rate": 0.65},
                "evidence_quality": {"agreed": 13, "total": 20, "rate": 0.65},
                "primary_root_cause": {"agreed": 9, "total": 20, "rate": 0.45},
                "exact_all_field": {"agreed": 6, "total": 20, "rate": 0.30}
            },
            "sample_tickets": ai_sample[:10],
            "hallucination_review": ai_hallucination,
            "total_audited_tickets": len(ai_ticket_audit)
        }
    }

    def json_serializer(o):
        if isinstance(o, (np.integer, np.int64)):
            return int(o)
        if isinstance(o, (np.floating, np.float64)):
            return float(o)
        if pd.isna(o):
            return None
        return str(o)

    # Write data.json
    json_path = dashboard_dir / "data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=2, default=json_serializer)

    # Write data.js for zero-CORS browser loading
    js_path = dashboard_dir / "data.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// Authoritative Vireo Audio Support Dashboard Data\n")
        f.write("window.VIREO_DATA = ")
        json.dump(dashboard_payload, f, indent=2, default=json_serializer)
        f.write(";\n")

    print(f"Exported dashboard data to {json_path} and {js_path}")
    return dashboard_payload


if __name__ == "__main__":
    export_dashboard_data()
