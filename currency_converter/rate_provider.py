"""Rate provider: orchestrates BNM client, date fallback, and cache."""


class RateProvider:
    def __init__(self, client, cache):
        raise NotImplementedError

    def get_rates(self, rate_date):
        raise NotImplementedError

    def get_cached_rates(self):
        raise NotImplementedError
