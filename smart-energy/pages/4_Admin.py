import streamlit as st
from auth import get_all_users
from data_utils import get_all_readings_df, aggregate_daily
from charts import admin_user_comparison
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Admin", page_icon="🛡️", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in.")
    st.stop()

if st.session_state.user.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()

st.markdown("## 🛡️ Admin Dashboard")
st.markdown("System overview and user management.")

users = get_all_users()
all_df = get_all_readings_df()

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Users", len(users))
k2.metric("Total Readings", len(all_df))
total_kwh = all_df["kwh"].sum() if not all_df.empty else 0
k3.metric("Total kWh Logged", f"{total_kwh:.1f}")
active = all_df["user_id"].nunique() if not all_df.empty else 0
k4.metric("Active Users", active)

st.markdown("---")

# User comparison chart
st.markdown("### 📊 Consumption by User")
if not all_df.empty:
    user_map = {str(u["_id"]): u["username"] for u in users}
    all_df["username"] = all_df["user_id"].map(user_map).fillna("Unknown")
    grouped = all_df.groupby("username")["kwh"].sum().reset_index()
    grouped.columns = ["user_id", "kwh"]
    st.plotly_chart(admin_user_comparison(grouped), use_container_width=True)
else:
    st.info("No readings data available.")

st.markdown("---")

# User table
st.markdown("### 👥 User Management")
if users:
    user_data = []
    for u in users:
        uid = str(u["_id"])
        user_readings = all_df[all_df["user_id"] == uid] if not all_df.empty else pd.DataFrame()
        user_data.append({
            "Username": u["username"],
            "Email": u.get("email", "—"),
            "Role": u.get("role", "user"),
            "Threshold (kWh)": u.get("threshold_kwh", 50),
            "Readings": len(user_readings),
            "Total kWh": round(user_readings["kwh"].sum(), 1) if not user_readings.empty else 0,
            "Joined": u.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d") if hasattr(u.get("created_at", ""), "strftime") else "—",
        })
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True, hide_index=True)
else:
    st.info("No users registered yet.")

st.markdown("---")

# Recent readings
st.markdown("### 📋 Recent Readings (All Users)")
if not all_df.empty:
    display = all_df.copy()
    display["username"] = display["user_id"].map({str(u["_id"]): u["username"] for u in users}).fillna("Unknown")
    display = display.sort_values("timestamp", ascending=False).head(50)
    display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display = display[["timestamp", "username", "kwh", "source"]].reset_index(drop=True)
    display.columns = ["Timestamp", "User", "kWh", "Source"]
    st.dataframe(display, use_container_width=True, hide_index=True)
else:
    st.info("No readings yet.")

st.markdown("---")

# System stats
st.markdown("### ⚙️ System Stats")
s1, s2 = st.columns(2)
with s1:
    st.markdown("**Reading Sources**")
    if not all_df.empty:
        src_counts = all_df["source"].value_counts().reset_index()
        src_counts.columns = ["Source", "Count"]
        st.dataframe(src_counts, hide_index=True)

with s2:
    st.markdown("**Daily Average by User**")
    if not all_df.empty:
        all_df["date"] = all_df["timestamp"].dt.date
        user_daily = all_df.groupby(["user_id", "date"])["kwh"].sum().reset_index()
        user_avg = user_daily.groupby("user_id")["kwh"].mean().reset_index()
        user_avg["username"] = user_avg["user_id"].map({str(u["_id"]): u["username"] for u in users}).fillna("Unknown")
        user_avg = user_avg[["username", "kwh"]].rename(columns={"kwh": "Avg Daily kWh"})
        user_avg["Avg Daily kWh"] = user_avg["Avg Daily kWh"].round(2)
        st.dataframe(user_avg, hide_index=True)
