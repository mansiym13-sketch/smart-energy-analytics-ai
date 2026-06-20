import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
    df["day_of_year"] = pd.to_datetime(df["date"]).dt.dayofyear
    df["day_index"] = range(len(df))
    return df


def train_and_predict(daily_df: pd.DataFrame, forecast_days: int = 14):
    if daily_df.empty or len(daily_df) < 5:
        return pd.DataFrame(), pd.DataFrame()

    df = prepare_features(daily_df)
    X = df[["day_index", "day_of_week", "day_of_year"]].values
    y = df["kwh"].values

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )
    model.fit(X, y)

    in_sample_pred = model.predict(X)
    residuals = y - in_sample_pred
    std = np.std(residuals)

    last_date = pd.to_datetime(daily_df["date"].iloc[-1])
    last_idx = df["day_index"].iloc[-1]

    future_dates = [last_date + timedelta(days=i + 1) for i in range(forecast_days)]
    future_df = pd.DataFrame({"date": future_dates})
    future_df["day_of_week"] = future_df["date"].dt.dayofweek
    future_df["day_of_year"] = future_df["date"].dt.dayofyear
    future_df["day_index"] = [last_idx + i + 1 for i in range(forecast_days)]

    X_future = future_df[["day_index", "day_of_week", "day_of_year"]].values
    preds = model.predict(X_future)
    preds = np.clip(preds, 0, None)

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "predicted_kwh": preds,
        "lower": np.clip(preds - 1.5 * std, 0, None),
        "upper": preds + 1.5 * std,
    })

    history_pred_df = pd.DataFrame({
        "date": pd.to_datetime(daily_df["date"]),
        "actual_kwh": y,
        "fitted_kwh": in_sample_pred,
    })

    return forecast_df, history_pred_df


def get_recommendations(daily_df: pd.DataFrame, threshold: float) -> list[str]:

    if daily_df.empty:
        return [
            "Start logging energy data to receive personalized recommendations."
        ]

    avg = daily_df["kwh"].mean()

    recent = (
        daily_df.tail(7)["kwh"].mean()
        if len(daily_df) >= 7
        else avg
    )

    trend = recent - avg

    recs = []

    # -----------------------------
    # Threshold Analysis
    # -----------------------------

    if recent > threshold:

        recs.append(
            f"⚠️ Recent average usage ({recent:.1f} kWh/day) exceeds your configured threshold ({threshold:.1f} kWh/day)."
        )

    # -----------------------------
    # Consumption Trend Analysis
    # -----------------------------

    if trend > 5:

        recs.append(
            "📈 Energy consumption is increasing rapidly. Investigate high-power appliances and reduce unnecessary usage."
        )

    elif trend < -5:

        recs.append(
            "✅ Energy usage is decreasing. Current conservation efforts appear effective."
        )

    # -----------------------------
    # Carbon Footprint Estimation
    # -----------------------------

    estimated_co2 = avg * 30 * 0.82

    if estimated_co2 > 1000:

        recs.append(
            f"🌱 Estimated monthly carbon emissions are approximately {estimated_co2:.0f} kg CO₂. Consider reducing HVAC and appliance usage."
        )

    # -----------------------------
    # High Consumption Detection
    # -----------------------------

    if avg > 60:

        recs.append(
            "💡 Average energy usage is significantly above normal. Switching to LED lighting and energy-efficient appliances could reduce consumption."
        )

    elif avg > 40:

        recs.append(
            "🌡️ Heating and cooling systems appear to contribute significantly to consumption. Adjust thermostat settings to improve efficiency."
        )

    # -----------------------------
    # Peak Day Detection
    # -----------------------------

    max_day = daily_df["kwh"].max()

    if max_day > avg * 1.5:

        recs.append(
            f"⚠️ Significant energy spike detected ({max_day:.1f} kWh). Review appliance activity on unusually high-consumption days."
        )

    # -----------------------------
    # Weekend Analysis
    # -----------------------------

    if len(daily_df) >= 14:

        tmp = daily_df.copy()

        tmp["dow"] = pd.to_datetime(
            tmp["date"]
        ).dt.dayofweek

        weekend_avg = tmp[
            tmp["dow"] >= 5
        ]["kwh"].mean()

        weekday_avg = tmp[
            tmp["dow"] < 5
        ]["kwh"].mean()

        if weekend_avg > weekday_avg * 1.2:

            recs.append(
                "📅 Weekend consumption is noticeably higher than weekday consumption. Consider distributing energy-intensive activities throughout the week."
            )

    # -----------------------------
    # Smart Recommendations
    # -----------------------------

    recs.append(
        "🔌 Eliminate standby power by using smart power strips for televisions, gaming systems, and chargers."
    )

    recs.append(
        "🌞 Schedule washing machines, dishwashers, and other heavy appliances during off-peak hours to reduce energy costs."
    )

    recs.append(
        "☀️ Renewable energy solutions such as rooftop solar panels can significantly offset long-term electricity consumption."
    )

    return recs