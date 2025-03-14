import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File path
TIMESHEET_FILE = "data/timesheets.csv"
TASKS_FILE = "data/tasks.csv"

# Ensure the directory exists
os.makedirs("data", exist_ok=True)

# Load or create timesheet file
def load_timesheet_data():
    if not os.path.exists(TIMESHEET_FILE):
        return pd.DataFrame(columns=["timesheet_id", "employee", "date", "login_time", "logout_time", "tasks", "task_notes", "hours_worked"])
    return pd.read_csv(TIMESHEET_FILE)

# Save timesheet data
def save_timesheet_data(df):
    df.to_csv(TIMESHEET_FILE, index=False)

# Load tasks
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return pd.DataFrame(columns=["task_id", "title", "assigned_to"])
    return pd.read_csv(TASKS_FILE)

# Main function
def timesheet_app():
    st.title("Employee Timesheet Tracker")
    
    if "username" not in st.session_state:
        st.error("Please login first!")
        return
    
    username = st.session_state.username
    today_date = datetime.today().strftime("%Y-%m-%d")
    timesheet_df = load_timesheet_data()
    tasks_df = load_tasks()
    
    # Generate timesheet ID
    timesheet_id = f"{username}_Proitbridge"
    
    # Filter tasks assigned to the user
    user_tasks = tasks_df[tasks_df["assigned_to"] == username]
    task_list = user_tasks["title"].tolist()
    
    # Find existing record for today
    user_entry = timesheet_df[(timesheet_df["employee"] == username) & (timesheet_df["date"] == today_date)]
    login_time = user_entry["login_time"].values[0] if not user_entry.empty else None
    logout_time = user_entry["logout_time"].values[0] if not user_entry.empty else None
    hours_worked = user_entry["hours_worked"].values[0] if not user_entry.empty else None
    
    st.subheader(f"Timesheet for {today_date}")
    
    # Login button
    if login_time is None:
        if st.button("Login"):
            login_time = datetime.now().strftime("%H:%M:%S")
            new_entry = pd.DataFrame({
                "timesheet_id": [timesheet_id],
                "employee": [username],
                "date": [today_date],
                "login_time": [login_time],
                "logout_time": [None],
                "tasks": [""],
                "task_notes": [""],
                "hours_worked": [None]
            })
            timesheet_df = pd.concat([timesheet_df, new_entry], ignore_index=True)
            save_timesheet_data(timesheet_df)
            st.experimental_rerun()
    elif pd.isna(logout_time):
        st.success(f"Logged in at: {login_time}")
        
        # Multi-task selection
        selected_tasks = st.multiselect("Select Tasks", task_list)
        task_notes = st.text_area("Add Notes for Selected Tasks")
        
        if st.button("Update Progress"):
            timesheet_df.loc[(timesheet_df["employee"] == username) & (timesheet_df["date"] == today_date), "tasks"] = ", ".join(selected_tasks)
            timesheet_df.loc[(timesheet_df["employee"] == username) & (timesheet_df["date"] == today_date), "task_notes"] = task_notes
            save_timesheet_data(timesheet_df)
            st.success("Progress updated successfully!")
            st.experimental_rerun()
        
        if st.button("Logout"):
            logout_time = datetime.now().strftime("%H:%M:%S")
            login_dt = datetime.strptime(login_time, "%H:%M:%S")
            logout_dt = datetime.strptime(logout_time, "%H:%M:%S")
            hours_worked = round((logout_dt - login_dt).total_seconds() / 3600, 2)
            timesheet_df.loc[(timesheet_df["employee"] == username) & (timesheet_df["date"] == today_date), "logout_time"] = logout_time
            timesheet_df.loc[(timesheet_df["employee"] == username) & (timesheet_df["date"] == today_date), "hours_worked"] = hours_worked
            save_timesheet_data(timesheet_df)
            st.experimental_rerun()
    else:
        st.success(f"Logged out at: {logout_time}. Total hours worked: {hours_worked}. You cannot log in or log out again today.")
    
    # Display timesheet history
    st.subheader("My Timesheet History")
    user_timesheets = timesheet_df[timesheet_df["employee"] == username]
    if not user_timesheets.empty:
        st.dataframe(user_timesheets.sort_values("date", ascending=False))

# Run the app
if __name__ == "__main__":
    if st.session_state.get("authenticated"):
        timesheet_app()
    else:
        st.error("Please login to access the timesheet.")