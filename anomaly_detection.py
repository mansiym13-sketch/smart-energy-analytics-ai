import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest


def detect_anomalies():

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

    return df, anomalies


if __name__ == "__main__":

    df, anomalies = detect_anomalies()

    print("\nANOMALIES FOUND")
    print("=" * 50)

    print(
        f"Total anomalies detected: {len(anomalies)}"
    )

    print(
        anomalies[
            [
                "Date",
                "Time",
                "Global_active_power"
            ]
        ].head(10)
    )