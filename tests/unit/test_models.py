import pytest
from decimal import Decimal
from datetime import date
from currency_converter.models import Currency, RateSnapshot, ConversionResult


class TestCurrency:
    def test_currency_has_code_name_rate(self):
        c = Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("19.65"))
        assert c.code == "EUR"
        assert c.name == "Euro"
        assert c.rate_to_mdl == Decimal("19.65")

    def test_mdl_currency_rate_is_one(self):
        c = Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1"))
        assert c.rate_to_mdl == Decimal("1")

    def test_currency_rate_must_be_decimal(self):
        c = Currency(code="USD", name="US Dollar", rate_to_mdl=Decimal("18.12"))
        assert isinstance(c.rate_to_mdl, Decimal)

    def test_currency_code_non_empty(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            Currency(code="", name="Euro", rate_to_mdl=Decimal("19.65"))

    def test_currency_name_non_empty(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            Currency(code="EUR", name="", rate_to_mdl=Decimal("19.65"))

    def test_currency_rate_positive(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("-1"))

    def test_currency_rate_not_zero(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("0"))


class TestRateSnapshot:
    def test_rate_snapshot_has_date_source_currencies(self):
        mdl = Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1"))
        eur = Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("19.65"))
        snap = RateSnapshot(
            rate_date=date(2026, 11, 4),
            source="BNM",
            currencies={"MDL": mdl, "EUR": eur}
        )
        assert snap.rate_date == date(2026, 11, 4)
        assert snap.source == "BNM"
        assert "MDL" in snap.currencies
        assert "EUR" in snap.currencies

    def test_rate_snapshot_source_is_bnm(self):
        mdl = Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1"))
        eur = Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("19.65"))
        snap = RateSnapshot(
            rate_date=date(2026, 11, 4),
            source="BNM",
            currencies={"MDL": mdl, "EUR": eur}
        )
        assert snap.source == "BNM"

    def test_rate_snapshot_requires_mdl(self):
        eur = Currency(code="EUR", name="Euro", rate_to_mdl=Decimal("19.65"))
        with pytest.raises((ValueError, TypeError, Exception)):
            RateSnapshot(
                rate_date=date(2026, 11, 4),
                source="BNM",
                currencies={"EUR": eur}
            )

    def test_rate_snapshot_requires_non_mdl_currency(self):
        mdl = Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1"))
        with pytest.raises((ValueError, TypeError, Exception)):
            RateSnapshot(
                rate_date=date(2026, 11, 4),
                source="BNM",
                currencies={"MDL": mdl}
            )


class TestConversionResult:
    def test_conversion_result_has_required_fields(self):
        result = ConversionResult(
            converted_amount=Decimal("100.00"),
            source_to_target_rate=Decimal("1.0845"),
            target_to_source_rate=Decimal("0.9220"),
            snapshot_date=date(2026, 11, 4),
            source="BNM"
        )
        assert result.converted_amount == Decimal("100.00")
        assert result.source_to_target_rate == Decimal("1.0845")
        assert result.target_to_source_rate == Decimal("0.9220")
        assert result.snapshot_date == date(2026, 11, 4)
        assert result.source == "BNM"
