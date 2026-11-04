"""Interfaces / protocols for the currency converter package."""
from typing import Protocol, Optional
from datetime import date
from currency_converter.models import RateSnapshot


class SourceUnavailableError(Exception):
    """Raised when the rate source cannot be reached or returns malformed data."""
    pass


class NoRatesForDateError(Exception):
    """Raised when the rate source reports no rates for the requested date (404 or empty rates)."""
    pass


class RateSourceProtocol(Protocol):
    def fetch_rates(self, rate_date: date) -> RateSnapshot:
        ...


class CacheProtocol(Protocol):
    def save(self, snapshot: RateSnapshot) -> None:
        ...

    def load(self) -> Optional[RateSnapshot]:
        ...


class RateProviderProtocol(Protocol):
    def get_rates(self, rate_date: date) -> RateSnapshot:
        ...

    def get_cached_rates(self) -> Optional[RateSnapshot]:
        ...
