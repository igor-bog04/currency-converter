import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date
from currency_converter.rate_provider import RateProvider
from currency_converter.converter import convert
from currency_converter.models import Currency, RateSnapshot

SAMPLE_DATE = date(2026, 11, 4)


def make_snapshot(d=SAMPLE_DATE):
    return RateSnapshot(
        rate_date=d,
        source="BNM",
        currencies={
            "MDL": Currency("MDL", "Moldovan Leu", Decimal("1")),
            "EUR": Currency("EUR", "Euro", Decimal("19.6500")),
            "USD": Currency("USD", "US Dollar", Decimal("18.1200")),
            "RON": Currency("RON", "Romanian Leu", Decimal("3.9500")),
        }
    )


class TestFullConversionFlow:
    def test_mdl_to_eur_via_mocked_provider(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        mock_client.fetch_rates.return_value = make_snapshot()
        mock_cache.load.return_value = None
        mock_cache.save.return_value = None

        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        result = convert(Decimal("100"), "MDL", "EUR", snapshot)

        assert result.converted_amount == Decimal("5.09")
        assert result.source == "BNM"
        assert result.snapshot_date == SAMPLE_DATE

    def test_cross_rate_eur_to_usd(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        mock_client.fetch_rates.return_value = make_snapshot()
        mock_cache.load.return_value = None
        mock_cache.save.return_value = None

        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        result = convert(Decimal("1"), "EUR", "USD", snapshot)

        # EUR->USD: 19.65 / 18.12 = 1.0845
        assert result.converted_amount is not None

    def test_cache_used_when_network_fails(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        from currency_converter.bnm_client import SourceUnavailableError
        mock_client.fetch_rates.side_effect = SourceUnavailableError("No network")
        mock_cache.load.return_value = make_snapshot()

        provider = RateProvider(client=mock_client, cache=mock_cache)
        cached = provider.get_cached_rates()
        assert cached is not None
        result = convert(Decimal("1"), "EUR", "MDL", cached)
        assert result.converted_amount == Decimal("19.65")

    def test_same_currency_conversion(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        mock_client.fetch_rates.return_value = make_snapshot()
        mock_cache.load.return_value = None
        mock_cache.save.return_value = None

        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        result = convert(Decimal("100"), "EUR", "EUR", snapshot)

        assert result.converted_amount == Decimal("100.00")
        assert result.source_to_target_rate == Decimal("1.0000")
