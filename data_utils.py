import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from db import get_readings_col, get_alerts_col, get_users_col
from bson import ObjectId
import random


def add_reading(user_id: str, kwh: float, source: str = "manual"):
    get_readings_col().insert_one({
        "user_id": user_id,
        "kwh": kwh,
        "source": source,
        "timestamp": datetime.utcnow(),
    })


def get_readings_df(user_id: str, days: int = 90) -> pd.DataFrame:
    since = datetime.utcnow() - timedelta(days=days)
    cursor = get_readings_col().find(
        {"user_id": user_id, "timestamp": {"$gte": since}},
        sort=[("timestamp", 1)]
    )
    records = list(cursor)
    if not records:
        return pd.DataFrame(columns=["timestamp", "kwh", "source"])
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[["timestamp", "kwh", "source"]]
    return df


def get_all_readings_df() -> pd.DataFrame:
    cursor = get_readings_col().find({}, sort=[("timestamp", 1)])
    records = list(cursor)
    if not records:
        return pd.DataFrame(columns=["user_id", "timestamp", "kwh", "source"])
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    return df.groupby("date")["kwh"].sum().reset_index()


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["week"] = df["timestamp"].dt.to_period("W").astype(str)
    return df.groupby("week")["kwh"].sum().reset_index()


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    return df.groupby("month")["kwh"].sum().reset_index()


def seed_demo_data(user_id: str, days: int = 60):
    col = get_readings_col()
    if col.find_one({"user_id": user_id}):
        return
    base = datetime.utcnow() - timedelta(days=days)
    records = []
    for i in range(days):
        ts = base + timedelta(days=i)
        kwh = round(random.uniform(20, 80) + 10 * np.sin(i / 7), 2)
        records.append({"user_id": user_id, "kwh": kwh, "source": "demo", "timestamp": ts})
    if records:
        col.insert_many(records)


def check_and_create_alerts(user_id: str, threshold: float):
    df = get_readings_df(user_id, days=1)
    if df.empty:
        return
    total = df["kwh"].sum()
    if total > threshold:
        get_alerts_col().insert_one({
            "user_id": user_id,
            "message": f"Daily usage {total:.1f} kWh exceeded threshold of {threshold:.1f} kWh",
            "kwh": total,
            "threshold": threshold,
            "timestamp": datetime.utcnow(),
            "read": False,
        })


def get_alerts(user_id: str):
    cursor = get_alerts_col().find({"user_id": user_id}, sort=[("timestamp", -1)], limit=20)
    return list(cursor)


def mark_alerts_read(user_id: str):
    get_alerts_col().update_many({"user_id": user_id, "read": False}, {"$set": {"read": True}})
