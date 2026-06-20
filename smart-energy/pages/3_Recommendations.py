import streamlit as st
from data_utils import get_readings_df, aggregate_daily
from ml_model import get_recommendations


st.set_page_config(page_title="Recommendations", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user
user_id = str(user["_id"])
threshold = float(user.get("threshold_kwh", 50.0))

st.markdown("## 🌿 Energy Saving Recommendations")
st.markdown("Personalized tips based on your usage patterns.")

df = get_readings_df(user_id, days=90)
daily_df = aggregate_daily(df)

if daily_df.empty:
    st.info("Log some energy readings first to receive personalized recommendations.")
else:
    avg = daily_df["kwh"].mean()
    recent7 = daily_df.tail(7)["kwh"].mean() if len(daily_df) >= 7 else avg

    col1, col2, col3 = st.columns(3)
    col1.metric("7-Day Average", f"{recent7:.1f} kWh/day")
    col2.metric("Overall Average", f"{avg:.1f} kWh/day")
    trend = recent7 - avg
    col3.metric("Trend vs Average", f"{trend:+.1f} kWh", delta_color="inverse")

st.markdown("---")

recs = get_recommendations(daily_df, threshold)

categories = {
    "⚠️ Urgent": [],
    "📈 Trends": [],
    "💡 Appliances": [],
    "🌿 Habits": [],
    "☀️ Renewable": [],
}

for rec in recs:
    if rec.startswith("⚠️"):
        categories["⚠️ Urgent"].append(rec)
    elif rec.startswith("📈"):
        categories["📈 Trends"].append(rec)
    elif any(rec.startswith(e) for e in ["💡", "🌡️", "🔌"]):
        categories["💡 Appliances"].append(rec)
    elif any(rec.startswith(e) for e in ["🌞", "📅", "🌿"]):
        categories["🌿 Habits"].append(rec)
    elif rec.startswith("☀️"):
        categories["☀️ Renewable"].append(rec)
    else:
        categories["🌿 Habits"].append(rec)

for cat, items in categories.items():
    if items:
        st.markdown(f"### {cat}")
        for item in items:
            st.info(item)

st.markdown("---")
st.markdown("### 📚 General Best Practices")

tips = [
    ("Smart Thermostats", "Programmable or smart thermostats can reduce heating and cooling costs by 10–15%."),
    ("Energy Star Appliances", "Replacing old appliances with Energy Star certified models saves 10–50% on their energy use."),
    ("Insulation", "Proper home insulation reduces the need for heating and cooling by up to 40%."),
    ("Natural Light", "Maximize natural lighting during the day to reduce artificial lighting costs."),
    ("Phantom Loads", "Use smart power strips to eliminate standby power from electronics when not in use."),
    ("Time-of-Use Pricing", "Run high-energy appliances during off-peak hours to take advantage of lower electricity rates."),
    ("Solar Options", "Even small solar installations can meaningfully offset grid electricity consumption."),
    ("Water Heating", "Lowering your water heater temperature from 140°F to 120°F saves up to 10% on water heating costs."),
]

cols = st.columns(2)
for i, (title, tip) in enumerate(tips):
    with cols[i % 2]:
        st.markdown(f"**{title}**")
        st.caption(tip)
        st.markdown("")
