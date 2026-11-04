import pytest
from decimal import Decimal
from datetime import date
import xml.etree.ElementTree as ET

SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<ValCurs Date="04.11.2026" name="Official exchange rate">
  <Valute NumCode="978" CharCode="EUR" Nom="1" Name="Euro">
    <CharCode>EUR</CharCode>
    <Nominal>1</Nominal>
    <Value>19.6500</Value>
    <Name>Euro</Name>
  </Valute>
  <Valute NumCode="840" CharCode="USD" Nom="1" Name="US Dollar">
    <CharCode>USD</CharCode>
    <Nominal>1</Nominal>
    <Value>18.1200</Value>
    <Name>US Dollar</Name>
  </Valute>
  <Valute NumCode="946" CharCode="RON" Nom="10" Name="Romanian Leu">
    <CharCode>RON</CharCode>
    <Nominal>10</Nominal>
    <Value>39.5000</Value>
    <Name>Romanian Leu</Name>
  </Valute>
</ValCurs>"""

SAMPLE_DATE = date(2026, 11, 4)
SAMPLE_DATE_STR = "04.11.2026"


@pytest.fixture
def sample_xml():
    return SAMPLE_XML


@pytest.fixture
def sample_date():
    return SAMPLE_DATE


@pytest.fixture
def sample_date_str():
    return SAMPLE_DATE_STR
