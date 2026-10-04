"""
Data loading and referential integrity validation module for Vireo Audio dataset.
Adheres strictly to the requirement that all agent joins use agent_id, never name.
"""
from typing import Dict, Tuple, Set
import pandas as pd
from pathlib import Path

from src import config


REQUIRED_COLUMNS: Dict[str, Set[str]] = {
    "tickets": {
        "ticket_id",
        "created_at",
        "first_response_at",
        "resolved_at",
        "status",
        "channel",
        "customer_id",
        "order_id",
        "product_sku",
        "category",
        "priority",
        "assigned_team",
        "agent_id",
        "transfers",
        "csat_score",
        "refund_amount_inr",
        "refund_reason_code",
        "replacement_issued",
        "customer_message",
        "agent_notes",
        "source_system",
    },
    "agents": {
        "agent_id",
        "name",
        "site",
        "team",
        "shift",
        "tier",
        "from_date",
        "to_date",
    },
    "customers": {
        "customer_id",
        "name",
        "city",
        "state",
        "signup_date",
        "care_plus",
    },
    "orders": {
        "order_id",
        "customer_id",
        "sku",
        "order_date",
        "channel",
        "qty",
        "order_value_inr",
        "lot_code",
    },
    "products": {
        "sku",
        "product_name",
        "family",
        "launch_date",
        "unit_cost_inr",
        "retail_price_inr",
        "warranty_months",
    },
}


def load_agents(file_path: Path = config.AGENTS_FILE) -> pd.DataFrame:
    """Load and validate agents roster."""
    if not file_path.exists():
        raise FileNotFoundError(f"Agents file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={
            "agent_id": "string",
            "name": "string",
            "site": "string",
            "team": "string",
            "shift": "string",
            "tier": "int64",
            "from_date": "string",
        },
    )

    missing = REQUIRED_COLUMNS["agents"] - set(df.columns)
    if missing:
        raise ValueError(f"agents.csv missing required columns: {missing}")

    if df["agent_id"].duplicated().any():
        dups = df[df["agent_id"].duplicated()]["agent_id"].tolist()
        raise ValueError(f"Duplicate agent_id found in agents.csv: {dups}")

    # Check for shared display names across agent_ids (e.g., Kavya Pandey)
    name_counts = df.groupby("name")["agent_id"].nunique()
    shared_names = name_counts[name_counts > 1].index.tolist()
    if shared_names:
        # Document shared names; ensure that any lookups or joins use agent_id
        pass

    return df


def load_customers(file_path: Path = config.CUSTOMERS_FILE) -> pd.DataFrame:
    """Load and validate customers data."""
    if not file_path.exists():
        raise FileNotFoundError(f"Customers file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={
            "customer_id": "string",
            "name": "string",
            "city": "string",
            "state": "string",
            "signup_date": "string",
            "care_plus": "string",
        },
    )

    missing = REQUIRED_COLUMNS["customers"] - set(df.columns)
    if missing:
        raise ValueError(f"customers.csv missing required columns: {missing}")

    if df["customer_id"].duplicated().any():
        dups = df[df["customer_id"].duplicated()]["customer_id"].tolist()
        raise ValueError(f"Duplicate customer_id found in customers.csv: {dups}")

    return df


def load_products(file_path: Path = config.PRODUCTS_FILE) -> pd.DataFrame:
    """Load and validate products data."""
    if not file_path.exists():
        raise FileNotFoundError(f"Products file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={
            "sku": "string",
            "product_name": "string",
            "family": "string",
            "launch_date": "string",
            "unit_cost_inr": "int64",
            "retail_price_inr": "int64",
            "warranty_months": "int64",
        },
    )

    missing = REQUIRED_COLUMNS["products"] - set(df.columns)
    if missing:
        raise ValueError(f"products.csv missing required columns: {missing}")

    if df["sku"].duplicated().any():
        dups = df[df["sku"].duplicated()]["sku"].tolist()
        raise ValueError(f"Duplicate sku found in products.csv: {dups}")

    return df


