"""
Unit tests for src/data_loader.py.
Verifies file loading, schema validation, and join referential integrity.
"""
import pytest
import pandas as pd
from pathlib import Path

from src import config, data_loader


def test_load_all_data_success():
    """Verify all 5 datasets load successfully with expected row counts."""
    tickets, agents, customers, orders, products = data_loader.load_all_data()

    assert len(tickets) == 11750, f"Expected 11,750 tickets, got {len(tickets)}"
    assert len(agents) == 44, f"Expected 44 agents, got {len(agents)}"
    assert len(customers) == 9500, f"Expected 9,500 customers, got {len(customers)}"
    assert len(orders) == 15500, f"Expected 15,500 orders, got {len(orders)}"
    assert len(products) == 14, f"Expected 14 products, got {len(products)}"


def test_agent_display_name_collision_handled():
    """Verify that multiple agents sharing the name 'Kavya Pandey' have distinct agent_ids."""
    agents = data_loader.load_agents()
    kavya_agents = agents[agents["name"] == "Kavya Pandey"]

    assert len(kavya_agents) == 2, "Expected exactly 2 agents named 'Kavya Pandey'"
    agent_ids = set(kavya_agents["agent_id"])
    assert agent_ids == {"A3006", "A3029"}, f"Unexpected agent_ids for Kavya Pandey: {agent_ids}"

    # Verify site, team, and tier differences
    a3006 = kavya_agents[kavya_agents["agent_id"] == "A3006"].iloc[0]
    a3029 = kavya_agents[kavya_agents["agent_id"] == "A3029"].iloc[0]

    assert a3006["site"] == "Indore" and a3006["team"] == "Chat Frontline"
    assert a3029["site"] == "Bengaluru" and a3029["team"] == "Logistics"


def test_ticket_agent_id_referential_integrity():
    """Verify that all tickets map to a valid agent_id in agents.csv."""
    tickets, agents, _, _, _ = data_loader.load_all_data()
    valid_agent_ids = set(agents["agent_id"])
    ticket_agent_ids = set(tickets["agent_id"])

    unmatched = ticket_agent_ids - valid_agent_ids
    assert len(unmatched) == 0, f"Found unmatched agent_ids in tickets: {unmatched}"


def test_missing_column_raises_error(tmp_path):
    """Verify that omitting a required column raises a ValueError."""
    bad_agents_csv = tmp_path / "bad_agents.csv"
    bad_agents_csv.write_text("agent_id,name,site\nA3001,John,Indore\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        data_loader.load_agents(bad_agents_csv)


def test_duplicate_primary_key_raises_error(tmp_path):
    """Verify that duplicate primary keys raise a ValueError."""
    dup_products_csv = tmp_path / "dup_products.csv"
    dup_products_csv.write_text(
        "sku,product_name,family,launch_date,unit_cost_inr,retail_price_inr,warranty_months\n"
        "SKU-1,Prod 1,Fam,2024-01-01,100,200,12\n"
        "SKU-1,Prod 1 Duplicate,Fam,2024-01-01,100,200,12\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate sku found"):
        data_loader.load_products(dup_products_csv)
