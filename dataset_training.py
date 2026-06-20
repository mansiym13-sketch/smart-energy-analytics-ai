import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor


# Load Dataset
df = pd.read_csv(
    "dataset/household_power_consumption.txt",
    sep=";",
    low_memory=False,
    nrows=50000
)

# Keep useful columns
df = df[
    [
        "Global_active_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]
]

# Replace missing values
df = df.replace("?", np.nan)

# Drop missing values
df = df.dropna()

# Convert all columns to numeric
for col in df.columns:
    df[col] = pd.to_numeric(df[col])

# Features
X = df[
    [
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]
]

# Target
y = df["Global_active_power"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


def evaluate_model(name, model):

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            pred
        )
    )

    r2 = r2_score(
        y_test,
        pred
    )

    return {
        "Model": name,
        "MAE": round(mae, 5),
        "RMSE": round(rmse, 5),
        "R2": round(r2, 5)
    }


models = [

    (
        "Linear Regression",
        LinearRegression()
    ),

    (
        "Random Forest",
        RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
    ),

    (
        "XGBoost",
        XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    )

]

results = []

for name, model in models:

    results.append(
        evaluate_model(
            name,
            model
        )
    )

results_df = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print("=" * 50)

print(results_df)

best_model = results_df.sort_values(
    by="R2",
    ascending=False
).iloc[0]

print("\nBEST MODEL")
print("=" * 50)

print(best_model)


best_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)

best_model.fit(X_train, y_train)

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": best_model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE")
print("=" * 50)
print(importance)