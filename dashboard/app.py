from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Electricity Usage", layout="wide")

DAILY = Path("data/processed/daily_kpis.parquet")
INTERVAL = Path("data/processed/interval_usage.parquet")

st.title("Household Electricity Analytics")
st.caption("Automated time-series analytics pipeline • public demo data by default")

if not DAILY.exists() or not INTERVAL.exists():
    st.error("Processed data not found. Run the demo generator and analytics pipeline first.")
    st.stop()

daily = pd.read_parquet(DAILY).sort_values("date")
interval = pd.read_parquet(INTERVAL).sort_values("timestamp")

latest = daily.iloc[-1]
previous = daily.iloc[-2] if len(daily) > 1 else latest
delta = latest["kwh"] - previous["kwh"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest day", f"{latest['kwh']:.1f} kWh", f"{delta:+.1f} kWh")
c2.metric("7-day average", f"{latest['rolling_7d_kwh']:.1f} kWh")
c3.metric("30-day average", f"{latest['rolling_30d_kwh']:.1f} kWh")
c4.metric("Data completeness", f"{latest['data_completeness_pct']:.0f}%")

st.subheader("Daily consumption")
fig = px.line(
    daily,
    x="date",
    y=["kwh", "rolling_7d_kwh", "rolling_30d_kwh"],
    labels={"value": "kWh", "date": "", "variable": "Series"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("24-hour × day usage heatmap")
heat = interval.copy()
heat["date"] = heat["timestamp"].dt.date
heat["half_hour"] = (
    heat["timestamp"].dt.hour.astype(str).str.zfill(2)
    + ":"
    + heat["timestamp"].dt.minute.astype(str).str.zfill(2)
)
pivot = heat.pivot_table(index="date", columns="half_hour", values="kwh", aggfunc="sum")
heat_fig = px.imshow(
    pivot.tail(60),
    aspect="auto",
    labels={"x": "Time of day", "y": "Date", "color": "kWh"},
)
st.plotly_chart(heat_fig, use_container_width=True)

st.subheader("Potential anomalies")
anomalies = daily[daily["is_anomaly"]].copy()
if anomalies.empty:
    st.info("No high-confidence anomalies detected in the selected history.")
else:
    st.dataframe(
        anomalies[["date", "kwh", "rolling_30d_kwh", "anomaly_z"]],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Private deployments can replace the synthetic source with supplier interval data "
    "without changing the analytics or dashboard layers."
)
