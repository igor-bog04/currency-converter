# Feature Specification: Desktop Currency Converter

**Feature Branch**: `001-desktop-currency-converter`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "Build a desktop currency converter with a graphical user interface.

Data source: official exchange rates of the National Bank of Moldova (BNM), XML at https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=DD.MM.YYYY. Each currency has CharCode, Nominal and Value; the rate of 1 unit in MDL is Value / Nominal. MDL itself is not in the list and must be added with rate 1. Conversion between two foreign currencies goes through MDL (cross rate).

The window contains:
1. Amount input field.
2. Source currency selector and target currency selector (code + name, e.g. "EUR — Euro"), MDL included, with a swap button.
3. Rate date selector, today by default.
4. Convert button, disabled until amount and both currencies are filled.
5. Result: converted amount, plus the rate used in both directions (1 A = x B and 1 B = y A).
6. Rate date and data source (BNM) always visible next to the result.

Required behavior:
- No network: the app does not crash, shows a clear message, and if cached data exists offers to use the last successfully received rates, showing their date.
- Weekends and holidays: BNM publishes rates on working days only (usually before 13:00 Chisinau time). If the response for the chosen date is empty or has no rates, the app steps back day by day (up to 10 days) to the latest available rates and clearly tells the user which date is used and why.
- Invalid input: negative amount, zero, letters, empty field, more than 2 decimal places — an error message next to the field, no conversion. Both comma and dot are accepted as the decimal separator.
- Same currency in both selectors: handled without error, the result equals the amount with rate 1.
- Caching: the last successful response is saved locally and survives restarts.
- Malformed or unexpected XML from the source is treated like an unavailable source, never a crash."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert money for a selected date (Priority: P1)

A user enters an amount, chooses a source and target currency, and selects a rate date. The app calculates the converted value using the official BNM rates and shows the exchange rate in both directions together with the rate date and source.

**Why this priority**: This is the core user value of the product. Without a reliable conversion result, the application does not satisfy its primary purpose.

**Independent Test**: Can be fully tested by entering a valid amount, selecting currencies, and confirming that the converted result matches the correct MDL cross-rate conversion for the chosen day.

**Acceptance Scenarios**:

1. **Given** the user opens the converter with a valid amount and two currencies selected, **When** they click Convert, **Then** the app displays the converted amount and the exchange rates used in both directions.
2. **Given** the user has chosen the same currency for both selectors, **When** they convert, **Then** the result equals the original amount and the effective rate is 1.
3. **Given** the selected date has valid BNM rates, **When** conversion runs, **Then** the app shows the rate date and BNM as the data source next to the result.

---

### User Story 2 - Handle unavailable or missing rate data (Priority: P1)

A user selects a date for which the BNM source is unavailable, closed, or empty. The app does not fail; it finds the latest usable historic rate within the allowed fallback window and clearly explains the date used and the reason.

**Why this priority**: Financial tools must remain usable even when rates are missing, and users must understand which rate is currently being applied.

**Independent Test**: Can be fully tested by choosing a weekend or holiday date or simulating an empty response and confirming that the app selects the nearest prior available date and presents a clear message.

**Acceptance Scenarios**:

1. **Given** the selected date has no published BNM rates, **When** the app checks the source, **Then** it searches backward up to 10 days and uses the latest available date.
2. **Given** the fallback date is found, **When** conversion is displayed, **Then** the app states which date is in use and why the fallback was applied.
3. **Given** no source data is available and no cached data exists, **When** conversion is attempted, **Then** the app shows a clear error message instead of crashing.

---

### User Story 3 - Recover gracefully from network and parsing failures (Priority: P2)

A user attempts to convert while offline or when the source returns malformed XML. The app shows a clear Russian-language message and, if cached data exists, offers the last successful rates with their date as a fallback option.

**Why this priority**: Product reliability matters for user trust, especially in a financial application where network and source issues are common.

**Independent Test**: Can be fully tested by disconnecting the app from the network or supplying malformed source data and confirming that the app remains responsive and communicates the issue clearly.

**Acceptance Scenarios**:

1. **Given** the network is unavailable, **When** the user requests a conversion, **Then** the app does not crash and shows a clear error message.
2. **Given** cached rates exist, **When** data is unavailable from the source, **Then** the app offers the last successful rates and shows their date.
3. **Given** the XML returned by the source is malformed or unexpected, **When** the app processes it, **Then** it treats it as an unavailable source and continues without crashing.

---

### User Story 4 - Validate input and preserve user trust (Priority: P2)

A user enters invalid values or leaves required fields blank. The app prevents conversion, shows an error next to the field, and accepts both dot and comma decimal separators while enforcing the specified monetary constraints.

**Why this priority**: Preventing invalid conversion attempts reduces mistakes and keeps financial calculations trustworthy.

**Independent Test**: Can be fully tested by entering values such as zero, negative numbers, letters, empty strings, and inputs with more than two decimal places and confirming the app blocks the conversion.

