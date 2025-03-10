import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_admin_dashboard():
    # Load data
    tasks_df = pd.read_csv("data/tasks.csv")
    leaves_df = pd.read_csv("data/leaves.csv")
    timesheets_df = pd.read_csv("data/timesheets.csv")

    # Dashboard layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Task Overview")
        if not tasks_df.empty:
            # Task status distribution
            status_counts = tasks_df['status'].value_counts()
            fig = px.pie(values=status_counts.values, 
                        names=status_counts.index, 
                        title="Task Status Distribution")
            st.plotly_chart(fig)

        # Pending approvals
        st.subheader("Pending Approvals")
        pending_tasks = tasks_df[
            (tasks_df['approved'] == False) & 
            (tasks_df['created_by'] != 'admin')
        ]
        if not pending_tasks.empty:
            for _, task in pending_tasks.iterrows():
                with st.expander(f"Task: {task['title']}"):
                    st.write(f"Created by: {task['created_by']}")
                    st.write(f"Description: {task['description']}")
                    if st.button(f"Approve Task #{task['task_id']}"):
                        tasks_df.loc[tasks_df['task_id'] == task['task_id'], 'approved'] = True
                        tasks_df.to_csv("data/tasks.csv", index=False)
                        st.success("Task approved!")
                        st.experimental_rerun()

    with col2:
        st.subheader("Leave Requests")
        pending_leaves = leaves_df[leaves_df['status'] == 'Pending']
        if not pending_leaves.empty:
            for _, leave in pending_leaves.iterrows():
                with st.expander(f"Leave Request: {leave['employee']}"):
                    st.write(f"Type: {leave['leave_type']}")
                    st.write(f"Duration: {leave['start_date']} to {leave['end_date']}")
                    st.write(f"Reason: {leave['reason']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Approve #{leave['leave_id']}"):
                            leaves_df.loc[leaves_df['leave_id'] == leave['leave_id'], 'status'] = 'Approved'
                            leaves_df.to_csv("data/leaves.csv", index=False)
                            st.success("Leave approved!")
                            st.experimental_rerun()
                    with col2:
                        if st.button(f"Reject #{leave['leave_id']}"):
                            leaves_df.loc[leaves_df['leave_id'] == leave['leave_id'], 'status'] = 'Rejected'
                            leaves_df.to_csv("data/leaves.csv", index=False)
                            st.error("Leave rejected!")
                            st.experimental_rerun()

    # Employee Performance Metrics
    st.subheader("Employee Performance Metrics")
    if not timesheets_df.empty:
        employee_hours = timesheets_df.groupby('employee')['hours_worked'].sum().reset_index()
        fig = px.bar(employee_hours, 
                     x='employee', 
                     y='hours_worked',
                     title="Total Hours Worked by Employee")
        st.plotly_chart(fig)

if __name__ == "__main__":
    if st.session_state.get('user_role') == 'admin':
        load_admin_dashboard()
    else:
        st.error("Access denied. Admin privileges required.")
