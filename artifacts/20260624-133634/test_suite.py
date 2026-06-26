"""Generated pytest suite for the tip calculator.

One test per acceptance criterion; each test name encodes the criterion id it
verifies (test_crit_<req>_<crit>_...).
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from generated_code import calculate_tip


def test_crit_1_1_returns_rounded_amounts():
    """Criterion 1.1: valid inputs return tip/total/per-person rounded to 2dp."""
    result = calculate_tip(100.00, 15, 2)
    assert result["tip_amount"] == Decimal("15.00")
    assert result["total_with_tip"] == Decimal("115.00")
    assert result["per_person_amount"] == Decimal("57.50")


def test_crit_1_2_tip_and_total_formula():
    """Criterion 1.2: tip = bill*pct/100 and total = bill + tip."""
    result = calculate_tip(80.00, 25, 1)
    assert result["tip_amount"] == Decimal("20.00")
    assert result["total_with_tip"] == Decimal("100.00")


def test_crit_1_3_per_person_division():
    """Criterion 1.3: per-person = total / people."""
    result = calculate_tip(90.00, 10, 3)
    assert result["per_person_amount"] == Decimal("33.00")


def test_crit_2_1_zero_tip():
    """Criterion 2.1: zero tip yields tip 0.00 and total equal to the bill."""
    result = calculate_tip(50.00, 0, 4)
    assert result["tip_amount"] == Decimal("0.00")
    assert result["total_with_tip"] == Decimal("50.00")


def test_crit_3_1_invalid_people_rejected():
    """Criterion 3.1: number of people < 1 or non-integer is rejected."""
    with pytest.raises(ValueError):
        calculate_tip(50.00, 10, 0)
    with pytest.raises(ValueError):
        calculate_tip(50.00, 10, 2.5)


def test_crit_4_1_invalid_bill_or_pct_rejected():
    """Criterion 4.1: negative bill total or tip percentage is rejected."""
    with pytest.raises(ValueError):
        calculate_tip(-1.00, 10, 2)
    with pytest.raises(ValueError):
        calculate_tip(50.00, -5, 2)
