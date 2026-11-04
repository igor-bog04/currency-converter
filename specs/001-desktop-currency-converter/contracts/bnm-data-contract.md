# BNM Data Contract

## Request

- **Service**: National Bank of Moldova official exchange rates
- **Method**: HTTP GET
- **Endpoint**: `https://www.bnm.md/en/official_exchange_rates`
- **Query**: `get_xml=1` and `date=DD.MM.YYYY`
- **Timeout**: 10 seconds per HTTP request
- **Date behavior**: Request the selected date first. If the response is empty or contains no
  usable rates, request each prior calendar date in sequence, through 10 days before the selected
  date (at most 11 dates including the selected date).

## Expected Response

The response has an XML root like `<ValCurs Date="…" name="Official exchange rate">`. Each
`<Valute>` currency entry contains:

- `CharCode`: currency code
- `Nominal`: number of currency units represented by `Value`
- `Value`: MDL value for the stated nominal
- `Name`: source-provided currency name

Each usable entry produces a rate of `Value / Nominal` MDL per one unit. MDL is not expected in
the response and is added locally with a rate of 1.

## Validation and Failure Handling

- A response is usable only when its XML is well-formed, has a `ValCurs` root and expected
  `Valute` entries, includes a valid `Date` in `DD.MM.YYYY` matching the requested candidate date,
  non-empty codes/names, and positive numeric `Nominal` and `Value` values. Numeric values must be
  finite; `NaN` and infinities are invalid.
- Duplicate codes or malformed/unexpected XML make that date's response unavailable rather than
  producing a partial or misleading rate set.
- Empty results and documents without usable rate entries trigger the date fallback sequence.
- A date-specific HTTP 404 is treated as no published rates for that date and advances to the
  previous date. Other HTTP errors, timeouts, and connection failures make the online source
  unavailable and trigger cache fallback; they must not escape into the UI as an unhandled
  exception.
- Malformed or unexpected XML is an unavailable-source failure, not a reason to trust partial data.
  If a cached snapshot is available, offer it according to the offline fallback flow.
- If all attempted online dates are unavailable, the application may offer the last successful
  cached snapshot. The user must see its effective date and explicitly choose whether to use it.
- The displayed source remains BNM; the UI also identifies when the snapshot is cached or from an
  earlier effective date.
- Weekends and holidays do not automatically trigger fallback: observed weekend and holiday
  requests returned populated rate entries, so the response content determines whether fallback
  is needed.
- These are official reference rates, not a promise of a bank's or exchange provider's customer
  transaction rate.

## Conversion Semantics

Rates are expressed as MDL per one currency unit. For currencies A and B:

`amount_B = amount_A * rate_A_to_MDL / rate_B_to_MDL`

The calculation retains Decimal precision until the output is rounded to two decimal places.
The displayed rate in each direction is rounded independently to four decimal places.
