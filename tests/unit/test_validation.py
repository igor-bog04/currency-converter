import pytest
from decimal import Decimal
from currency_converter.validation import validate_amount


class TestValidAmounts:
    def test_integer_amount(self):
        result = validate_amount("100")
        assert result == Decimal("100")

    def test_one_decimal_place_dot(self):
        result = validate_amount("10.5")
        assert result == Decimal("10.5")

    def test_two_decimal_places_dot(self):
        result = validate_amount("10.55")
        assert result == Decimal("10.55")

    def test_comma_as_decimal_separator(self):
        result = validate_amount("10,55")
        assert result == Decimal("10.55")

    def test_one_decimal_comma(self):
        result = validate_amount("10,5")
        assert result == Decimal("10.5")

    def test_large_amount(self):
        result = validate_amount("999999.99")
        assert result == Decimal("999999.99")


class TestInvalidAmounts:
    def test_empty_string_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("")

    def test_letters_raise(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("abc")

    def test_zero_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("0")

    def test_negative_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("-10")

    def test_more_than_two_decimal_places_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("10.555")

    def test_multiple_decimal_separators_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("10.5.5")

    def test_space_as_grouping_separator_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("1 000")

    def test_apostrophe_grouping_separator_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("1'000")

    def test_comma_as_thousands_separator_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("1,000.50")

    def test_scientific_notation_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("1e5")

    def test_whitespace_only_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("   ")

    def test_mixed_comma_dot_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("1,000.50")

    def test_plus_prefix_raises(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            validate_amount("+10")
