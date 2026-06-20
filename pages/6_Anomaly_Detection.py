import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px

from sklearn.ensemble import IsolationForest

import streamlit as st

if st.session_state.get("user") is None:
    st.warning("🔒 Please login to access this page.")
    st.stop()

st.set_page_config(
    page_title="Anomaly Detection",
    page_icon="⚠",
    layout="wide"
)


st.title("⚠ AI Anomaly Detection Dashboard")

st.markdown("""
Detect unusual energy consumption patterns using Isolation Forest.
The system automatically identifies abnormal spikes in energy usage.
""")

# ==========================
# LOAD DATASET
# ==========================

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

# ==========================
# ISOLATION FOREST
# ==========================

iso = IsolationForest(
    contamination=0.02,
    random_state=42
)

df["anomaly"] = iso.fit_predict(
    df[["Global_active_power"]]
)

anomalies = df[
    df["anomaly"] == -1
]

normal = df[
    df["anomaly"] == 1
]

# ==========================
# METRICS
# ==========================

st.subheader("📊 Detection Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Records",
        len(df)
    )

with col2:
    st.metric(
        "Anomalies Detected",
        len(anomalies)
    )

with col3:
    st.metric(
        "Detection Rate",
        f"{(len(anomalies)/len(df))*100:.2f}%"
    )

# ==========================
# HIGHEST SPIKE
# ==========================

highest_spike = anomalies[
    "Global_active_power"
].max()

st.error(
    f"⚠ Highest Energy Spike Detected: {highest_spike:.2f} kW"
)

# ==========================
# SCATTER PLOT
# ==========================

plot_df = df.reset_index()

fig = px.scatter(
    plot_df,
    x=plot_df.index,
    y="Global_active_power",
    color="anomaly",
    title="Energy Usage Anomaly Detection"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================
# ANOMALY TABLE
# ==========================

st.subheader("🚨 Detected Anomalies")

st.dataframe(
    anomalies[
        [
            "Date",
            "Time",
            "Global_active_power"
        ]
    ].head(50),
    use_container_width=True
)

# ==========================
# INSIGHTS
# ==========================

st.subheader("🧠 AI Insights")

st.info(
    """
Isolation Forest detected unusual energy consumption patterns.

Possible Causes:

• Faulty electrical equipment

• Air conditioner overload

• High power appliance usage

• Unexpected consumption spikes

• Meter irregularities
"""
)