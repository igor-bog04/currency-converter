# Research: Desktop Currency Converter

## Decisions

### Runtime and Desktop Interface

- **Decision**: Use Python 3.11+ and CustomTkinter for a Windows desktop interface.
- **Rationale**: These are explicit project constraints. CustomTkinter supplies the requested
  rounded-card presentation and light/dark appearance while retaining a desktop interaction model.
- **Alternatives considered**: A browser-based UI or another GUI toolkit; neither is needed for the
  requested single-user Windows desktop app.

### BNM Retrieval and XML Parsing

- **Decision**: Retrieve the official BNM XML with `requests`, a 10-second timeout per request,
  and parse it with `xml.etree.ElementTree`. Treat HTTP, timeout, malformed, and structurally
  unexpected responses as unavailable data.
- **Rationale**: This follows the specified official endpoint and standard-library XML parser,
  with explicit failure behavior rather than partial or fabricated rates.
- **Alternatives considered**: Third-party XML libraries and alternate rate providers; both are
  unnecessary and would change the mandated source or dependency footprint.
- **Verified source details**: The endpoint requires a zero-padded `DD.MM.YYYY` date query. The
  observed XML root is `ValCurs` with `Date` and `name` attributes; entries use `Valute` and
  contain `CharCode`, `Nominal`, `Name`, and `Value`. MDL was absent in the sampled response.
  Weekend/holiday requests in the sample returned populated results, so fallback is based on
  actual empty/unusable responses, not on weekday assumptions. A date-specific HTTP 404 is treated
  as no rates for that candidate date; transport failures and server errors abort online lookup
  and trigger cache fallback.

### Rate-Date Fallback

- **Decision**: Query the selected date first, then each preceding calendar date through 10 days
  earlier (at most 11 dates total). Stop on the first fully validated non-empty rate set.
- **Rationale**: This makes the spec's "up to 10 days" precise and selects the nearest available
  rate date. The exact date and fallback reason are part of the result metadata and user message.
- **Alternatives considered**: Fixed weekday arithmetic or a calendar of BNM holidays; either can
  miss exceptional publication gaps and is not required when actual source responses can be
  checked sequentially.

### Decimal Conversion and Display

- **Decision**: Parse all monetary input and BNM numeric values as `Decimal`. Calculate
  `amount * source_rate_to_mdl / target_rate_to_mdl` without intermediate rounding; quantize the
  converted amount to two decimal places and each displayed directional rate independently to
  four decimal places, using `ROUND_HALF_UP`. Reject non-finite values and serialize Decimal cache
  values as decimal strings.
- **Rationale**: Decimal arithmetic is a constitutional requirement. Keeping full precision until
  display avoids compounded rounding; explicit half-up rounding makes boundary behavior stable
  and testable.
- **Alternatives considered**: Binary floating point (prohibited) and rounding intermediate MDL
  amounts (can introduce avoidable cross-rate error). Half-even rounding is also deterministic but
  is not selected because the product's user-facing amount convention is conventional half-up.
- **Rounding note**: The exact tie-breaking mode is not specified in the user requirements;
  half-up is an explicit design default and must be covered by boundary tests.

### Cache Persistence and Offline Use

- **Decision**: Store a single last-successful validated snapshot in
  `%APPDATA%\CurrencyConverter\cache.json`. Write a temporary file in the same directory and
  atomically replace the cache. When online retrieval fails, offer a readable cached snapshot and
  require the user to confirm its use.
- **Rationale**: This follows the requested persistence and user choice, protects against partial
  writes, and retains the source's effective date for transparency.
- **Alternatives considered**: Multiple historical cache entries or a database; neither is
  required for the single-snapshot offline fallback.

### Responsive UI and Error Reporting

- **Decision**: Run all network retrieval, parsing, and date fallback in a worker thread. Send
  completion/error outcomes through a thread-safe queue; a UI-thread `after` callback owns all
  widget updates. Only one rate operation runs at a time, and stale results are ignored when the
  request is no longer current. Present clear Russian messages for network, XML, and file failures
  and keep the window responsive.
- **Rationale**: The GUI event loop must remain available while requests run; widget updates belong
  on the UI thread. Explicit outcomes avoid unhandled exceptions and unclear fallback behavior.
- **Alternatives considered**: Synchronous requests on the UI thread (would freeze the window) and
  a separate service process (unneeded for a single-user local app).
- **Timeout note**: Requests' 10-second timeout bounds socket inactivity, not necessarily total
  elapsed time. The worker thread is therefore necessary even when a timeout is configured.

### Test Strategy and Dependencies

- **Decision**: Keep runtime and test dependencies in `requirements.txt`; run all tests with
  `python -m pytest`. Unit-test every non-UI layer and mock HTTP responses and failures.
- **Rationale**: This matches the project requirements and makes core financial and failure-path
  behavior deterministic without network access.
- **Alternatives considered**: Live-network tests (fragile and non-repeatable) and a second test
  command or dependency manifest (not required by the project's single-command workflow).

## Sources

- [BNM official exchange rates XML for 04.11.2026](https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=04.11.2026)
  confirms the endpoint format and observed XML fields. [A weekend request](https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=01.11.2026)
  and [a holiday request](https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=01.01.2026)
  returned populated lists, so actual response contents determine fallback.
- [Python `decimal`](https://docs.python.org/3/library/decimal.html),
  [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html),
  [threading](https://docs.python.org/3/library/threading.html),
  [Tkinter threading model](https://docs.python.org/3.11/library/tkinter.html#threading-model),
  [queue](https://docs.python.org/3/library/queue.html),
  [tempfile](https://docs.python.org/3/library/tempfile.html), and
  [os.replace](https://docs.python.org/3/library/os.html#os.replace) documentation.
- [CustomTkinter documentation](https://customtkinter.tomschimansky.com/documentation/) and
  [Requests timeout documentation](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
  inform UI-thread and HTTP timeout practices.
