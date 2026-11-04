<!-- Sync Impact Report: version 1.0.0 → 1.1.0 | Modified principles: Architecture & Separation of Concerns, Reliability & User Communication, Financial Correctness, Offline-First Data Integrity, Quality, UX, and Delivery Discipline | Added sections: Delivery Standards; Development Workflow | Removed sections: None | Deferred TODOs: TODO(RATIFICATION_DATE): original ratification date not provided -->
# Currency Converter Constitution

## Core Principles

### I. Architecture and Separation of Concerns
The project MUST separate the rate source, cache, conversion logic, and UI into distinct modules. The UI and business logic MUST depend on small interfaces, while concrete implementations are composed in a single composition root. This structure is required because it keeps the system testable, replaceable, and resilient to changes in data source or presentation logic.

### II. Reliability and User-Centered Error Handling
The application MUST never crash on network, parsing, or file errors. Every failure MUST be caught, translated into a clear Russian-language message, and shown to the user without exposing internal implementation details. Recovery paths and explicit user guidance are mandatory because trust in a financial tool depends on predictable, understandable behavior.

### III. Financial Correctness Through Decimal Arithmetic
All monetary calculations MUST use Decimal arithmetic rather than floating-point numbers. Conversion results MUST be rounded to 2 decimal places, while rate display values MUST be shown with 4 decimal places. This requirement is non-negotiable because monetary precision and auditability are core product guarantees.

### IV. Offline-First Data Integrity
The last successful source response MUST be cached locally and retained across app restarts. The user MUST always see the date and source of the rate currently in use, even when the network is unavailable. This requirement ensures continuity, traceability, and resilience in the face of connectivity loss.

### V. Quality, UX, and Delivery Discipline
The product MUST provide a polished modern UI with consistent spacing, rounded cards, clear disabled states, and both light and dark themes. All non-UI logic MUST be covered by pytest unit tests with mocked network access, and the full suite MUST run with a single documented command. Documentation MUST be in English, UI text MUST be in Russian, and the team MUST use a separate branch for each stage, meaningful commit messages, and pull requests for merges into main.

## Delivery Standards

The project MUST keep README documentation in English and keep user-visible text in Russian. The release process MUST include a documented test command, accurate setup guidance, and clear descriptions of supported features and assumptions. Any platform or workflow change that affects development, release, or user behavior MUST be reflected in documentation before merge.

## Development Workflow

The team MUST work in separate branches for each stage of the lifecycle, including specification, implementation, and testing. Meaningful commit messages are required so that the history explains the intent of each change. Merges into main MUST occur only through pull requests, with the review process confirming that functionality, tests, and documentation remain aligned with this Constitution.

## Governance

This Constitution defines the non-negotiable operating rules for the currency converter project. Amendments require written rationale, review of the affected principle or section, and approval before they become binding. Versioning follows Semantic Versioning: PATCH for clarifying wording or non-semantic refinements, MINOR for new guidance or materially expanded requirements, and MAJOR for removals or redefinitions of mandatory principles. Compliance review requires each change to confirm that the product remains correct, reliable, user-safe, and testable under the requirements in this Constitution.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): original ratification date not provided | **Last Amended**: 2026-11-04
