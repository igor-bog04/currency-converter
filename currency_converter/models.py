"""Data models: Currency, RateSnapshot, ConversionResult."""


class Currency:
    def __init__(self, code, name, rate_to_mdl):
        raise NotImplementedError


class RateSnapshot:
    def __init__(self, rate_date, source, currencies):
        raise NotImplementedError


class ConversionResult:
    def __init__(self, converted_amount, source_to_target_rate, target_to_source_rate, snapshot_date, source):
        raise NotImplementedError
