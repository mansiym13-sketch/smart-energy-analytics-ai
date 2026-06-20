import streamlit as st
from data_utils import (
    get_readings_df, aggregate_daily, aggregate_weekly, aggregate_monthly,
    add_reading, seed_demo_data, check_and_create_alerts, get_alerts, mark_alerts_read
)
from charts import daily_bar_chart, weekly_line_chart, monthly_bar_chart, heatmap_chart
from ml_model import train_and_predict, get_recommendations
from report_utils import build_pdf_report
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="⚡", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in to view the dashboard.")
    st.stop()

user = st.session_state.user
user_id = str(user["_id"])

# Header
col_title, col_alert = st.columns([4, 1])
with col_title:
    st.markdown(f"## ⚡ Energy Dashboard — *{user['username']}*")

# Load data
df = get_readings_df(user_id, days=90)
daily_df = aggregate_daily(df)
weekly_df = aggregate_weekly(df)
monthly_df = aggregate_monthly(df)

threshold = float(user.get("threshold_kwh", 50.0))

# Check alerts
if not df.empty:
    check_and_create_alerts(user_id, threshold)

alerts = get_alerts(user_id)
unread = [a for a in alerts if not a.get("read")]

with col_alert:
    if unread:
        st.error(f"🔔 {len(unread)} Alert(s)")
    else:
        st.success("✅ No Alerts")

# KPI metrics
st.markdown("---")
k1, k2, k3, k4 = st.columns(4)

today_kwh = daily_df["kwh"].iloc[-1] if not daily_df.empty else 0
week_kwh = weekly_df["kwh"].iloc[-1] if not weekly_df.empty else 0
month_kwh = monthly_df["kwh"].iloc[-1] if not monthly_df.empty else 0
avg_kwh = daily_df["kwh"].mean() if not daily_df.empty else 0

k1.metric("Today's Usage", f"{today_kwh:.1f} kWh",
          delta=f"Threshold: {threshold:.0f} kWh",
          delta_color="off")
k2.metric("This Week", f"{week_kwh:.1f} kWh")
k3.metric("This Month", f"{month_kwh:.1f} kWh")
k4.metric("Daily Average", f"{avg_kwh:.1f} kWh")

st.markdown("---")

# Add manual reading
with st.expander("➕ Log Energy Reading"):
    with st.form("add_reading"):
        kwh_val = st.number_input("Energy consumed (kWh)", min_value=0.0, max_value=5000.0, step=0.1, value=30.0)
        submitted = st.form_submit_button("Log Reading")
        if submitted:
            add_reading(user_id, kwh_val)
            st.success(f"Logged {kwh_val} kWh successfully!")
            st.rerun()

# Charts tabs
tab1, tab2, tab3, tab4 = st.tabs(["📅 Daily", "📆 Weekly", "🗓️ Monthly", "🗺️ Heatmap"])

with tab1:
    st.plotly_chart(daily_bar_chart(daily_df, threshold), use_container_width=True)

with tab2:
    st.plotly_chart(weekly_line_chart(weekly_df), use_container_width=True)

with tab3:
    st.plotly_chart(monthly_bar_chart(monthly_df), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_chart(daily_df), use_container_width=True)

# Alerts section
st.markdown("---")
st.markdown("### 🔔 Alerts")
if alerts:
    for a in alerts[:5]:
        color = "🔴" if not a.get("read") else "⚪"
        ts = a["timestamp"].strftime("%Y-%m-%d %H:%M") if hasattr(a["timestamp"], "strftime") else str(a["timestamp"])
        st.markdown(f"{color} `{ts}` — {a['message']}")
    if unread:
        if st.button("Mark all as read"):
            mark_alerts_read(user_id)
            st.rerun()
else:
    st.info("No alerts yet.")

# Threshold setting
st.markdown("---")
st.markdown("### ⚙️ Alert Threshold")
new_threshold = st.slider("Daily threshold (kWh)", 10.0, 200.0, threshold, 1.0)
if st.button("Save Threshold"):
    from auth import update_threshold
    update_threshold(user_id, new_threshold)
    st.session_state.user["threshold_kwh"] = new_threshold
    st.success("Threshold updated!")
    st.rerun()

# Export PDF
st.markdown("---")
st.markdown("### 📄 Export Report")
recommendations = get_recommendations(daily_df, threshold)
if st.button("Generate PDF Report"):
    pdf_bytes = build_pdf_report(
        user["username"], daily_df, weekly_df, monthly_df, recommendations
    )
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name=f"energy_report_{user['username']}.pdf",
        mime="application/pdf"
    )
