import streamlit as st
from auth import register_user, login_user
from data_utils import seed_demo_data

st.set_page_config(
    page_title="Smart Energy Monitor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for green sustainability theme
st.markdown("""
<style>
/* ── Dark background for entire app ── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
.main, .block-container,
[data-testid="stVerticalBlock"] {
    background-color: #0A0A0A !important;
}
[data-testid="stHeader"] {
    background-color: #0A0A0A !important;
    border-bottom: 1px solid #1A2A1A;
}
/* Force text colour on main content */
[data-testid="stMain"] p,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] label,
[data-testid="stMain"] span,
[data-testid="stMain"] div {
    color: #E8F5E9;
}
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1F0A 0%, #0D2B0D 100%) !important;
    border-right: 1px solid #2E7D32;
}
[data-testid="stSidebar"] * {
    color: #E8F5E9 !important;
}
/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2E7D32, #388E3C);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #388E3C, #43A047);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(46,125,50,0.4);
}
/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div,
.stSelectbox div[data-baseweb="select"] {
    background-color: #1A2A1A !important;
    color: #E8F5E9 !important;
    border-color: #2E7D32 !important;
}
/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #1A2A1A;
    border: 1px solid #2E7D32;
    border-radius: 10px;
    padding: 12px;
}
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0A1F0A;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] { color: #A5D6A7; }
.stTabs [aria-selected="true"] {
    background: #2E7D32;
    border-radius: 6px;
    color: white !important;
}
/* ── Tables / expanders ── */
.stDataFrame { border: 1px solid #2E7D32; border-radius: 8px; }
div[data-testid="stExpander"] {
    border: 1px solid #2E7D32;
    border-radius: 8px;
    background: #0D1F0D;
}
/* ── Alerts / info boxes ── */
[data-testid="stAlert"] {
    background-color: #0D2B0D !important;
    border-color: #2E7D32 !important;
}
</style>
""", unsafe_allow_html=True)

# Session state init
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## ⚡ Smart Energy")
    st.markdown("*Monitor · Predict · Save*")
    st.markdown("---")

    if st.session_state.user:
        u = st.session_state.user
        st.markdown(f"👤 **{u['username']}**")
        st.markdown(f"🏷️ Role: `{u.get('role', 'user')}`")
        st.markdown("---")
        st.markdown("**Navigation**")
        st.markdown("- 📊 Dashboard")
        st.markdown("- 🔮 Predictions")
        st.markdown("- 🌿 Recommendations")
        if u.get("role") == "admin":
            st.markdown("- 🛡️ Admin")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        st.markdown("Please log in to get started.")

# ---- Main Content ----
if st.session_state.user is None:
    # Hero
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px 0;">
        <div style="font-size: 4rem;">⚡</div>
        <h1 style="color:#2E7D32; font-size:2.5rem; margin:0;">Smart Energy Monitor</h1>
        <p style="color:#A5D6A7; font-size:1.1rem; margin-top:8px;">
            Monitor consumption · Predict the future · Save the planet
        </p>
    </div>
    """, unsafe_allow_html=True)

    feat_cols = st.columns(4)
    features = [
        ("Real-time Dashboard", "Daily, weekly & monthly charts with threshold alerts"),
        ("ML Predictions", "14-day forecast powered by scikit-learn"),
        ("Eco Tips", "Personalised energy saving recommendations"),
        ("PDF Reports", "Export professional reports with one click"),
    ]
    for col, (title, desc) in zip(feat_cols, features):
        with col:
            st.markdown(f"""
            <div style="background:#1A2A1A; border:1px solid #2E7D32; border-radius:10px;
                        padding:16px; text-align:center;">
                <div style="color:#66BB6A; font-weight:700; font-size:1rem; margin-bottom:6px;">{title}</div>
                <div style="color:#A5D6A7; font-size:0.85rem; line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Auth tabs
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    with login_tab:
        st.markdown("### Welcome back")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, user, msg = login_user(username, password)
                    if ok:
                        st.session_state.user = user
                        user_id = str(user["_id"])
                        seed_demo_data(user_id)
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with register_tab:
        st.markdown("### Create an account")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_user")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            new_password2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
            role_choice = st.selectbox("Account type", ["user", "admin"])
            submitted = st.form_submit_button("Register", use_container_width=True)
            if submitted:
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != new_password2:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = register_user(new_username, new_password, new_email, role=role_choice)
                    if ok:
                        st.success(msg + " Please log in.")
                    else:
                        st.error(msg)

else:
    # Logged-in home
    user = st.session_state.user
    st.markdown(f"## 👋 Welcome back, **{user['username']}**!")
    st.markdown("Use the sidebar to navigate between pages.")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style="background:#1A2A1A; border:1px solid #2E7D32; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:2.5rem;">📊</div>
            <div style="color:#66BB6A; font-weight:600; margin-top:8px;">Dashboard</div>
            <div style="color:#A5D6A7; font-size:0.9rem;">View your energy charts</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:#1A2A1A; border:1px solid #2E7D32; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:2.5rem;">🔮</div>
            <div style="color:#66BB6A; font-weight:600; margin-top:8px;">Predictions</div>
            <div style="color:#A5D6A7; font-size:0.9rem;">ML-powered forecasting</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style="background:#1A2A1A; border:1px solid #2E7D32; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:2.5rem;">🌿</div>
            <div style="color:#66BB6A; font-weight:600; margin-top:8px;">Recommendations</div>
            <div style="color:#A5D6A7; font-size:0.9rem;">Personalised eco tips</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success(
    "⚡ AI-powered energy analytics using XGBoost forecasting, anomaly detection, and sustainability insights."
)