**Acceptance Scenarios**:

1. **Given** the amount field is empty or contains letters, **When** the user attempts conversion, **Then** the app shows a validation error and does not convert.
2. **Given** the amount is zero, negative, or has more than 2 decimal places, **When** the user submits the form, **Then** the app blocks the conversion and displays an error next to the field.
3. **Given** the user enters either a comma or a dot as the decimal separator, **When** the amount is validated, **Then** the input is accepted as a valid number when it meets the format rules.

---

### Edge Cases

- What happens when the user chooses a future date that has no published rates? The app must step back through the fallback window and clearly indicate the effective rate date.
- How does the system handle malformed XML from the source? It treats the response as unavailable and proceeds without crashing.
- What happens when both selector values are identical? The conversion is treated as a self-conversion with an effective rate of 1 and the original amount is returned.
- What happens when the user tries to submit before both currencies are selected? The Convert button remains disabled and no conversion is attempted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a desktop currency conversion form with an amount field, source currency selector, target currency selector, rate date selector, swap button, and Convert action.
- **FR-002**: The system MUST include Moldova Leu (MDL) in the currency list with a fixed rate of 1 and MUST treat MDL as the reference currency when converting between two foreign currencies.
- **FR-003**: The system MUST fetch official BNM exchange-rate data from the published XML endpoint for the selected date and MUST derive each currency rate as Value / Nominal.
- **FR-004**: The system MUST calculate cross rates through MDL for conversions between two non-MDL currencies and MUST display the rate in both directions, including the resulting converted amount.
- **FR-005**: The system MUST show the selected rate date and the BNM data source next to the result at all times.
- **FR-006**: The system MUST disable the Convert action until the amount field is valid and both source and target currencies have been selected.
- **FR-007**: The system MUST accept a positive amount consisting only of digits with at most one decimal separator (comma or dot) and at most two fractional digits. It MUST reject empty values, letters, negative amounts, zero amounts, grouping separators (including spaces, apostrophes, or thousands commas), scientific notation, multiple decimal separators, and amounts with more than two fractional digits with an adjacent field-level error.
- **FR-008**: The system MUST handle same-currency selections without error and MUST return the original amount with an effective rate of 1.
- **FR-009**: The system MUST treat a missing network connection as an unavailable source and MUST show a clear Russian-language error message without crashing.
- **FR-010**: When the source is unavailable, the system MUST offer the last successfully cached rates, show their date, and use them only if the user accepts.
- **FR-011**: The system MUST check the selected date and, when the response is empty, contains no usable rates, or returns a date-specific HTTP 404, step backward day by day up to 10 days to the latest available rate set. Transport errors and server errors MUST NOT trigger date fallback; they MUST be handled as an unavailable source through the offline/cache recovery path.
- **FR-012**: The system MUST clearly inform the user which effective rate date is being used and why the fallback was necessary.
- **FR-013**: The system MUST save the last successful response locally so the cached rates remain available after application restarts.
- **FR-014**: The system MUST treat malformed or unexpected XML as an unavailable source and MUST not crash the application.
- **FR-015**: The system MUST keep UI labels and messages in Russian while the project documentation remains in English.
- **FR-016**: While requesting prior dates because rates are missing, the system MUST show a loading indicator and keep the window responsive.

### Key Entities

- **Currency**: A supported currency with a code, display name, and an exchange rate expressed relative to MDL for a specific date.
- **Rate Snapshot**: The set of official BNM rates returned for a given date, including the source date and the list of currencies and values used for conversion.
- **Conversion Request**: The amount entered by the user, the source currency, the target currency, and the rate date selected for calculation.
- **Conversion Result**: The converted amount, the rate in both directions, and the effective rate date and source used for the calculation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a valid conversion in under 10 seconds from submitting the conversion to seeing the result when one successful BNM response is returned over a normal internet connection. This target does not apply when date fallback is required.
- **SC-002**: 100% of invalid amount inputs are rejected with a visible error and no conversion is performed.
- **SC-003**: The app falls back to the latest available rate within 10 days without crashing when BNM data is missing for a selected date.
- **SC-004**: The user can see the active rate date and source next to each conversion result and can understand when a fallback was applied.
- **SC-005**: The application remains functional after a restart when cached BNM data is available and does not lose the last successful rate snapshot.
- **SC-006**: Users successfully complete conversions with same-currency selections and receive a result equal to the entered amount.
- **SC-007**: During date fallback, the loading indicator remains visible and the window continues responding while prior dates are requested.

## Assumptions

- Users operate the application on a desktop environment with standard input and display capabilities.
- The source data is expected to be available through the official BNM XML endpoint for working days, with missing data on weekends and public holidays.
- The application may use local persistent storage to retain the last successful exchange-rate snapshot.
- All user-facing messages are presented in Russian, while the project documentation and authoring context remain in English.
- The feature scope is limited to a desktop currency conversion workflow and does not include multi-user accounts or backend synchronization.
