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
