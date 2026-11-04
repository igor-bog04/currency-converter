# Tasks: Desktop Currency Converter

**Input**: Design documents from `specs/001-desktop-currency-converter/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/bnm-data-contract.md,
quickstart.md

**Tests**: Test tasks are included because the project constitution requires pytest unit tests for
all non-UI logic and mocked network access.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing
after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a separate file and has no incomplete dependency.
- **[Story]**: User-story label for story phases; setup, foundation, and polish tasks omit it.
- Every task specifies concrete file paths.

## Phase 1: Setup

**Purpose**: Initialize the Python desktop project and test environment.

- [ ] T001 Create the `currency_converter/` package, `tests/unit/`, and root `main.py` structure per `specs/001-desktop-currency-converter/plan.md`
- [ ] T002 Add `customtkinter` and `requests` runtime dependencies and `pytest` test dependency to `requirements.txt`
- [ ] T003 [P] Create test package configuration and shared fixtures in `tests/conftest.py`
- [ ] T004 Add English setup, launch, and `python -m pytest` instructions to `README.md`

## Phase 2: Foundational

**Purpose**: Establish shared models, explicit boundaries, and error/result types required by every
story.

- [ ] T005 [P] Add model and interface contract unit tests in `tests/unit/test_models.py`; run them and confirm failure before implementing the models and protocols
- [ ] T006 Define `Currency`, `RateSnapshot`, and conversion result models in `currency_converter/models.py`; currency code and name are non-empty, codes are unique per snapshot, rate is a finite positive Decimal, and MDL rate is exactly 1
- [ ] T007 Define narrow rate-source, cache, and rate-provider protocols plus typed source/cache outcome errors in `currency_converter/interfaces.py`
- [ ] T008 Add `currency_converter/__init__.py` package exports for the public model and interface types

**Checkpoint**: Shared data shapes and module boundaries are ready; user-story work can proceed.

## Phase 3: User Story 1 - Convert money for a selected date (Priority: P1) 🎯 MVP

**Goal**: Calculate and present a valid conversion from official BNM rates for a chosen date,
including same-currency conversions, both directional rates, and source/date attribution.

**Independent Test**: With deterministic BNM XML fixtures, convert a positive amount between MDL
and a foreign currency and between two foreign currencies; verify result, both rates, and effective
date/source. Same-currency conversion returns the amount unchanged with rate 1.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add XML parsing and rate-derivation tests for `CharCode`, `Name`, `Nominal`, `Value`, and MDL insertion in `tests/unit/test_bnm_client.py`
- [ ] T010 [P] [US1] Add Decimal conversion tests for MDL, foreign cross rates, both directional rates, same-currency conversion, and 2/4-place formatting in `tests/unit/test_converter.py`

### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement BNM request construction, `DD.MM.YYYY` formatting, 10-second timeout, XML structural validation, and `Value / Nominal` rates in `currency_converter/bnm_client.py`
- [ ] T012 [P] [US1] Implement pure Decimal cross-rate conversion, same-currency behavior, and `ROUND_HALF_UP` output rounding in `currency_converter/converter.py`
- [ ] T013 [US1] Implement the initial rate provider path for one selected date and validated BNM snapshot in `currency_converter/rate_provider.py`
- [ ] T014 [US1] Implement the currency selectors, amount control, date control, swap control, disabled-until-required-fields result action, result and rate display, BNM/date attribution, and light/dark themed rounded-card UI in `currency_converter/ui.py`
- [ ] T015 [US1] Wire concrete BNM client, provider, converter, and UI implementations from the composition root in `main.py`

**Checkpoint**: User Story 1 supports online conversion; invalid/missing-rate recovery is extended in
following stories.

## Phase 4: User Story 2 - Handle unavailable or missing rate dates (Priority: P1)

**Goal**: Select the nearest available prior rate date when the selected date's result is empty,
contains no usable rates, or returns a date-specific HTTP 404; explain the effective date and reason.

**Independent Test**: Mock an empty or 404 response on the selected date followed by a valid prior
date; verify the first usable rate snapshot is selected within 10 prior days and the UI presents
the requested/effective date distinction and reason.

### Tests for User Story 2

- [ ] T016 [P] [US2] Add provider tests for selected-date success, empty response, date-specific 404, nearest-prior selection, and the 10-prior-date limit in `tests/unit/test_rate_provider.py`
- [ ] T017 [P] [US2] Add UI outcome tests for requested date, effective date, and fallback explanation in `tests/unit/test_ui_state.py`

### Implementation for User Story 2

- [ ] T018 [US2] Extend `currency_converter/bnm_client.py` to classify date-specific HTTP 404 and empty/no-rate XML separately from transport/server failures
- [ ] T019 [US2] Implement sequential lookup of selected date through 10 preceding dates and typed fallback outcomes in `currency_converter/rate_provider.py`
- [ ] T020 [US2] Present Russian-language loading, no-rate fallback reason, requested/effective date, and active-state feedback in `currency_converter/ui.py`

**Checkpoint**: User Story 2 selects the latest available rate in the defined search window.

## Phase 5: User Story 3 - Recover gracefully from network and parsing failures (Priority: P2)

**Goal**: Keep the application resilient when BNM is unavailable, offer a valid persisted last
successful snapshot, and never crash on cache, network, or XML errors.

**Independent Test**: Mock network and malformed XML failures with valid, missing, and corrupt
cache cases; verify the user can accept cached rates with their date or receive a clear Russian
error when none are usable.

### Tests for User Story 3

- [ ] T021 [P] [US3] Add cache tests for decimal-string JSON round trips, AppData path, atomic replacement, corrupt JSON, and read/write failures in `tests/unit/test_cache.py`
- [ ] T022 [P] [US3] Add provider tests for network timeout/errors, malformed XML, cache offer/decline/accept, and cache date reporting in `tests/unit/test_rate_provider.py`
- [ ] T023 [P] [US3] Add UI resilience tests for Russian error and cache offer states in `tests/unit/test_ui_state.py`

### Implementation for User Story 3

- [ ] T024 [US3] Implement the single-snapshot JSON cache in `%APPDATA%\CurrencyConverter\cache.json`, serializing Decimal values as strings and replacing a same-directory temporary file atomically in `currency_converter/cache.py`
- [ ] T025 [US3] Extend `currency_converter/rate_provider.py` to fall back to last-successful cache after online source unavailability and expose explicit accept/decline outcomes without replacing cache with invalid data
- [ ] T026 [US3] Run network lookup, parse, and fallback in a worker and deliver outcomes through a thread-safe queue polled with UI-thread callbacks in `currency_converter/ui.py`
- [ ] T027 [US3] Add Russian-language messages for connection, timeout, malformed XML, cache read/write, no-cache, and cached-rate acceptance/decline outcomes in `currency_converter/ui.py`
- [ ] T028 [US3] Handle cancellation and window close without blocking the UI or applying stale worker results in `currency_converter/ui.py`

**Checkpoint**: Online and cached rates are presented transparently and recoverably.

## Phase 6: User Story 4 - Validate input and preserve user trust (Priority: P2)

**Goal**: Accept valid positive decimal input with either decimal separator and prevent invalid
conversion requests with adjacent Russian field errors.

**Independent Test**: Validate empty, alphabetic, zero, negative, excess-precision, comma-decimal,
dot-decimal, grouping, and non-finite inputs; verify only specified valid forms enable conversion.

### Tests for User Story 4

- [ ] T029 [P] [US4] Add amount validation tests for empty, letters, zero, negative, over-two-decimal, comma, dot, grouping, scientific notation, and non-finite inputs in `tests/unit/test_validation.py`
- [ ] T030 [US4] Add UI-state tests for Convert-button enablement and adjacent validation feedback in `tests/unit/test_ui_state.py`

### Implementation for User Story 4

- [ ] T031 [US4] Implement strict amount parsing into finite Decimal values, accepting either comma or dot and rejecting zero, negative, empty, non-numeric, and more than two fractional digits in `currency_converter/validation.py`
- [ ] T032 [US4] Connect amount and selector validation to Convert-button disabled state and adjacent Russian errors in `currency_converter/ui.py`
- [ ] T033 [US4] Preserve input validation and current conversion result when swapping selected currencies in `currency_converter/ui.py`

**Checkpoint**: Invalid values cannot reach the converter; valid amount formats are consistently
accepted.

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete cross-story documentation, review, and validation.

- [ ] T034 [P] Document English project overview, BNM reference-rate caveat, setup, run command, cache behavior, and `python -m pytest` in `README.md`
- [ ] T035 [P] Add isolated provider-to-converter integration tests with mocked BNM responses and a temporary cache in `tests/integration/test_conversion_flow.py`
- [ ] T036 Run `python -m pytest` and resolve failures across `tests/unit/`
- [ ] T037 Follow `specs/001-desktop-currency-converter/quickstart.md` to review install, launch, conversion, fallback, offline cache, and invalid-input acceptance paths
- [ ] T038 Review branch and PR workflow for separate specs, implementation, and test stages and document any required handoff in `README.md`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No prerequisite; all setup tasks may begin immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user-story phases.
- **US1 (Phase 3)**: Depends on the foundational models and interfaces.
- **US2 (Phase 4)**: Depends on US1's BNM client/provider path to extend source-date lookup.
- **US3 (Phase 5)**: Depends on US2's provider outcomes and adds persistence and offline recovery.
- **US4 (Phase 6)**: Depends on US1's UI/conversion flow; validation-module work can start after Phase 2, while UI integration follows US2/US3 to avoid conflicting edits.
- **Polish (Phase 7)**: Depends on all selected stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another story. Defines the MVP.
- **US2 (P1)**: Extends US1's rate-provider path; should follow US1 to avoid duplicate work.
- **US3 (P2)**: Builds on the source/provider outcomes from US1 and US2; implement after them.
- **US4 (P2)**: Uses the UI introduced in US1. Its isolated validation module and unit tests can be prepared after Phase 2, but the story's UI integration follows US2 and US3 to avoid parallel edits to `currency_converter/ui.py`.

### Parallel Opportunities

- Setup: T003 can run alongside T001/T002 after directory creation. T004 and T034 both update `README.md`, so keep them sequential.
- Foundation: T005 defines expected contracts before T006/T007; implementation starts only after the tests fail against the missing types. T008 follows the model and interface definitions.
- US1: T009, T010, T011, and T012 are separable files after foundation; T013 follows the client; T014 and T015 follow their injected interface definitions.
- US2: T016 and T017 are independent tests; T018 and T019 are sequential source/provider changes, followed by T020.
- US3: T021, T022, and T023 can be developed in separate files; T024 precedes T025; T026-T028 touch UI and should be coordinated or serialized.
- US4: T029 is isolated in `tests/unit/test_validation.py`; T030 shares the UI-state test file with earlier stories and should be coordinated. T031 precedes T032; T032/T033 follow the earlier story UI changes.

## Parallel Example: User Story 1

```text
After Phase 2, write and run the tests first:
Task: T009 XML client tests in tests/unit/test_bnm_client.py
Task: T010 Decimal converter tests in tests/unit/test_converter.py

Confirm these tests fail before implementing their behavior, then:
Task: T011 BNM client in currency_converter/bnm_client.py
Task: T012 Pure converter in currency_converter/converter.py

After T011:
Task: T013 Rate provider in currency_converter/rate_provider.py
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational tasks.
2. Complete US1: online BNM conversion, core UI, Decimal cross-rate result.
3. Validate US1 with mocked client/converter unit tests and the quickstart.
4. Deliver the conversion MVP before adding fallback and offline recovery.

### Incremental Delivery

1. Add US2 to support missing dates and clear prior-date selection.
2. Add US3 to persist successful rates and offer offline recovery.
3. Add US4 to complete strict input validation and disabled-state behavior.
4. Complete cross-cutting documentation, all tests, and quickstart review.

## Notes

- `[P]` tasks use distinct files and do not depend on unfinished tasks.
- `[US#]` labels map directly to user stories in `specs/001-desktop-currency-converter/spec.md`.
- Tests are required by the project constitution; use mocked HTTP and avoid live-source tests.
- Keep user-visible UI text in Russian and project documentation in English.
- The `specs` branch is for specification artifacts; implementation and test stages require their own branches and main merges occur through pull requests.
