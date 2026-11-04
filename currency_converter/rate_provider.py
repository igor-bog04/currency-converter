"""Rate provider: orchestrates BNM client, date fallback, and cache."""
from datetime import date, timedelta
from typing import Optional

from currency_converter.interfaces import NoRatesForDateError, SourceUnavailableError
from currency_converter.models import RateSnapshot


class RateProvider:
    def __init__(self, client, cache):
        self.client = client
        self.cache = cache

    def get_rates(self, rate_date: date) -> RateSnapshot:
        current_date = rate_date
        max_lookback_days = 10
        last_error = None

        for attempt in range(max_lookback_days + 1):
            try:
                snapshot = self.client.fetch_rates(current_date)
                if self.cache is not None:
                    try:
                        self.cache.save(snapshot)
                    except Exception:
                        pass
                return snapshot
            except NoRatesForDateError as e:
                last_error = e
                current_date = current_date - timedelta(days=1)
            except SourceUnavailableError:
                # Network/server/XML errors must NOT trigger date fallback
                raise

        if last_error:
            raise last_error
        raise NoRatesForDateError(f"No rates found within {max_lookback_days} days of {rate_date}")

    def get_cached_rates(self) -> Optional[RateSnapshot]:
        if self.cache is None:
            return None
        try:
            return self.cache.load()
        except Exception:
            return None
