# Desktop Currency Converter

A desktop application that fetches official exchange rates from the National Bank of Moldova (BNM) and performs currency conversions.

## Prerequisites

- Python 3.11 or higher
- Windows (uses `%APPDATA%` for cache storage)

## Setup

1. Clone the repository and switch to the appropriate branch:
   ```powershell
   git clone <repo-url>
   cd currency-converter
   ```

2. Create and activate a virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Launch

```powershell
.\.venv\Scripts\python.exe main.py
```

## Running Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Or, with the virtual environment activated:

```powershell
python -m pytest -v
```

## Notes

- Exchange rates are fetched from the BNM public XML API (`bnm.md`). These are **reference rates** and may differ from commercial bank rates.
- The last successful rate snapshot is cached in `%APPDATA%\CurrencyConverter\cache.json` and offered when the network is unavailable.
- All user-visible text in the UI is in Russian.
- Tests use mocked HTTP calls and do not require a live internet connection.
