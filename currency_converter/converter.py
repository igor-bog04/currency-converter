"""Pure Decimal currency conversion logic."""
from decimal import Decimal, ROUND_HALF_UP
from currency_converter.models import RateSnapshot, ConversionResult


def convert(amount: Decimal, source_code: str, target_code: str, snapshot: RateSnapshot) -> ConversionResult:
    if source_code not in snapshot.currencies:
        raise ValueError(f"Source currency '{source_code}' not found in snapshot.")
    if target_code not in snapshot.currencies:
        raise ValueError(f"Target currency '{target_code}' not found in snapshot.")

    cents = Decimal("0.01")
    four_decimals = Decimal("0.0001")

    if source_code == target_code:
        converted_amount = amount.quantize(cents, rounding=ROUND_HALF_UP)
        forward_rate = Decimal("1.0000")
        reverse_rate = Decimal("1.0000")
    else:
        rate_source_to_mdl = snapshot.currencies[source_code].rate_to_mdl
        rate_target_to_mdl = snapshot.currencies[target_code].rate_to_mdl

        raw_converted = (amount * rate_source_to_mdl) / rate_target_to_mdl
        converted_amount = raw_converted.quantize(cents, rounding=ROUND_HALF_UP)

        raw_forward = rate_source_to_mdl / rate_target_to_mdl
        forward_rate = raw_forward.quantize(four_decimals, rounding=ROUND_HALF_UP)

        raw_reverse = rate_target_to_mdl / rate_source_to_mdl
        reverse_rate = raw_reverse.quantize(four_decimals, rounding=ROUND_HALF_UP)

    return ConversionResult(
        converted_amount=converted_amount,
        source_to_target_rate=forward_rate,
        target_to_source_rate=reverse_rate,
        snapshot_date=snapshot.rate_date,
        source=snapshot.source,
    )
