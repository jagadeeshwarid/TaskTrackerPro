import streamlit as st
import pandas as pd
from utils.auth import check_password, create_user, reset_password
from utils.database import initialize_database

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #2596be;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .main {
        background-color: #0b0039;
        color: white;
    }
    .stTitle {
        color: #2596be !important;
    }
    .stHeader {
        background-color: rgba(37, 150, 190, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_reset' not in st.session_state:
    st.session_state.show_reset = False

# Initialize database
initialize_database()

def reset_password_form():
    st.subheader("Reset Admin Password")
    with st.form("reset_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if new_password != confirm_password:
                st.error("New passwords don't match!")
                return
            if check_password("admin", current_password):
                success = reset_password("admin", new_password)
                if success:
                    st.success("Password reset successful! Please login with new password.")
                    st.session_state.show_reset = False
                    st.rerun()
                else:
                    st.error("Failed to reset password. Please try again.")
            else:
                st.error("Current password is incorrect!")

def login():
    st.title("Employee Management System")

    # Create three columns for centered login form
    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Login")
            with col2:
                if st.form_submit_button("Reset Admin Password"):
                    st.session_state.show_reset = True
                    st.rerun()

        if submitted:
            try:
                if check_password(username, password):
                    user_data = pd.read_csv("data/users.csv")
                    user = user_data[user_data['username'] == username].iloc[0]
                    st.session_state.authenticated = True
                    st.session_state.user_role = user['role']
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                st.error(f"An error occurred during login. Please try again.")

def main():
    if not st.session_state.authenticated:
        if st.session_state.show_reset:
            reset_password_form()
            if st.button("Back to Login"):
                st.session_state.show_reset = False
                st.rerun()
        else:
            login()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()

        if st.session_state.user_role == "admin":
            st.title("Admin Dashboard")
        else:
            st.title("Employee Dashboard")

if __name__ == "__main__":
    main()