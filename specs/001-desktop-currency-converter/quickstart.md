# Quickstart: Desktop Currency Converter

## Prerequisites

- Windows with Python 3.11 or newer
- Internet access for retrieving current BNM rates

## Install

From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Expected result: a Russian-language desktop window opens with MDL and BNM currencies, a date
selector defaulting to today, and conversion controls.

## Validate

```powershell
python -m pytest
```

Expected result: the full unit test suite completes successfully. Network requests are mocked in
tests; no live BNM access is required.

## End-to-End Checks

1. Enter a positive amount with up to two decimal places, select two currencies, and convert.
   Verify the result, both directional rates, effective date, and BNM attribution.
2. Select the same source and target currency. Verify the amount is unchanged and both displayed
   rates are 1.
3. Select a date without published rates. Verify the app searches backward no more than 10 days
   and explains the effective date.
4. With the network unavailable, verify the app remains responsive and offers a persisted
   last-successful snapshot, if one exists.
5. Enter zero, a negative number, letters, an empty amount, and an amount with more than two
   decimal places. Verify each is rejected with a Russian-language field error.

See [the data model](./data-model.md) and [the BNM data contract](./contracts/bnm-data-contract.md)
for the rate and fallback semantics.
