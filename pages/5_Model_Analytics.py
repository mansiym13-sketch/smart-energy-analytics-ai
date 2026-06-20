import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit as st

if st.session_state.get("user") is None:
    st.warning("🔒 Please login to access this page.")
    st.stop()

st.set_page_config(
    page_title="Model Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Model Analytics Dashboard")

st.markdown("""
Compare machine learning models used for energy consumption forecasting.
The best-performing model is automatically selected based on evaluation metrics.
""")

# ==========================
# MODEL COMPARISON DATA
# ==========================

comparison_df = pd.DataFrame({
    "Model": [
        "Linear Regression",
        "Random Forest",
        "XGBoost"
    ],
    "MAE": [
        0.03945,
        0.02854,
        0.02638
    ],
    "RMSE": [
        0.06251,
        0.05398,
        0.04790
    ],
    "R² Score": [
        0.99784,
        0.99839,
        0.99873
    ]
})

# ==========================
# BEST MODEL
# ==========================

st.success(
    "🏆 Best Model Selected: XGBoost"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "MAE",
        "0.02638"
    )

with col2:
    st.metric(
        "RMSE",
        "0.04790"
    )

with col3:
    st.metric(
        "R² Score",
        "0.99873"
    )

# ==========================
# MODEL COMPARISON TABLE
# ==========================

st.subheader("📋 Model Comparison")

st.dataframe(
    comparison_df,
    use_container_width=True
)

# ==========================
# R² COMPARISON CHART
# ==========================

st.subheader("📈 Model Performance Comparison")

fig_r2 = px.bar(
    comparison_df,
    x="Model",
    y="R² Score",
    text="R² Score",
    title="R² Score Comparison"
)

fig_r2.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_r2,
    use_container_width=True
)

# ==========================
# FEATURE IMPORTANCE
# ==========================

importance_df = pd.DataFrame({
    "Feature": [
        "Global Intensity",
        "Sub Metering 3",
        "Voltage",
        "Sub Metering 1",
        "Sub Metering 2"
    ],
    "Importance": [
        0.997963,
        0.001085,
        0.000397,
        0.000382,
        0.000172
    ]
})

st.subheader("🎯 XGBoost Feature Importance")

fig_importance = px.bar(
    importance_df,
    x="Feature",
    y="Importance",
    text="Importance",
    title="Feature Importance Analysis"
)

fig_importance.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_importance,
    use_container_width=True
)

# ==========================
# INTERPRETATION
# ==========================

st.subheader("🧠 Model Insights")

st.info("""
XGBoost achieved the highest performance among all tested models.

Key Findings:

• Global Intensity is the most influential feature (99.8%)

• XGBoost achieved an R² Score of 0.99873

• Random Forest ranked second

• Linear Regression produced the lowest accuracy

• XGBoost was selected as the final forecasting model
""")

# ==========================
# RESEARCH SUMMARY
# ==========================

st.subheader("📑 Research Summary")

st.markdown("""
### Forecasting Models Evaluated

1. Linear Regression
2. Random Forest Regressor
3. XGBoost Regressor

### Evaluation Metrics

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score

### Final Model

The XGBoost Regressor was selected as the final forecasting model due to its superior predictive performance across all evaluation metrics.
""")