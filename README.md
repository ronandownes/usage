# Household Electricity Analytics

A production-style analytics project for household electricity consumption.

## Purpose

This repository demonstrates an end-to-end analytics workflow:

- automated ingestion of interval electricity readings
- validation and data-quality checks
- time-series transformation
- KPI calculation
- anomaly detection
- forecasting-ready datasets
- interactive self-service dashboard
- scheduled GitHub Actions pipeline

The public repository contains code and synthetic/demo data only. Private household readings and credentials should never be committed.

## Architecture

```
Provider / CSV export
        |
        v
 ingestion/fetch_usage.py
        |
        v
 data/raw/
        |
        v
 analytics/build_marts.py
        |
        +--> daily KPIs
        +--> hourly profiles
        +--> rolling averages
        +--> anomaly flags
        |
        v
 dashboard/app.py
```

## Core KPIs

- daily kWh
- 7-day and 30-day rolling averages
- previous-day comparison
- same-weekday baseline
- peak half-hour demand
- overnight baseload
- day/night usage split
- anomaly score
- data completeness

## Run locally

```bash
pip install -r requirements.txt
python scripts/generate_demo_data.py
python analytics/build_marts.py
streamlit run dashboard/app.py
```

## Security

Do not commit:

- supplier passwords
- API tokens
- MPRN/account identifiers
- raw private household interval readings

Live credentials should be supplied through environment variables or GitHub Actions Secrets.

## Portfolio relevance

The project is designed to demonstrate SQL/data-modelling thinking, time-series analytics, dashboarding, automated pipelines, data quality and self-service analytics.
