import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date
import requests

from currency_converter.bnm_client import BnmClient

SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<ValCurs Date="04.11.2026" name="Official exchange rate">
  <Valute>
    <CharCode>EUR</CharCode>
    <Nominal>1</Nominal>
    <Value>19.6500</Value>
    <Name>Euro</Name>
  </Valute>
  <Valute>
    <CharCode>USD</CharCode>
    <Nominal>1</Nominal>
    <Value>18.1200</Value>
    <Name>US Dollar</Name>
  </Valute>
  <Valute>
    <CharCode>RON</CharCode>
    <Nominal>10</Nominal>
    <Value>39.5000</Value>
    <Name>Romanian Leu</Name>
  </Valute>
</ValCurs>"""

EMPTY_XML = """<?xml version="1.0" encoding="utf-8"?>
<ValCurs Date="02.11.2026" name="Official exchange rate">
</ValCurs>"""

NO_USABLE_RATES_XML = """<?xml version="1.0" encoding="utf-8"?>
<ValCurs Date="02.11.2026" name="Official exchange rate">
  <Valute>
    <CharCode></CharCode>
    <Nominal>0</Nominal>
    <Value>0</Value>
    <Name></Name>
  </Valute>
</ValCurs>"""

MALFORMED_XML = """this is not xml at all"""


class TestBnmClientUrlConstruction:
    def test_constructs_correct_url_for_date(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            client.fetch_rates(date(2026, 11, 4))
            args, kwargs = mock_get.call_args
            url = args[0] if args else kwargs.get("url", "")
            assert "bnm.md" in url
            assert "04.11.2026" in url
            assert "get_xml=1" in url

    def test_date_formatted_as_dd_mm_yyyy(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            client.fetch_rates(date(2026, 1, 5))
            args, kwargs = mock_get.call_args
            url = args[0] if args else kwargs.get("url", "")
            assert "05.01.2026" in url

    def test_uses_10_second_timeout(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            client.fetch_rates(date(2026, 11, 4))
            args, kwargs = mock_get.call_args
            assert kwargs.get("timeout") == 10


class TestBnmClientXmlParsing:
    def test_parses_eur_rate_correctly(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            snapshot = client.fetch_rates(date(2026, 11, 4))
            assert "EUR" in snapshot.currencies
            assert snapshot.currencies["EUR"].rate_to_mdl == Decimal("19.65")

    def test_parses_nominal_correctly_ron(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            snapshot = client.fetch_rates(date(2026, 11, 4))
            # RON: Nominal=10, Value=39.5 -> rate = 39.5 / 10 = 3.95
            assert snapshot.currencies["RON"].rate_to_mdl == Decimal("3.95")

    def test_inserts_mdl_with_rate_one(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            snapshot = client.fetch_rates(date(2026, 11, 4))
            assert "MDL" in snapshot.currencies
            assert snapshot.currencies["MDL"].rate_to_mdl == Decimal("1")

    def test_snapshot_date_matches_requested_date(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            snapshot = client.fetch_rates(date(2026, 11, 4))
            assert snapshot.rate_date == date(2026, 11, 4)

    def test_snapshot_source_is_bnm(self):
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = SAMPLE_XML
            mock_get.return_value = mock_response
            snapshot = client.fetch_rates(date(2026, 11, 4))
            assert snapshot.source == "BNM"


class TestBnmClientFailures:
    def test_connection_error_raises_source_unavailable(self):
        from currency_converter.interfaces import SourceUnavailableError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("No network")
            with pytest.raises(SourceUnavailableError):
                client.fetch_rates(date(2026, 11, 4))

    def test_timeout_error_raises_source_unavailable(self):
        from currency_converter.interfaces import SourceUnavailableError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Timed out")
            with pytest.raises(SourceUnavailableError):
                client.fetch_rates(date(2026, 11, 4))

    def test_server_error_500_raises_source_unavailable(self):
        from currency_converter.interfaces import SourceUnavailableError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            with pytest.raises(SourceUnavailableError):
                client.fetch_rates(date(2026, 11, 4))

    def test_malformed_xml_raises_source_unavailable(self):
        from currency_converter.interfaces import SourceUnavailableError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = MALFORMED_XML
            mock_get.return_value = mock_response
            with pytest.raises(SourceUnavailableError):
                client.fetch_rates(date(2026, 11, 4))

    def test_http_404_raises_no_rates_for_date(self):
        from currency_converter.interfaces import NoRatesForDateError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            with pytest.raises(NoRatesForDateError):
                client.fetch_rates(date(2026, 11, 4))

    def test_empty_xml_raises_no_rates_for_date(self):
        from currency_converter.interfaces import NoRatesForDateError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = EMPTY_XML
            mock_get.return_value = mock_response
            with pytest.raises(NoRatesForDateError):
                client.fetch_rates(date(2026, 11, 4))

    def test_xml_without_usable_rates_raises_no_rates_for_date(self):
        from currency_converter.interfaces import NoRatesForDateError
        client = BnmClient()
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = NO_USABLE_RATES_XML
            mock_get.return_value = mock_response
            with pytest.raises(NoRatesForDateError):
                client.fetch_rates(date(2026, 11, 4))
