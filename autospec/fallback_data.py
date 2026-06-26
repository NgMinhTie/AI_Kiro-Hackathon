"""Deterministic fallback data for the tip-calculator demo.

Contains curated, known-good outputs for each agent stage
so the demo runs fully offline without any LLM/Bedrock dependency.
"""
from __future__ import annotations

from autospec.models import (
    AcceptanceCriterion, AlignmentVerdict, Gap, GeneratedCode,
    Requirement, SpecDocument, TestReport, TestResult, TestSuite,
)

# ─── SPEC AGENT OUTPUT ───────────────────────────────────────────────────────

DEMO_SPEC = SpecDocument(
    requirements=(
        Requirement(
            number=1,
            title="Calculate tip amount",
            criteria=(
                AcceptanceCriterion(
                    id="1.1",
                    given="A bill total and a tip percentage",
                    when="The tip calculator is invoked",
                    then="It returns the tip amount = bill_total * tip_percentage / 100, rounded to 2 decimal places",
                ),
            ),
        ),
        Requirement(
            number=2,
            title="Calculate total with tip",
            criteria=(
                AcceptanceCriterion(
                    id="2.1",
                    given="A bill total and a tip percentage",
                    when="The tip calculator is invoked",
                    then="It returns total_with_tip = bill_total + tip_amount, rounded to 2 decimal places",
                ),
            ),
        ),
        Requirement(
            number=3,
            title="Calculate per-person amount",
            criteria=(
                AcceptanceCriterion(
                    id="3.1",
                    given="A total with tip and a number of people >= 1",
                    when="The tip calculator is invoked",
                    then="It returns per_person = total_with_tip / number_of_people, rounded to 2 decimal places",
                ),
            ),
        ),
        Requirement(
            number=4,
            title="Handle zero tip",
            criteria=(
                AcceptanceCriterion(
                    id="4.1",
                    given="A bill total and a tip percentage of 0",
                    when="The tip calculator is invoked",
                    then="It returns tip_amount = 0.00 and total_with_tip = bill_total",
                ),
            ),
        ),
        Requirement(
            number=5,
            title="Reject invalid number of people",
            criteria=(
                AcceptanceCriterion(
                    id="5.1",
                    given="A number of people less than 1 or not an integer",
                    when="The tip calculator is invoked",
                    then="It raises a ValueError with a message indicating people must be >= 1",
                ),
            ),
        ),
        Requirement(
            number=6,
            title="Reject negative bill or tip",
            criteria=(
                AcceptanceCriterion(
                    id="6.1",
                    given="A bill total < 0 or a tip percentage < 0",
                    when="The tip calculator is invoked",
                    then="It raises a ValueError with a message indicating the value is out of range",
                ),
            ),
        ),
    ),
    edge_cases=(
        "Bill total of 0.00 with any valid tip percentage",
        "Tip percentage of exactly 100 (doubling the bill)",
        "Very large bill (999,999,999.99) to test overflow",
        "Single person (no splitting needed)",
        "Fractional per-person amounts that require rounding",
        "Tip percentage of 0 with multiple people",
    ),
)

# ─── BUILD AGENT OUTPUT ──────────────────────────────────────────────────────

DEMO_CODE_SOURCE = '''\
"""Tip Calculator Module.

A pure-function implementation that computes tip amounts,
totals with tip, and per-person split amounts.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_tip(bill_total: float, tip_percentage: float, num_people: int) -> dict:
    """Calculate tip, total with tip, and per-person amount.

    Args:
        bill_total: The total bill amount (must be >= 0).
        tip_percentage: The tip percentage (must be >= 0, e.g. 15 for 15%).
        num_people: Number of people splitting the bill (must be integer >= 1).

    Returns:
        A dictionary with keys: tip_amount, total_with_tip, per_person_amount.

    Raises:
        ValueError: If inputs are out of valid range.
    """
    # Validate inputs
    if not isinstance(num_people, int) or num_people < 1:
        raise ValueError("Number of people must be an integer greater than or equal to 1.")
    if bill_total < 0:
        raise ValueError("Bill total must be greater than or equal to 0.00.")
    if tip_percentage < 0:
        raise ValueError("Tip percentage must be greater than or equal to 0.")

    # Use Decimal for precise money arithmetic
    bill = Decimal(str(bill_total))
    pct = Decimal(str(tip_percentage))
    people = Decimal(str(num_people))

    # Calculate
    tip_amount = (bill * pct / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_with_tip = (bill + tip_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    per_person = (total_with_tip / people).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "tip_amount": float(tip_amount),
        "total_with_tip": float(total_with_tip),
        "per_person_amount": float(per_person),
    }
'''

