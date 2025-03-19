import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_employee_dashboard():
    username = st.session_state.username

    # Load data
    try:
        tasks_df = pd.read_csv("data/tasks.csv")
        leaves_df = pd.read_csv("data/leaves.csv")
        timesheets_df = pd.read_csv("data/timesheets.csv")
    except FileNotFoundError:
        st.error("Data files not found. Please ensure 'tasks.csv', 'leaves.csv', and 'timesheets.csv' are in the 'data' directory.")
        return

    # Filter data for current user
    user_tasks = tasks_df[tasks_df['assigned_to'] == username]
    user_leaves = leaves_df[leaves_df['employee'] == username]
    user_timesheets = timesheets_df[timesheets_df['employee'] == username]

    # Dashboard layout
    st.title(f"Welcome, {username}!")
    
    # Task status distribution
    st.subheader("My Tasks")
    if not user_tasks.empty:
        # Task status counts
        not_started = len(user_tasks[user_tasks['status'] == 'Not Started'])
        in_progress = len(user_tasks[user_tasks['status'] == 'In Progress'])
        completed = len(user_tasks[user_tasks['status'] == 'Completed'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Not Started", value=not_started, delta=None)
        with col2:
            st.metric(label="In Progress", value=in_progress, delta=None)
        with col3:
            st.metric(label="Completed", value=completed, delta=None)

        # Task status distribution
        status_counts = user_tasks['status'].value_counts()
        fig = px.pie(values=status_counts.values, 
                    names=status_counts.index, 
                    title="Task Status",
                    color_discrete_sequence=px.colors.sequential.Blues)
        fig.update_layout(height=500, width=700)
        st.plotly_chart(fig)

        # Task list with status update
        st.subheader("Task List")
        for _, task in user_tasks.iterrows():
            with st.expander(f"Task: {task['title']}", expanded=False):
                st.write(f"Description: {task['description']}")
                st.write(f"Deadline: {task['deadline']}")
                st.write(f"Severity: {task['severity']}")
                new_status = st.selectbox(
                    "Status",
                    ["Not Started", "In Progress", "Completed"],
                    index=["Not Started", "In Progress", "Completed"].index(task['status']),
                    key=f"status_{task['task_id']}"
                )
                if st.button("Update Status", key=f"update_{task['task_id']}"):
                    if new_status != task['status']:
                        tasks_df.loc[tasks_df['task_id'] == task['task_id'], 'status'] = new_status
                        tasks_df.to_csv("data/tasks.csv", index=False)
                        st.success("Status updated!")
                        st.experimental_rerun()
    else:
        st.info("No tasks assigned.")

    # Leave requests and time report
    st.subheader("My Leave Requests and Time Report")
    col3, col4 = st.columns([6, 4])
    
    with col3:
        if not user_leaves.empty:
            for _, leave in user_leaves.iterrows():
                with st.expander(f"Leave Request ({leave['start_date']} to {leave['end_date']})", expanded=False):
                    st.write(f"Type: {leave['leave_type']}")
                    st.write(f"Status: {leave['status']}")
                    st.write(f"Reason: {leave['reason']}")
        else:
            st.info("No leave requests.")

        if not user_timesheets.empty:
            daily_hours = user_timesheets.groupby('date')['hours_worked'].sum().reset_index()
            fig = px.line(daily_hours, 
                         x='date', 
                         y='hours_worked',
                         title="Daily Hours Worked",
                         color_discrete_sequence=['#2596be'])
            fig.update_layout(height=400, width=600)
            st.plotly_chart(fig)

    with col4:
        if not user_timesheets.empty:
            # Weekly summary
            st.subheader("Weekly Summary")
            total_hours = user_timesheets['hours_worked'].sum()
            st.metric("Total Hours Logged", f"{total_hours:.1f}")
        else:
            st.info("No time reports.")

if __name__ == "__main__":
    if st.session_state.get('authenticated'):
        load_employee_dashboard()
    else:
        st.error("Please login to access the dashboard.")
