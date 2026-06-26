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
