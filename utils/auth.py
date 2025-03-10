import hashlib
import pandas as pd
import streamlit as st

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    """Verify username and password"""
    try:
        users_df = pd.read_csv("data/users.csv")
        user = users_df[users_df['username'] == username]
        if not user.empty:
            stored_password = user.iloc[0]['password']
            return stored_password == hash_password(password)
    except Exception as e:
        st.error(f"Error checking password: {str(e)}")
    return False

def create_user(username, password, role):
    """Create a new user"""
    try:
        users_df = pd.read_csv("data/users.csv")
        if username in users_df['username'].values:
            return False, "Username already exists"
        
        new_user = pd.DataFrame({
            'username': [username],
            'password': [hash_password(password)],
            'role': [role]
        })
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv("data/users.csv", index=False)
        return True, "User created successfully"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"
