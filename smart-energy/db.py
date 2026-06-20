import os
import ssl
import pymongo
import certifi
from datetime import datetime

MONGODB_URI = "mongodb+srv://mansi:Mansi12345@cluster0.nf5pcbp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

_client = None

def get_client():
    global _client
    if _client is None:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        _client = pymongo.MongoClient(
            MONGODB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
    return _client

def get_db():
    client = get_client()
    return client["smart_energy"]

def get_users_col():
    return get_db()["users"]

def get_readings_col():
    return get_db()["energy_readings"]

def get_alerts_col():
    return get_db()["alerts"]

def get_settings_col():
    return get_db()["settings"]

def ensure_indexes():
    try:
        get_users_col().create_index("username", unique=True)
        get_readings_col().create_index([("user_id", 1), ("timestamp", -1)])
        get_alerts_col().create_index([("user_id", 1), ("timestamp", -1)])
    except Exception:
        pass
