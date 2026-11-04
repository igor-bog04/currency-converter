import pytest
from decimal import Decimal
from datetime import date
from currency_converter.converter import convert
from currency_converter.models import Currency, RateSnapshot, ConversionResult


@pytest.fixture
def snapshot():
    return RateSnapshot(
        rate_date=date(2026, 11, 4),
        source="BNM",
        currencies={
            "MDL": Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1")),
            "EUR": Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("19.6500")),
            "USD": Currency(code="USD", name="US Dollar", rate_to_mdl=Decimal("18.1200")),
            "RON": Currency(code="RON", name="Romanian Leu", rate_to_mdl=Decimal("3.9500")),
        }
    )


class TestConvertFromMdl:
    def test_mdl_to_eur(self, snapshot):
        result = convert(Decimal("100"), "MDL", "EUR", snapshot)
        # 100 * 1 / 19.65 = 5.0890...
        assert result.converted_amount == Decimal("5.09")

    def test_mdl_to_usd(self, snapshot):
        result = convert(Decimal("100"), "MDL", "USD", snapshot)
        # 100 * 1 / 18.12 = 5.52...
        assert result.converted_amount == Decimal("5.52")


class TestConvertToMdl:
    def test_eur_to_mdl(self, snapshot):
        result = convert(Decimal("1"), "EUR", "MDL", snapshot)
        # 1 * 19.65 / 1 = 19.65
        assert result.converted_amount == Decimal("19.65")

    def test_usd_to_mdl(self, snapshot):
        result = convert(Decimal("10"), "USD", "MDL", snapshot)
        # 10 * 18.12 / 1 = 181.20
        assert result.converted_amount == Decimal("181.20")


class TestConvertCrossRate:
    def test_eur_to_usd(self, snapshot):
        result = convert(Decimal("1"), "EUR", "USD", snapshot)
        # 1 * 19.65 / 18.12 = 1.0844...
        assert result.converted_amount == Decimal("1.08")

    def test_usd_to_eur(self, snapshot):
        result = convert(Decimal("1"), "USD", "EUR", snapshot)
        # 1 * 18.12 / 19.65 = 0.9221...
        assert result.converted_amount == Decimal("0.92")


class TestSameCurrencyConversion:
    def test_same_currency_returns_original_amount(self, snapshot):
        result = convert(Decimal("100"), "EUR", "EUR", snapshot)
        assert result.converted_amount == Decimal("100.00")

    def test_same_currency_rate_is_one(self, snapshot):
        result = convert(Decimal("100"), "EUR", "EUR", snapshot)
        assert result.source_to_target_rate == Decimal("1.0000")
        assert result.target_to_source_rate == Decimal("1.0000")

    def test_mdl_to_mdl(self, snapshot):
        result = convert(Decimal("50"), "MDL", "MDL", snapshot)
        assert result.converted_amount == Decimal("50.00")


class TestDirectionalRates:
    def test_both_directional_rates_present(self, snapshot):
        result = convert(Decimal("1"), "EUR", "USD", snapshot)
        assert hasattr(result, "source_to_target_rate")
        assert hasattr(result, "target_to_source_rate")

    def test_rates_displayed_to_4_decimal_places(self, snapshot):
        result = convert(Decimal("1"), "EUR", "USD", snapshot)
        # Rate should be quantized to 4 decimal places
        assert result.source_to_target_rate == result.source_to_target_rate.quantize(Decimal("0.0001"))
        assert result.target_to_source_rate == result.target_to_source_rate.quantize(Decimal("0.0001"))

    def test_eur_to_usd_forward_rate(self, snapshot):
        result = convert(Decimal("1"), "EUR", "USD", snapshot)
        # 19.65 / 18.12 = 1.08443... -> 1.0844 (ROUND_HALF_UP to 4 places)
        assert result.source_to_target_rate == Decimal("1.0844")

    def test_eur_to_usd_reverse_rate(self, snapshot):
        result = convert(Decimal("1"), "EUR", "USD", snapshot)
        # 18.12 / 19.65 = 0.9221...
        assert result.target_to_source_rate == Decimal("0.9221")


class TestResultMetadata:
    def test_result_includes_snapshot_date(self, snapshot):
        result = convert(Decimal("1"), "EUR", "MDL", snapshot)
        assert result.snapshot_date == date(2026, 11, 4)

    def test_result_source_is_bnm(self, snapshot):
        result = convert(Decimal("1"), "EUR", "MDL", snapshot)
        assert result.source == "BNM"

    def test_converted_amount_uses_decimal(self, snapshot):
        result = convert(Decimal("1"), "EUR", "MDL", snapshot)
        assert isinstance(result.converted_amount, Decimal)
