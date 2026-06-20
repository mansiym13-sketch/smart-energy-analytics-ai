import streamlit as st
from data_utils import get_readings_df, aggregate_daily
from ml_model import train_and_predict, get_recommendations
from charts import forecast_chart
import pandas as pd

st.set_page_config(page_title="Predictions", page_icon="🔮", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user
user_id = str(user["_id"])
threshold = float(user.get("threshold_kwh", 50.0))

st.markdown("## 🔮 ML Energy Predictions")
st.markdown("Powered by polynomial regression trained on your historical data.")

df = get_readings_df(user_id, days=90)
daily_df = aggregate_daily(df)

if len(daily_df) < 5:
    st.warning("⚠️ Not enough data for predictions. Log at least 5 readings or use demo data from the home page.")
    st.stop()

forecast_days = st.slider("Forecast horizon (days)", 7, 30, 14)

with st.spinner("Training model..."):
    forecast_df, history_df = train_and_predict(daily_df, forecast_days=forecast_days)

st.plotly_chart(forecast_chart(history_df, forecast_df), use_container_width=True)

if not forecast_df.empty:
    st.markdown("### 📊 Forecast Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Predicted Daily", f"{forecast_df['predicted_kwh'].mean():.1f} kWh")
    col2.metric("Peak Predicted Day",
                f"{forecast_df.loc[forecast_df['predicted_kwh'].idxmax(), 'date'].strftime('%b %d')} — {forecast_df['predicted_kwh'].max():.1f} kWh")
    days_over = (forecast_df["predicted_kwh"] > threshold).sum()
    col3.metric("Days Exceeding Threshold", f"{days_over} / {forecast_days}")

    st.markdown("### 📋 Forecast Table")
    display_df = forecast_df.copy()
    display_df["date"] = display_df["date"].astype(str)
    display_df["predicted_kwh"] = display_df["predicted_kwh"].round(2)
    display_df["lower"] = display_df["lower"].round(2)
    display_df["upper"] = display_df["upper"].round(2)
    display_df.columns = ["Date", "Predicted kWh", "Lower Bound", "Upper Bound"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🌿 Energy Saving Recommendations")

recs = get_recommendations(daily_df, threshold)
for rec in recs:
    st.markdown(f"- {rec}")
