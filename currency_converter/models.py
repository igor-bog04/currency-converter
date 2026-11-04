"""Data models: Currency, RateSnapshot, ConversionResult."""
from decimal import Decimal
from datetime import date
from typing import Mapping


class Currency:
    def __init__(self, code: str, name: str, rate_to_mdl: Decimal):
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Currency code must be a non-empty string.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Currency name must be a non-empty string.")
        if not isinstance(rate_to_mdl, Decimal):
            raise ValueError("Rate to MDL must be a Decimal.")
        if not rate_to_mdl.is_finite() or rate_to_mdl <= Decimal("0"):
            raise ValueError("Rate to MDL must be a positive finite Decimal.")
        if code.strip() == "MDL" and rate_to_mdl != Decimal("1"):
            raise ValueError("MDL rate must be exactly 1.")

        self.code = code.strip()
        self.name = name.strip()
        self.rate_to_mdl = rate_to_mdl

    def __repr__(self) -> str:
        return f"Currency(code={self.code!r}, name={self.name!r}, rate_to_mdl={self.rate_to_mdl})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Currency):
            return False
        return (
            self.code == other.code
            and self.name == other.name
            and self.rate_to_mdl == other.rate_to_mdl
        )


class RateSnapshot:
    def __init__(self, rate_date: date, source: str, currencies: Mapping[str, Currency]):
        if not isinstance(rate_date, date):
            raise ValueError("rate_date must be a valid date.")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a non-empty string.")
        if not isinstance(currencies, Mapping):
            raise ValueError("currencies must be a mapping of code to Currency.")

        if "MDL" not in currencies:
            raise ValueError("Snapshot must contain MDL currency.")

        non_mdl = [code for code in currencies.keys() if code != "MDL"]
        if not non_mdl:
            raise ValueError("Snapshot must contain at least one non-MDL currency.")

        for code, curr in currencies.items():
            if not isinstance(curr, Currency):
                raise ValueError(f"Value for {code} must be a Currency instance.")
            if curr.code != code:
                raise ValueError(f"Currency code mismatch: key={code}, curr.code={curr.code}")

        self.rate_date = rate_date
        self.source = source.strip()
        self.currencies = dict(currencies)

    def __repr__(self) -> str:
        return f"RateSnapshot(rate_date={self.rate_date}, source={self.source!r}, currencies={list(self.currencies.keys())})"


class ConversionResult:
    def __init__(
        self,
        converted_amount: Decimal,
        source_to_target_rate: Decimal,
        target_to_source_rate: Decimal,
        snapshot_date: date,
        source: str,
    ):
        if not isinstance(converted_amount, Decimal):
            raise ValueError("converted_amount must be a Decimal.")
        if not isinstance(source_to_target_rate, Decimal):
            raise ValueError("source_to_target_rate must be a Decimal.")
        if not isinstance(target_to_source_rate, Decimal):
            raise ValueError("target_to_source_rate must be a Decimal.")
        if not isinstance(snapshot_date, date):
            raise ValueError("snapshot_date must be a date.")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a non-empty string.")

        self.converted_amount = converted_amount
        self.source_to_target_rate = source_to_target_rate
        self.target_to_source_rate = target_to_source_rate
        self.snapshot_date = snapshot_date
        self.source = source.strip()

    def __repr__(self) -> str:
        return (
            f"ConversionResult(converted_amount={self.converted_amount}, "
            f"source_to_target_rate={self.source_to_target_rate}, "
            f"target_to_source_rate={self.target_to_source_rate}, "
            f"snapshot_date={self.snapshot_date}, source={self.source!r})"
        )
