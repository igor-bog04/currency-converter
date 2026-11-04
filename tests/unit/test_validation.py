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
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("")
        assert exc_info.value is not None

    def test_letters_raise(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("abc")
        assert exc_info.value is not None

    def test_zero_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("0")
        assert exc_info.value is not None

    def test_negative_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("-10")
        assert exc_info.value is not None

    def test_more_than_two_decimal_places_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("10.555")
        assert exc_info.value is not None

    def test_multiple_decimal_separators_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("10.5.5")
        assert exc_info.value is not None

    def test_space_as_grouping_separator_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1 000")
        assert exc_info.value is not None

    def test_apostrophe_grouping_separator_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1'000")
        assert exc_info.value is not None

    def test_comma_as_thousands_separator_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1,000.50")
        assert exc_info.value is not None

    def test_scientific_notation_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1e5")
        assert exc_info.value is not None

    def test_whitespace_only_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("   ")
        assert exc_info.value is not None

    def test_mixed_comma_dot_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1,000.50")
        assert exc_info.value is not None

    def test_plus_prefix_raises(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("+10")
        assert exc_info.value is not None


class TestValidationSpecificMessages:
    def test_zero_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("0")
        assert str(exc_info.value) == "Сумма должна быть больше нуля"

    def test_negative_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("-15")
        assert str(exc_info.value) == "Сумма должна быть больше нуля"

    def test_letters_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("abc")
        assert str(exc_info.value) == "Введите число"

    def test_more_than_two_decimals_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("12.345")
        assert str(exc_info.value) == "Не более 2 знаков после запятой"

    def test_grouping_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1 000")
        assert str(exc_info.value) == "Используйте только цифры и один разделитель (точку или запятую)"

    def test_scientific_message(self):
        from currency_converter.validation import AmountValidationError
        with pytest.raises(AmountValidationError) as exc_info:
            validate_amount("1e4")
        assert str(exc_info.value) == "Используйте только цифры и один разделитель (точку или запятую)"
