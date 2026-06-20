import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# LOGIN PROTECTION
# ----------------------------

if st.session_state.get("user") is None:
    st.warning("🔒 Please login to access this page.")
    st.stop()

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Carbon Footprint",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Carbon Footprint Analytics")

st.markdown("""
Estimate the environmental impact of household energy consumption.
Carbon emissions are calculated using standard electricity emission factors.
""")

# ----------------------------
# LOAD DATASET
# ----------------------------

df = pd.read_csv(
    "dataset/household_power_consumption.txt",
    sep=";",
    low_memory=False,
    nrows=50000
)

df = df.replace("?", np.nan)
df = df.dropna()

df["Global_active_power"] = pd.to_numeric(
    df["Global_active_power"]
)

# ----------------------------
# CARBON CALCULATIONS
# ----------------------------

# Approximate conversion:
# 1 kWh ≈ 0.82 kg CO₂

total_energy = df["Global_active_power"].sum()

total_co2 = total_energy * 0.82

trees_required = total_co2 / 21.77

# ----------------------------
# METRICS
# ----------------------------

st.subheader("📊 Carbon Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Energy Consumed",
        f"{total_energy:,.2f} kWh"
    )

with col2:
    st.metric(
        "Estimated CO₂ Emissions",
        f"{total_co2:,.2f} kg"
    )

with col3:
    st.metric(
        "Trees Needed to Offset",
        f"{trees_required:,.0f}"
    )

# ----------------------------
# DAILY CARBON TREND
# ----------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d/%m/%Y"
)

daily_energy = (
    df.groupby("Date")["Global_active_power"]
    .sum()
    .reset_index()
)

daily_energy["CO2"] = (
    daily_energy["Global_active_power"] * 0.82
)

st.subheader("📈 Carbon Emissions Trend")

fig = px.line(
    daily_energy,
    x="Date",
    y="CO2",
    title="Daily Carbon Emissions"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------
# ENERGY VS CO2
# ----------------------------

st.subheader("⚡ Energy vs CO₂")

fig2 = px.scatter(
    daily_energy,
    x="Global_active_power",
    y="CO2",
    title="Energy Consumption vs Carbon Emissions"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ----------------------------
# TOP HIGH EMISSION DAYS
# ----------------------------

st.subheader("🚨 Highest Carbon Emission Days")

top_days = daily_energy.sort_values(
    by="CO2",
    ascending=False
).head(10)

st.dataframe(
    top_days,
    use_container_width=True
)

# ----------------------------
# AI INSIGHTS
# ----------------------------

st.subheader("🧠 Sustainability Insights")

if total_co2 > 10000:

    st.error(
        f"""
High Carbon Impact Detected

Estimated Emissions:
{total_co2:,.0f} kg CO₂

Recommendations:

• Reduce peak-hour consumption

• Use energy-efficient appliances

• Optimize cooling systems

• Monitor high-usage devices
"""
    )

else:

    st.success(
        f"""
Good Energy Efficiency

Estimated Emissions:
{total_co2:,.0f} kg CO₂

Current energy usage appears
to be relatively efficient.
"""
    )

# ----------------------------
# ENVIRONMENTAL FACTS
# ----------------------------

st.subheader("🌍 Environmental Impact")

st.info(
    f"""
Total CO₂ Generated:
{total_co2:,.0f} kg

Trees Required To Offset:
{trees_required:,.0f}

Reducing electricity consumption by 10%
could save approximately:

{total_co2 * 0.10:,.0f} kg CO₂
"""
)