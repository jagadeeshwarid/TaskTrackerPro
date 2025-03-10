import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def load_timesheet():
    st.title("Timesheet Management")
    
    # Load data
    timesheets_df = pd.read_csv("data/timesheets.csv")
    tasks_df = pd.read_csv("data/tasks.csv")

    # Get user's tasks for the dropdown
    user_tasks = tasks_df[tasks_df['assigned_to'] == st.session_state.username]
    
    # Timesheet entry form
    with st.form("timesheet_form"):
        st.subheader("Log Time")
        date = st.date_input("Date")
        hours_worked = st.number_input("Hours Worked", min_value=0.0, max_value=24.0, step=0.5)
        task_id = st.selectbox("Related Task", 
                              options=user_tasks['task_id'].tolist(),
                              format_func=lambda x: user_tasks[user_tasks['task_id']==x]['title'].iloc[0])
        description = st.text_area("Work Description")
        
        submitted = st.form_submit_button("Log Time")
        
        if submitted:
            if hours_worked > 0:
                new_entry = pd.DataFrame({
                    'timesheet_id': [str(uuid.uuid4())],
                    'employee': [st.session_state.username],
                    'date': [date.strftime("%Y-%m-%d")],
                    'hours_worked': [hours_worked],
                    'task_id': [task_id],
                    'description': [description]
                })
                
                timesheets_df = pd.concat([timesheets_df, new_entry], ignore_index=True)
                timesheets_df.to_csv("data/timesheets.csv", index=False)
                st.success("Time logged successfully!")
                st.experimental_rerun()
            else:
                st.error("Please enter valid hours worked")

    # Timesheet history
    st.subheader("My Timesheet History")
    user_timesheets = timesheets_df[timesheets_df['employee'] == st.session_state.username]
    
    if not user_timesheets.empty:
        user_timesheets = user_timesheets.sort_values('date', ascending=False)
        for _, entry in user_timesheets.iterrows():
            with st.expander(f"Date: {entry['date']} ({entry['hours_worked']} hours)"):
                task_title = user_tasks[user_tasks['task_id'] == entry['task_id']]['title'].iloc[0]
                st.write(f"Task: {task_title}")
                st.write(f"Description: {entry['description']}")
                
                if st.button(f"Delete Entry #{entry['timesheet_id']}"):
                    timesheets_df = timesheets_df[timesheets_df['timesheet_id'] != entry['timesheet_id']]
                    timesheets_df.to_csv("data/timesheets.csv", index=False)
                    st.success("Entry deleted!")
                    st.experimental_rerun()

if __name__ == "__main__":
    if st.session_state.get('authenticated'):
        load_timesheet()
    else:
        st.error("Please login to access timesheet management.")
