import streamlit as st
import pandas as pd
from utils.auth import check_password, create_user
from utils.database import initialize_database

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Initialize database
initialize_database()

def login():
    st.title("Employee Management System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if check_password(username, password):
                user_data = pd.read_csv("data/users.csv")
                user = user_data[user_data['username'] == username].iloc[0]
                st.session_state.authenticated = True
                st.session_state.user_role = user['role']
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

def main():
    if not st.session_state.authenticated:
        login()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.experimental_rerun()

        if st.session_state.user_role == "admin":
            st.title("Admin Dashboard")
            # Admin specific content will be handled in admin_dashboard.py
        else:
            st.title("Employee Dashboard")
            # Employee specific content will be handled in employee_dashboard.py

if __name__ == "__main__":
    main()
