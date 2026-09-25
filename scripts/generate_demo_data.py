from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/demo")
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)
start = pd.Timestamp.today().normalize() - pd.Timedelta(days=365)
timestamps = pd.date_range(start=start, periods=365 * 48, freq="30min")

hour = timestamps.hour + timestamps.minute / 60
weekday = timestamps.dayofweek

# Synthetic household pattern: baseload + morning/evening peaks + seasonal effect.
morning = 0.28 * np.exp(-0.5 * ((hour - 7.5) / 1.2) ** 2)
evening = 0.55 * np.exp(-0.5 * ((hour - 18.5) / 2.0) ** 2)
weekend = np.where(weekday >= 5, 0.07, 0.0)
day_of_year = timestamps.dayofyear.to_numpy()
seasonal = 0.12 * (1 + np.cos(2 * np.pi * (day_of_year - 10) / 365))
noise = rng.normal(0, 0.045, len(timestamps))

kwh = np.clip(0.09 + morning + evening + weekend + seasonal + noise, 0.03, None)

df = pd.DataFrame({
    "timestamp": timestamps,
    "kwh": np.round(kwh, 4),
    "source": "synthetic_demo"
})

df.to_csv(OUT / "interval_usage.csv", index=False)
print(f"Wrote {len(df):,} demo readings to {OUT / 'interval_usage.csv'}")
