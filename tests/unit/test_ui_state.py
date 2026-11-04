import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Test the UI state machine / logic without spinning up a real window
# These test helpers/pure functions that determine UI state
from currency_converter.models import Currency, RateSnapshot, ConversionResult


class TestConvertButtonState:
    """Tests for logic determining when Convert button is enabled."""

    def test_button_disabled_when_amount_empty(self):
        """Convert button must be disabled when amount is empty."""
        from currency_converter.ui import can_convert
        assert can_convert(amount="", source="EUR", target="MDL") is False

    def test_button_disabled_when_source_missing(self):
        from currency_converter.ui import can_convert
        assert can_convert(amount="100", source=None, target="MDL") is False

    def test_button_disabled_when_target_missing(self):
        from currency_converter.ui import can_convert
        assert can_convert(amount="100", source="EUR", target=None) is False

    def test_button_enabled_when_all_fields_filled(self):
        from currency_converter.ui import can_convert
        assert can_convert(amount="100", source="EUR", target="MDL") is True

    def test_button_disabled_with_invalid_amount(self):
        from currency_converter.ui import can_convert
        assert can_convert(amount="abc", source="EUR", target="MDL") is False

    def test_button_disabled_when_amount_zero(self):
        from currency_converter.ui import can_convert
        assert can_convert(amount="0", source="EUR", target="MDL") is False


class TestFallbackMessages:
    """Tests for Russian-language fallback and error messages."""

    def test_fallback_message_includes_effective_date(self):
        from currency_converter.ui import format_fallback_message
        effective = date(2026, 11, 2)
        msg = format_fallback_message(requested=date(2026, 11, 4), effective=effective)
        assert "02.11.2026" in msg or "2026" in msg

    def test_fallback_message_is_non_empty(self):
        from currency_converter.ui import format_fallback_message
        msg = format_fallback_message(requested=date(2026, 11, 4), effective=date(2026, 11, 2))
        assert len(msg) > 0

    def test_error_message_no_network_non_empty(self):
        from currency_converter.ui import format_error_message
        msg = format_error_message("no_network")
        assert len(msg) > 0

    def test_error_message_cache_offered_non_empty(self):
        from currency_converter.ui import format_error_message
        msg = format_error_message("cache_available", cache_date=date(2026, 11, 2))
        assert len(msg) > 0

    def test_error_message_no_cache_non_empty(self):
        from currency_converter.ui import format_error_message
        msg = format_error_message("no_cache")
        assert len(msg) > 0


class TestResultDisplay:
    """Tests for conversion result display formatting."""

    def test_result_shows_converted_amount(self):
        from currency_converter.ui import format_result
        result = ConversionResult(
            converted_amount=Decimal("100.00"),
            source_to_target_rate=Decimal("1.0845"),
            target_to_source_rate=Decimal("0.9221"),
            snapshot_date=date(2026, 11, 4),
            source="BNM"
        )
        text = format_result(result, source_code="EUR", target_code="USD")
        assert "100" in text or "100.00" in text

    def test_result_includes_rate_date(self):
        from currency_converter.ui import format_result
        result = ConversionResult(
            converted_amount=Decimal("100.00"),
            source_to_target_rate=Decimal("1.0845"),
            target_to_source_rate=Decimal("0.9221"),
            snapshot_date=date(2026, 11, 4),
            source="BNM"
        )
        text = format_result(result, source_code="EUR", target_code="USD")
        assert "04.11.2026" in text or "2026" in text

    def test_result_includes_bnm_source(self):
        from currency_converter.ui import format_result
        result = ConversionResult(
            converted_amount=Decimal("100.00"),
            source_to_target_rate=Decimal("1.0845"),
            target_to_source_rate=Decimal("0.9221"),
            snapshot_date=date(2026, 11, 4),
            source="BNM"
        )
        text = format_result(result, source_code="EUR", target_code="USD")
        assert "BNM" in text
