"""CustomTkinter UI for the currency converter application."""


def can_convert(amount, source, target):
    raise NotImplementedError


def format_fallback_message(requested, effective):
    raise NotImplementedError


def format_error_message(error_type, **kwargs):
    raise NotImplementedError


def format_result(result, source_code, target_code):
    raise NotImplementedError
