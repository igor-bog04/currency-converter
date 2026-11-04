# Data Model: Desktop Currency Converter

## Currency

Represents a selectable currency and, when available, its value relative to MDL.

| Field | Meaning | Validation |
|---|---|---|
| `code` | ISO-like code from BNM, or `MDL` | Non-empty; unique within a rate snapshot |
| `name` | Display name from BNM, or `Moldovan Leu` for MDL | Non-empty |
| `rate_to_mdl` | MDL value of one currency unit | Finite positive Decimal; MDL is exactly 1 |

Currencies are identified by `code`. A snapshot always includes MDL, even though BNM omits it.

## Rate Snapshot

An immutable set of rates successfully obtained from BNM for a single effective date.

| Field | Meaning | Validation |
|---|---|---|
| `rate_date` | Date BNM rates apply to | Valid calendar date |
| `source` | Official source identifier | `BNM` |
| `currencies` | Currency code to currency data mapping | At least one usable non-MDL currency and MDL |

For each BNM item, `rate_to_mdl = Value / Nominal`, with both values parsed as Decimal. A fully
invalid or structurally unexpected document is unavailable; invalid monetary values, missing
required fields, or duplicate codes must not be used in a conversion.

The local cache contains exactly one last-successful snapshot. Decimal values are serialized as
decimal strings and reconstructed from strings, never through binary floating point. The JSON file
is replaced atomically so a failed write cannot leave a partial cache file.

## Conversion Request

| Field | Meaning | Validation |
|---|---|---|
| `amount` | Positive amount entered by the user | Finite Decimal, greater than zero, standard decimal notation, at most 2 fractional digits |
| `source_code` | Currency the user converts from | Present in the effective snapshot |
| `target_code` | Currency the user converts to | Present in the effective snapshot |
| `requested_date` | Date selected in the UI | Valid date; defaults to today's local date |

The input accepts either `.` or `,` as the decimal separator. Invalid input is rejected before
conversion and receives an adjacent Russian-language message.

## Conversion Result

| Field | Meaning |
|---|---|
| `converted_amount` | Amount rounded to 2 decimal places |
| `source_to_target_rate` | Full-precision rate used for one source unit, displayed to 4 places |
| `target_to_source_rate` | Independently calculated reciprocal, displayed to 4 places |
| `snapshot_date` | Effective rate date, which can differ from the requested date |
| `source` | `BNM`, with cached/fallback status communicated separately |

For source rate `rA` and target rate `rB`, both measured in MDL per unit, the conversion is
`amount * rA / rB`. If both currencies are the same, both rates are 1 and the result equals the
input amount.

## State and Recovery

The rate provider transitions through:

1. **Loading online rates** for the selected date and, if necessary, earlier dates.
2. **Rates available** when a valid snapshot is found; persist it as the last successful snapshot.
3. **Online source unavailable** after network, timeout, parsing, or data validation failure.
4. **Cached rates offered** when an online source failure occurs and a last-successful snapshot
   can be loaded; the user may accept or decline using that snapshot.
5. **Unavailable** when there are no usable online or cached rates; show a Russian-language
   message and keep the application responsive.

Only a fully validated online snapshot replaces the cache. A failed cache read or write is reported
to the user; it must not crash the application.
