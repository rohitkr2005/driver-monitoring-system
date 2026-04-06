import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Driver Monitoring Dashboard", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{BASE_URL}/login",
            params={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    st.write("Don't have an account?")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()

# ---------------- SIGNUP PAGE ----------------
def signup_page():
    st.title("🆕 Create Admin Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Signup"):
        response = requests.post(
            f"{BASE_URL}/signup",
            params={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.success("Account Created Successfully ✅")
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

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

    st.sidebar.title("Menu")

    option = st.sidebar.selectbox(
        "Choose Option",
        ["Add Vehicle", "View Vehicles", "Live Alerts"]
    )

    # -------- ADD VEHICLE --------
    if option == "Add Vehicle":
        st.subheader("➕ Add New Vehicle")

        vehicle_no = st.text_input("Vehicle Number")
        dashcam_id = st.text_input("Dashcam ID")

        if st.button("Add Vehicle"):
            response = requests.post(
                f"{BASE_URL}/add_vehicle",
                params={
                    "vehicle_no": vehicle_no,
                    "dashcam_id": dashcam_id
                }
            )

            if response.status_code == 200:
                st.success("Vehicle Added ✅")
            else:
                st.error("Error adding vehicle ❌")

    # -------- VIEW VEHICLES --------
    elif option == "View Vehicles":
        st.subheader("📋 Registered Vehicles")

        response = requests.get(f"{BASE_URL}/vehicles")

        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("No vehicles found")

    # -------- LIVE ALERTS --------
    elif option == "Live Alerts":
        st.subheader("🚨 Live Alerts")

        if st.button("🔄 Refresh Alerts"):
            pass

        response = requests.get(f"{BASE_URL}/alerts")

        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)

                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                st.dataframe(df)

                latest = df.iloc[-1]
                st.warning(
                    f"⚠ Latest Alert: {latest['alert_type']} from {latest['vehicle_id']}"
                )
            else:
                st.success("No alerts yet 🎉")

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    dashboard()