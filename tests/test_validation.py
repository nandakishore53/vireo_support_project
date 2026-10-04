"""
Integration tests for src/validation.py.
Verifies that the entire validation suite runs and asserts 100% parity against known ground truth.
"""
import pytest
from src import config, validation


def test_full_validation_suite_passes():
    """Verify that all validation checks pass with zero discrepancies."""
    res = validation.run_validation()

    assert bool(res["all_passed"]) is True, "Validation suite failed one or more checks"
    for check in res["checks"]:
        assert bool(check["passed"]) is True, f"Check failed: {check['check']} -> {check['actual']}"


def test_validation_report_created():
    """Verify that outputs/validation_report.md exists and is populated."""
    assert config.VALIDATION_REPORT_FILE.exists(), "validation_report.md was not created"
    content = config.VALIDATION_REPORT_FILE.read_text(encoding="utf-8")

    assert "PASSED (100% Metric Parity)" in content
    assert "1,064 breaches" in content
    assert "131" in content
    assert "Rs 590,934.00" in content
    assert "2,309" in content
