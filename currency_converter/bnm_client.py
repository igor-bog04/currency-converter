"""BNM (National Bank of Moldova) HTTP client."""
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Dict
import requests

from currency_converter.interfaces import SourceUnavailableError, NoRatesForDateError
from currency_converter.models import Currency, RateSnapshot


class BnmClient:
    BASE_URL = "https://www.bnm.md/en/official_exchange_rates"

    def fetch_rates(self, rate_date: date) -> RateSnapshot:
        date_str = rate_date.strftime("%d.%m.%Y")
        url = f"{self.BASE_URL}?get_xml=1&date={date_str}"

        try:
            response = requests.get(url, timeout=10)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise SourceUnavailableError(f"Network error while fetching rates: {e}") from e
        except requests.RequestException as e:
            raise SourceUnavailableError(f"Request failed: {e}") from e

        if response.status_code == 404:
            raise NoRatesForDateError(f"HTTP 404: No rates published for date {date_str}")
        if response.status_code != 200:
            raise SourceUnavailableError(f"Server returned HTTP status {response.status_code}")

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            raise SourceUnavailableError(f"Malformed XML response: {e}") from e

        if root.tag != "ValCurs":
            raise SourceUnavailableError(f"Unexpected root tag '{root.tag}' in XML")

        valutes = root.findall("Valute")
        if not valutes:
            raise NoRatesForDateError(f"Empty XML rates document for date {date_str}")

        currencies: Dict[str, Currency] = {}
        seen_codes = set()

        for valute in valutes:
            char_code_elem = valute.find("CharCode")
            nominal_elem = valute.find("Nominal")
            value_elem = valute.find("Value")
            name_elem = valute.find("Name")

            char_code = (char_code_elem.text or "").strip() if char_code_elem is not None else ""
            nominal_text = (nominal_elem.text or "").strip() if nominal_elem is not None else ""
            value_text = (value_elem.text or "").strip() if value_elem is not None else ""
            name = (name_elem.text or "").strip() if name_elem is not None else ""

            if not char_code or not name:
                continue

            if char_code in seen_codes:
                raise SourceUnavailableError(f"Duplicate currency code '{char_code}' in XML")
            seen_codes.add(char_code)

            try:
                nominal = Decimal(nominal_text.replace(",", "."))
                value = Decimal(value_text.replace(",", "."))
            except (InvalidOperation, TypeError):
                continue

            if not nominal.is_finite() or not value.is_finite() or nominal <= Decimal("0") or value <= Decimal("0"):
                continue

            rate_to_mdl = value / nominal
            currencies[char_code] = Currency(code=char_code, name=name, rate_to_mdl=rate_to_mdl)

        if not currencies:
            raise NoRatesForDateError(f"No usable currency rates found for date {date_str}")

        currencies["MDL"] = Currency(code="MDL", name="Moldovan Leu", rate_to_mdl=Decimal("1"))

        return RateSnapshot(rate_date=rate_date, source="BNM", currencies=currencies)
