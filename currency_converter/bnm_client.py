"""BNM (National Bank of Moldova) HTTP client."""


class NoRatesError(Exception):
    """Raised when a date has no available rates (404 or empty response)."""
    pass


class SourceUnavailableError(Exception):
    """Raised on transport or server errors (network down, 5xx)."""
    pass


class BnmClient:
    def fetch_rates(self, rate_date):
        raise NotImplementedError
