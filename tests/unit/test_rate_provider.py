import pytest
from unittest.mock import MagicMock, patch, call
from decimal import Decimal
from datetime import date, timedelta
from currency_converter.rate_provider import RateProvider
from currency_converter.models import Currency, RateSnapshot

SAMPLE_DATE = date(2026, 11, 4)


def make_snapshot(d=SAMPLE_DATE):
    return RateSnapshot(
        rate_date=d,
        source="BNM",
        currencies={
            "MDL": Currency("MDL", "Moldovan Leu", Decimal("1")),
            "EUR": Currency("EUR", "Euro", Decimal("19.65")),
        }
    )


class TestRateProviderSuccess:
    def test_returns_snapshot_on_first_try(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        mock_client.fetch_rates.return_value = make_snapshot()
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        assert snapshot is not None
        assert snapshot.rate_date == SAMPLE_DATE

    def test_saves_snapshot_to_cache_on_success(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        mock_client.fetch_rates.return_value = make_snapshot()
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        provider.get_rates(SAMPLE_DATE)
        mock_cache.save.assert_called_once()


class TestRateProviderDateFallback:
    def test_falls_back_when_first_date_has_no_rates(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        prior_date = SAMPLE_DATE - timedelta(days=1)
        # First call raises NoRatesError (date-specific), second returns snapshot
        from currency_converter.bnm_client import NoRatesError
        mock_client.fetch_rates.side_effect = [
            NoRatesError("No rates for date"),
            make_snapshot(prior_date)
        ]
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        assert snapshot.rate_date == prior_date

    def test_fallback_stops_at_10_prior_dates(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        from currency_converter.bnm_client import NoRatesError
        mock_client.fetch_rates.side_effect = NoRatesError("No rates")
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        with pytest.raises(Exception):
            provider.get_rates(SAMPLE_DATE)
        # Should have tried at most 11 dates (selected + 10 prior)
        assert mock_client.fetch_rates.call_count <= 11

    def test_404_triggers_date_fallback(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        from currency_converter.bnm_client import NoRatesError
        prior_date = SAMPLE_DATE - timedelta(days=1)
        mock_client.fetch_rates.side_effect = [
            NoRatesError("HTTP 404"),
            make_snapshot(prior_date)
        ]
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        snapshot = provider.get_rates(SAMPLE_DATE)
        assert snapshot is not None


class TestRateProviderNetworkFailure:
    def test_network_error_triggers_cache_fallback(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        from currency_converter.bnm_client import SourceUnavailableError
        mock_client.fetch_rates.side_effect = SourceUnavailableError("No network")
        mock_cache.load.return_value = make_snapshot()
        provider = RateProvider(client=mock_client, cache=mock_cache)
        cached = provider.get_cached_rates()
        assert cached is not None

    def test_transport_error_does_not_trigger_date_fallback(self):
        mock_client = MagicMock()
        mock_cache = MagicMock()
        from currency_converter.bnm_client import SourceUnavailableError
        mock_client.fetch_rates.side_effect = SourceUnavailableError("Timeout")
        mock_cache.load.return_value = None
        provider = RateProvider(client=mock_client, cache=mock_cache)
        with pytest.raises(Exception):
            provider.get_rates(SAMPLE_DATE)
        # Should NOT have retried with prior dates
        assert mock_client.fetch_rates.call_count == 1
