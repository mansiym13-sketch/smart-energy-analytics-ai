import bcrypt
import streamlit as st
from db import get_users_col, ensure_indexes
from datetime import datetime


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(username: str, password: str, email: str, role: str = "user") -> tuple[bool, str]:
    ensure_indexes()
    col = get_users_col()
    if col.find_one({"username": username}):
        return False, "Username already exists."
    if col.find_one({"email": email}):
        return False, "Email already registered."
    col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.utcnow(),
        "threshold_kwh": 50.0,
    })
    return True, "Registered successfully!"


def login_user(username: str, password: str) -> tuple[bool, dict | None, str]:
    col = get_users_col()
    user = col.find_one({"username": username})
    if not user:
        return False, None, "User not found."
    if not verify_password(password, user["password_hash"]):
        return False, None, "Incorrect password."
    return True, user, "Login successful!"


def get_all_users():
    return list(get_users_col().find({}, {"password_hash": 0}))


def update_threshold(user_id, threshold: float):
    from bson import ObjectId
    get_users_col().update_one({"_id": ObjectId(user_id)}, {"$set": {"threshold_kwh": threshold}})
