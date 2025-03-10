import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_employee_dashboard():
    username = st.session_state.username
    
    # Load data
    tasks_df = pd.read_csv("data/tasks.csv")
    leaves_df = pd.read_csv("data/leaves.csv")
    timesheets_df = pd.read_csv("data/timesheets.csv")

    # Filter data for current user
    user_tasks = tasks_df[tasks_df['assigned_to'] == username]
    user_leaves = leaves_df[leaves_df['employee'] == username]
    user_timesheets = timesheets_df[timesheets_df['employee'] == username]

    # Dashboard layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("My Tasks")
        if not user_tasks.empty:
            # Task status distribution
            status_counts = user_tasks['status'].value_counts()
            fig = px.pie(values=status_counts.values, 
                        names=status_counts.index, 
                        title="My Task Status")
            st.plotly_chart(fig)

        # Task list with status update
        for _, task in user_tasks.iterrows():
            with st.expander(f"Task: {task['title']}"):
                st.write(f"Description: {task['description']}")
                st.write(f"Deadline: {task['deadline']}")
                st.write(f"Severity: {task['severity']}")
                new_status = st.selectbox(
                    "Status",
                    ["Not Started", "In Progress", "Completed"],
                    index=["Not Started", "In Progress", "Completed"].index(task['status']),
                    key=f"status_{task['task_id']}"
                )
                if new_status != task['status']:
                    tasks_df.loc[tasks_df['task_id'] == task['task_id'], 'status'] = new_status
                    tasks_df.to_csv("data/tasks.csv", index=False)
                    st.success("Status updated!")
                    st.experimental_rerun()

    with col2:
        st.subheader("My Leave Requests")
        if not user_leaves.empty:
            for _, leave in user_leaves.iterrows():
                with st.expander(f"Leave Request ({leave['start_date']} to {leave['end_date']})"):
                    st.write(f"Type: {leave['leave_type']}")
                    st.write(f"Status: {leave['status']}")
                    st.write(f"Reason: {leave['reason']}")

        st.subheader("My Time Report")
        if not user_timesheets.empty:
            daily_hours = user_timesheets.groupby('date')['hours_worked'].sum().reset_index()
            fig = px.line(daily_hours, 
                         x='date', 
                         y='hours_worked',
                         title="Daily Hours Worked")
            st.plotly_chart(fig)

if __name__ == "__main__":
    if st.session_state.get('authenticated'):
        load_employee_dashboard()
    else:
        st.error("Please login to access the dashboard.")
