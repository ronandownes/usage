# Data Model

## Interval usage

Grain: one electricity reading per interval.

| Field | Meaning |
|---|---|
| timestamp | beginning/end of supplier interval |
| kwh | electricity consumed in the interval |
| source | provider or synthetic demo source |

## Daily KPI mart

Grain: one row per calendar day.

Measures include:

- daily kWh
- peak interval kWh
- overnight kWh
- interval count
- data completeness
- 7-day rolling mean
- 30-day rolling mean
- previous-day percentage change
- same-weekday baseline
- anomaly z-score

## Design principle

Raw ingestion is separated from transformation and presentation so that a live provider integration can be replaced without rewriting the analytics or dashboard.
