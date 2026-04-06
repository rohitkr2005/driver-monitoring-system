import streamlit as st
import requests
import pandas as pd
import time

BASE_URL = "https://driver-monitoring-backend-2lbb.onrender.com"

st.set_page_config(
    page_title="Driver Monitoring Dashboard",
    layout="wide",
    page_icon="🚗"
)

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.stButton>button {
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- API HELPER ----------------
def api_request(method, endpoint, params=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.post(url, params=params, timeout=10)
        return response
    except:
        return None

# ---------------- LOGIN ----------------
def login_page():
    st.title("🔐 Admin Login")

    col1, col2 = st.columns([1,1])
    with col1:
        username = st.text_input("Username")
    with col2:
        password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = api_request("POST", "/login", {
            "username": username,
            "password": password
        })

        if response and response.status_code == 200:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials / Server Error ❌")

    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()

# ---------------- SIGNUP ----------------
def signup_page():
    st.title("🆕 Create Admin Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Signup"):
        response = api_request("POST", "/signup", {
            "username": username,
            "password": password
        })

        if response and response.status_code == 200:
            st.success("Account Created ✅")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Signup Failed ❌")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("🚗 Driver Monitoring Dashboard")

    # Sidebar
    st.sidebar.title("📊 Menu")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["📊 Overview", "➕ Add Vehicle", "🚗 Vehicles", "🚨 Alerts"]
    )

    # -------- OVERVIEW --------
    if page == "📊 Overview":
        st.subheader("System Overview")

        col1, col2, col3 = st.columns(3)

        vehicles_res = api_request("GET", "/vehicles")
        alerts_res = api_request("GET", "/alerts")

        total_vehicles = len(vehicles_res.json()) if vehicles_res and vehicles_res.status_code == 200 else 0
        total_alerts = len(alerts_res.json()) if alerts_res and alerts_res.status_code == 200 else 0

        col1.metric("Total Vehicles", total_vehicles)
        col2.metric("Total Alerts", total_alerts)
        col3.metric("System Status", "🟢 Online")

    # -------- ADD VEHICLE --------
    elif page == "➕ Add Vehicle":
        st.subheader("Add Vehicle")

        vehicle_no = st.text_input("Vehicle Number")
        dashcam_id = st.text_input("Dashcam ID")

        if st.button("Add"):
            res = api_request("POST", "/add_vehicle", {
                "vehicle_no": vehicle_no,
                "dashcam_id": dashcam_id
            })

            if res and res.status_code == 200:
                st.success("Vehicle Added ✅")
            else:
                st.error("Failed ❌")

    # -------- VEHICLES --------
    elif page == "🚗 Vehicles":
        st.subheader("Registered Vehicles")

        res = api_request("GET", "/vehicles")

        if res and res.status_code == 200:
            data = res.json()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No vehicles found")
        else:
            st.error("Error fetching data ❌")

    # -------- ALERTS --------
    elif page == "🚨 Alerts":
        st.subheader("Live Alerts")

        auto_refresh = st.checkbox("Auto Refresh (5s)")

        res = api_request("GET", "/alerts")

        if res and res.status_code == 200:
            data = res.json()

            if data:
                df = pd.DataFrame(data)

                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                st.dataframe(df, use_container_width=True)

                latest = df.iloc[-1]
                st.error(
                    f"🚨 Latest Alert: {latest['alert_type']} | Vehicle: {latest['vehicle_id']}"
                )
            else:
                st.success("No alerts 🎉")
        else:
            st.error("Error fetching alerts ❌")

        if auto_refresh:
            time.sleep(5)
            st.rerun()

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    dashboard()