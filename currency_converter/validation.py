"""Amount input validation."""
import re
from decimal import Decimal, InvalidOperation


class AmountValidationError(ValueError):
    """Raised when an entered amount is invalid."""
    pass


_AMOUNT_REGEX = re.compile(r"^\d+([.,]\d{1,2})?$")


def validate_amount(s: str) -> Decimal:
    if not isinstance(s, str):
        raise AmountValidationError("Сумма должна быть строкой.")

    s_clean = s.strip()
    if not s_clean:
        raise AmountValidationError("Введите сумму.")

    # Must match regex: only digits, at most one comma or dot, at most 2 fractional digits
    # No signs (+ or -), no spaces, no grouping separators, no scientific notation
    if not _AMOUNT_REGEX.match(s):
        raise AmountValidationError(
            "Некорректный формат суммы. Используйте только цифры и разделитель '.' или ',' (не более 2 знаков после запятой)."
        )

    normalized = s.replace(",", ".")
    try:
        val = Decimal(normalized)
    except InvalidOperation as e:
        raise AmountValidationError("Не удалось преобразовать значение в число.") from e

    if not val.is_finite():
        raise AmountValidationError("Сумма должна быть конечным числом.")

    if val <= Decimal("0"):
        raise AmountValidationError("Сумма должна быть больше нуля.")

    return val
