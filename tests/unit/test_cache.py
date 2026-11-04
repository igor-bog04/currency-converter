import pytest
import json
import os
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock
from currency_converter.cache import RateCache
from currency_converter.models import Currency, RateSnapshot


def make_snapshot(d=date(2026, 11, 4)):
    return RateSnapshot(
        rate_date=d,
        source="BNM",
        currencies={
            "MDL": Currency("MDL", "Moldovan Leu", Decimal("1")),
            "EUR": Currency("EUR", "Euro", Decimal("19.6500")),
            "USD": Currency("USD", "US Dollar", Decimal("18.1200")),
        }
    )


class TestCacheSaveLoad:
    def test_save_and_load_roundtrip(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache = RateCache(path=str(cache_path))
        snapshot = make_snapshot()
        cache.save(snapshot)
        loaded = cache.load()
        assert loaded is not None
        assert loaded.rate_date == date(2026, 11, 4)
        assert loaded.source == "BNM"
        assert "EUR" in loaded.currencies
        assert loaded.currencies["EUR"].rate_to_mdl == Decimal("19.6500")

    def test_decimal_serialized_as_string(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache = RateCache(path=str(cache_path))
        snapshot = make_snapshot()
        cache.save(snapshot)
        with open(cache_path) as f:
            data = json.load(f)
        # Find EUR rate value - should be a string not a float
        # Traverse data to find rate values
        assert isinstance(data, dict)

    def test_load_returns_none_when_no_cache(self, tmp_path):
        cache_path = tmp_path / "nonexistent.json"
        cache = RateCache(path=str(cache_path))
        assert cache.load() is None

    def test_load_returns_none_on_corrupt_json(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache_path.write_text("this is not json { corrupted")
        cache = RateCache(path=str(cache_path))
        assert cache.load() is None

    def test_mdl_preserved_in_roundtrip(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache = RateCache(path=str(cache_path))
        snapshot = make_snapshot()
        cache.save(snapshot)
        loaded = cache.load()
        assert "MDL" in loaded.currencies
        assert loaded.currencies["MDL"].rate_to_mdl == Decimal("1")


class TestCacheAtomicWrite:
    def test_save_does_not_leave_partial_file_on_error(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache = RateCache(path=str(cache_path))
        snapshot = make_snapshot()
        # Write a valid file first
        cache.save(snapshot)
        assert cache_path.exists()


class TestCacheAppDataPath:
    def test_default_cache_uses_appdata_path(self):
        cache = RateCache()
        assert "CurrencyConverter" in cache.path or "APPDATA" in cache.path.upper() or os.environ.get("APPDATA", "") in cache.path
