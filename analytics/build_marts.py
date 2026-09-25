from pathlib import Path
import numpy as np
import pandas as pd

DEMO = Path("data/demo/interval_usage.csv")
RAW = Path("data/raw/interval_usage.csv")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


def load_usage() -> pd.DataFrame:
    source = RAW if RAW.exists() else DEMO
    if not source.exists():
        raise FileNotFoundError(
            "No interval data found. Run scripts/generate_demo_data.py first."
        )

    df = pd.read_csv(source, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["timestamp"].dt.dayofweek >= 5
    df["is_overnight"] = df["timestamp"].dt.hour.between(0, 5)
    return df


def build_daily(df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        df.groupby("date", as_index=False)
          .agg(
              kwh=("kwh", "sum"),
              peak_interval_kwh=("kwh", "max"),
              intervals=("kwh", "size"),
              overnight_kwh=("kwh", lambda s: s[df.loc[s.index, "is_overnight"]].sum()),
          )
    )

    daily["date"] = pd.to_datetime(daily["date"])
    daily["data_completeness_pct"] = (daily["intervals"] / 48 * 100).clip(upper=100)
    daily["rolling_7d_kwh"] = daily["kwh"].rolling(7, min_periods=1).mean()
    daily["rolling_30d_kwh"] = daily["kwh"].rolling(30, min_periods=1).mean()
    daily["previous_day_pct"] = daily["kwh"].pct_change() * 100

    # Baseline against the previous four matching weekdays.
    weekday_num = daily["date"].dt.dayofweek
    daily["same_weekday_baseline_kwh"] = (
        daily.assign(weekday_num=weekday_num)
             .groupby("weekday_num")["kwh"]
             .transform(lambda x: x.shift(1).rolling(4, min_periods=1).mean())
    )

    baseline = daily["rolling_30d_kwh"]
    std = daily["kwh"].rolling(30, min_periods=7).std()
    daily["anomaly_z"] = (daily["kwh"] - baseline) / std.replace(0, np.nan)
    daily["is_anomaly"] = daily["anomaly_z"].abs() >= 2.5

    return daily


def build_hourly_profile(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["weekday", "hour"], as_index=False)
          .agg(avg_kwh=("kwh", "mean"), median_kwh=("kwh", "median"))
    )


def main() -> None:
    df = load_usage()
    daily = build_daily(df)
    hourly = build_hourly_profile(df)

    df.to_parquet(OUT / "interval_usage.parquet", index=False)
    daily.to_parquet(OUT / "daily_kpis.parquet", index=False)
    hourly.to_parquet(OUT / "hourly_profile.parquet", index=False)

    print(f"Built marts from {len(df):,} interval readings.")
    print(f"Daily rows: {len(daily):,}")


if __name__ == "__main__":
    main()