DEMO_CODE = GeneratedCode(module_name="tip_calculator", source=DEMO_CODE_SOURCE)

# ─── TEST AGENT OUTPUT ────────────────────────────────────────────────────────

DEMO_TEST_SOURCE = '''\
"""Tests for the Tip Calculator — one test per acceptance criterion."""
import pytest
from tip_calculator import calculate_tip


class TestCalculateTip:
    """Test suite for calculate_tip function."""

    def test_1_1_tip_amount_calculated(self):
        """Criterion 1.1: tip = bill * pct / 100, rounded to 2dp."""
        result = calculate_tip(100.00, 15, 2)
        assert result["tip_amount"] == 15.00

    def test_2_1_total_with_tip(self):
        """Criterion 2.1: total = bill + tip, rounded to 2dp."""
        result = calculate_tip(100.00, 15, 2)
        assert result["total_with_tip"] == 115.00

    def test_3_1_per_person_amount(self):
        """Criterion 3.1: per_person = total / people, rounded to 2dp."""
        result = calculate_tip(100.00, 15, 2)
        assert result["per_person_amount"] == 57.50

    def test_4_1_zero_tip(self):
        """Criterion 4.1: 0% tip returns tip=0 and total=bill."""
        result = calculate_tip(50.00, 0, 1)
        assert result["tip_amount"] == 0.00
        assert result["total_with_tip"] == 50.00

    def test_5_1_reject_invalid_people(self):
        """Criterion 5.1: people < 1 raises ValueError."""
        with pytest.raises(ValueError, match="integer greater than or equal to 1"):
            calculate_tip(100.00, 15, 0)

    def test_5_1_reject_non_integer_people(self):
        """Criterion 5.1: non-integer people raises ValueError."""
        with pytest.raises(ValueError, match="integer greater than or equal to 1"):
            calculate_tip(100.00, 15, 1.5)

    def test_6_1_reject_negative_bill(self):
        """Criterion 6.1: negative bill raises ValueError."""
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            calculate_tip(-10.00, 15, 1)

    def test_6_1_reject_negative_tip_pct(self):
        """Criterion 6.1: negative tip pct raises ValueError."""
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            calculate_tip(100.00, -5, 1)
'''

DEMO_TEST_SUITE = TestSuite(
    source=DEMO_TEST_SOURCE,
    criterion_ids=("1.1", "2.1", "3.1", "4.1", "5.1", "5.1", "6.1", "6.1"),
)

DEMO_TEST_REPORT = TestReport(
    results=(
        TestResult(criterion_id="1.1", name="test_1_1_tip_amount_calculated", status="passed", detail=""),
        TestResult(criterion_id="2.1", name="test_2_1_total_with_tip", status="passed", detail=""),
        TestResult(criterion_id="3.1", name="test_3_1_per_person_amount", status="passed", detail=""),
        TestResult(criterion_id="4.1", name="test_4_1_zero_tip", status="passed", detail=""),
        TestResult(criterion_id="5.1", name="test_5_1_reject_invalid_people", status="passed", detail=""),
        TestResult(criterion_id="5.1", name="test_5_1_reject_non_integer_people", status="passed", detail=""),
        TestResult(criterion_id="6.1", name="test_6_1_reject_negative_bill", status="passed", detail=""),
        TestResult(criterion_id="6.1", name="test_6_1_reject_negative_tip_pct", status="passed", detail=""),
    ),
    passed=8,
    failed=0,
    coverage_percentage=96.0,
    quality_gate_status="met",
)

# ─── REVIEW AGENT OUTPUT ─────────────────────────────────────────────────────

DEMO_VERDICT = AlignmentVerdict(verdict="ALIGNED", gaps=())
