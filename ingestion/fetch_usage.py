"""
Provider-agnostic electricity ingestion entry point.

Live supplier integration should be added as an adapter and should return
a DataFrame with at least:

    timestamp, kwh

Credentials must come from environment variables or a secret manager.
Never hard-code account credentials in this repository.
"""

from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def normalise_usage(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "kwh"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="raise")
    out["kwh"] = pd.to_numeric(out["kwh"], errors="raise")

    if out["timestamp"].duplicated().any():
        raise ValueError("Duplicate interval timestamps found")

    if (out["kwh"] < 0).any():
        raise ValueError("Negative electricity usage found")

    return out.sort_values("timestamp").reset_index(drop=True)


def save_raw(df: pd.DataFrame, filename: str = "interval_usage.csv") -> Path:
    target = RAW_DIR / filename
    normalise_usage(df).to_csv(target, index=False)
    return target


if __name__ == "__main__":
    raise SystemExit(
        "No live supplier adapter configured yet. "
        "Use scripts/generate_demo_data.py for the public demo pipeline."
    )
