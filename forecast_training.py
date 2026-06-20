import pandas as pd
from prophet import Prophet
import joblib

# Dataset
df = pd.read_csv(
    "dataset/household_power_consumption.txt",
    sep=";",
    low_memory=False
)

# Clean data
df = df[df["Global_active_power"] != "?"]

df["Global_active_power"] = pd.to_numeric(
    df["Global_active_power"],
    errors="coerce"
)

# Create datetime
df["datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"],
    dayfirst=True
)

# Aggregate daily consumption
daily = (
    df.groupby(df["datetime"].dt.date)
    ["Global_active_power"]
    .mean()
    .reset_index()
)

daily.columns = ["ds", "y"]

# Train Prophet
model = Prophet(
    daily_seasonality=True,
    yearly_seasonality=True
)

model.fit(daily)

# Save model
joblib.dump(model, "forecast_model.pkl")

print("Forecast model trained successfully!")