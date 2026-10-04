"""
Configuration constants, paths, and policy parameters for Vireo Audio Support Analytics.
Reference: reference/support-policy.pdf (Version 3.2, Effective 1 April 2025)
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REFERENCE_DIR = BASE_DIR / "reference"
OUTPUTS_DIR = BASE_DIR / "outputs"

# CSV Data Files
TICKETS_FILE = DATA_DIR / "tickets.csv"
AGENTS_FILE = DATA_DIR / "agents.csv"
CUSTOMERS_FILE = DATA_DIR / "customers.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"

# Output Files
AGENT_METRICS_FILE = OUTPUTS_DIR / "agent_metrics.csv"
PEER_METRICS_FILE = OUTPUTS_DIR / "peer_metrics.csv"
RAW_BOTTOM10_FILE = OUTPUTS_DIR / "raw_bottom10.csv"
TRAINING_CANDIDATES_FILE = OUTPUTS_DIR / "training_candidates.csv"
POLICY_EXCEPTIONS_FILE = OUTPUTS_DIR / "policy_exceptions.csv"
VALIDATION_REPORT_FILE = OUTPUTS_DIR / "validation_report.md"

# First-Response SLA Targets in Minutes (Policy §3)
# chat: 15 minutes, voice callback: 2 hours (120m), social: 4 hours (240m), email: 8 hours (480m)
SLA_TARGETS_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

# SLA Breach Credit in INR (Policy §3)
SLA_BREACH_PENALTY_INR = 350

# Cost Standards in INR (Policy §4)
CONTACT_COST_INR = {
    "chat": 210,
    "email": 260,
    "voice": 520,
    "social": 240,
    "blended": 290,
}
INTERNAL_TRANSFER_COST_INR = 305
AGENT_HOURLY_COST_INR = 165
AGENT_SHIFT_HOURS = 8

# Replacement Logistics Surcharge in INR (Policy §5)
REPLACEMENT_LOGISTICS_SURCHARGE_INR = 340

# Goodwill Credit Cap in INR (Policy §5)
GOODWILL_CREDIT_CAP_INR = 500

# Legacy Helpdesk Migration Parameters (Policy §9)
LEGACY_MIGRATION_DATE = "2025-09-14"
LEGACY_SOURCE_SYSTEM = "legacy_fd"
MODERN_SOURCE_SYSTEM = "helpdesk"
# Reconstructed legacy resolution timestamps were stored in UTC; IST is UTC + 5:30 (+330 minutes)
LEGACY_UTC_OFFSET_MINUTES = 330
LEGACY_UTC_OFFSET_HOURS = 5.5

# Peer Group Mapping from Team and Tier
# Methodology Section A.2:
# 1. Chat Frontline (Tier 1)
# 2. Email Frontline (Tier 1)
# 3. Voice Frontline (Tier 1)
# 4. Logistics (Tier 1)
# 5. Returns & Billing (Tier 1: Returns Desk + Billing)
# 6. Escalations & Warranty (Tier 2)
PEER_GROUP_MAPPING = {
    "Chat Frontline": "Chat Frontline",
    "Email Frontline": "Email Frontline",
    "Voice Frontline": "Voice Frontline",
    "Logistics": "Logistics",
    "Returns Desk": "Returns & Billing",
    "Billing": "Returns & Billing",
    "Escalations & Warranty": "Escalations & Warranty",
}

# Empirical Bayes Shrinkage Constant (Methodology Section C.2)
EMPIRICAL_BAYES_M = 25

# Dataset Scope Constants (1 Jan 2025 – 30 Jun 2026 = 18 months = 1.5 years)
DATASET_MONTHS = 18.0
ANNUALIZATION_FACTOR = 12.0 / DATASET_MONTHS  # 1.0 / 1.5 = 0.6666667
