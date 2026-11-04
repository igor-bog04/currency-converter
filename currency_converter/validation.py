"""Amount input validation."""
from decimal import Decimal, InvalidOperation


class AmountValidationError(ValueError):
    """Raised when an entered amount is invalid."""
    pass


def validate_amount(s: str) -> Decimal:
    if not isinstance(s, str):
        raise AmountValidationError("Введите число")

    s_clean = s.strip()
    if not s_clean:
        raise AmountValidationError("Введите число")

    # 1. Check for scientific notation
    if "e" in s_clean.lower():
        raise AmountValidationError("Используйте только цифры и один разделитель (точку или запятую)")

    # 2. Check for grouping separators (spaces, apostrophes)
    if " " in s_clean or "'" in s_clean:
        raise AmountValidationError("Используйте только цифры и один разделитель (точку или запятую)")

    # 3. Check for multiple decimal/grouping separators
    dot_count = s_clean.count(".")
    comma_count = s_clean.count(",")
    if (dot_count + comma_count) > 1:
        raise AmountValidationError("Используйте только цифры и один разделитель (точку или запятую)")

    # 4. Check for letters
    if any(c.isalpha() for c in s_clean):
        raise AmountValidationError("Введите число")

    # 5. Check for signs (+ or -) or other non-digit non-separator characters
    if s_clean.startswith("+"):
        raise AmountValidationError("Используйте только цифры и один разделитель (точку или запятую)")

    # 6. Check for negative numbers
    if s_clean.startswith("-"):
        raise AmountValidationError("Сумма должна быть больше нуля")

    # 7. Check if remaining characters are only digits and at most one separator
    valid_chars = set("0123456789.,")
    if not all(c in valid_chars for c in s_clean):
        raise AmountValidationError("Введите число")

    # 8. Check decimal places
    separator = "." if dot_count == 1 else ("," if comma_count == 1 else None)
    if separator:
        parts = s_clean.split(separator)
        if len(parts[0]) == 0 or len(parts[1]) == 0:
            raise AmountValidationError("Введите число")
        if len(parts[1]) > 2:
            raise AmountValidationError("Не более 2 знаков после запятой")

    normalized = s_clean.replace(",", ".")
    try:
        val = Decimal(normalized)
    except InvalidOperation as e:
        raise AmountValidationError("Введите число") from e

    if not val.is_finite():
        raise AmountValidationError("Введите число")

    # 9. Check zero or negative
    if val <= Decimal("0"):
        raise AmountValidationError("Сумма должна быть больше нуля")

    return val
