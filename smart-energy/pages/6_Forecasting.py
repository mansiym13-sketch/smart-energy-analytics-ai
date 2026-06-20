import streamlit as st
import plotly.express as px
from forecast_utils import get_forecast

if not st.session_state.get("authenticated", False):
    st.warning("🔒 Please login to access this page.")
    st.stop()

st.title("🔮 Energy Forecasting")

forecast = get_forecast(30)

fig = px.line(
    forecast,
    x="ds",
    y="yhat",
    title="Next 30 Days Energy Forecast"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    forecast.tail(30),
    use_container_width=True
)