def load_orders(file_path: Path = config.ORDERS_FILE) -> pd.DataFrame:
    """Load and validate orders data."""
    if not file_path.exists():
        raise FileNotFoundError(f"Orders file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={
            "order_id": "string",
            "customer_id": "string",
            "sku": "string",
            "order_date": "string",
            "channel": "string",
            "qty": "int64",
            "order_value_inr": "int64",
            "lot_code": "string",
        },
    )

    missing = REQUIRED_COLUMNS["orders"] - set(df.columns)
    if missing:
        raise ValueError(f"orders.csv missing required columns: {missing}")

    if df["order_id"].duplicated().any():
        dups = df[df["order_id"].duplicated()]["order_id"].tolist()
        raise ValueError(f"Duplicate order_id found in orders.csv: {dups}")

    return df


def load_tickets(file_path: Path = config.TICKETS_FILE) -> pd.DataFrame:
    """Load and validate support tickets data."""
    if not file_path.exists():
        raise FileNotFoundError(f"Tickets file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype={
            "ticket_id": "string",
            "created_at": "string",
            "first_response_at": "string",
            "resolved_at": "string",
            "status": "string",
            "channel": "string",
            "customer_id": "string",
            "order_id": "string",
            "product_sku": "string",
            "category": "string",
            "priority": "string",
            "assigned_team": "string",
            "agent_id": "string",
            "transfers": "int64",
            "csat_score": "float64",
            "refund_amount_inr": "float64",
            "refund_reason_code": "string",
            "replacement_issued": "string",
            "customer_message": "string",
            "agent_notes": "string",
            "source_system": "string",
        },
    )

    missing = REQUIRED_COLUMNS["tickets"] - set(df.columns)
    if missing:
        raise ValueError(f"tickets.csv missing required columns: {missing}")

    if df["ticket_id"].duplicated().any():
        dups = df[df["ticket_id"].duplicated()]["ticket_id"].tolist()
        raise ValueError(f"Duplicate ticket_id found in tickets.csv: {dups}")

    return df


def load_all_data(
    data_dir: Path = config.DATA_DIR,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all 5 datasets and execute referential integrity checks.
    Returns: (tickets, agents, customers, orders, products)
    """
    agents = load_agents(data_dir / "agents.csv")
    customers = load_customers(data_dir / "customers.csv")
    products = load_products(data_dir / "products.csv")
    orders = load_orders(data_dir / "orders.csv")
    tickets = load_tickets(data_dir / "tickets.csv")

    # REFERENTIAL INTEGRITY CHECKS
    # 1. Tickets -> Agents: All ticket agent_ids must exist in agents.csv
    valid_agents = set(agents["agent_id"])
    ticket_agents = set(tickets["agent_id"])
    unmatched_agents = ticket_agents - valid_agents
    if unmatched_agents:
        raise ValueError(
            f"Referential integrity failure: {len(unmatched_agents)} unmatched agent_ids in tickets.csv"
        )

    # 2. Tickets -> Customers: All customer_ids in tickets must exist in customers.csv
    valid_customers = set(customers["customer_id"])
    ticket_customers = set(tickets["customer_id"])
    unmatched_customers = ticket_customers - valid_customers
    if unmatched_customers:
        raise ValueError(
            f"Referential integrity failure: {len(unmatched_customers)} unmatched customer_ids in tickets.csv"
        )

    # 3. Tickets -> Products: All product_skus must exist in products.csv
    valid_skus = set(products["sku"])
    ticket_skus = set(tickets["product_sku"])
    unmatched_skus = ticket_skus - valid_skus
    if unmatched_skus:
        raise ValueError(
            f"Referential integrity failure: {len(unmatched_skus)} unmatched product_skus in tickets.csv"
        )

    # 4. Tickets -> Orders: Quoted order_ids must exist in orders.csv
    quoted_orders = tickets[tickets["order_id"].notna()]["order_id"]
    valid_orders = set(orders["order_id"])
    unmatched_orders = set(quoted_orders) - valid_orders
    if unmatched_orders:
        raise ValueError(
            f"Referential integrity failure: {len(unmatched_orders)} unmatched order_ids in tickets.csv"
        )

    return tickets, agents, customers, orders, products
