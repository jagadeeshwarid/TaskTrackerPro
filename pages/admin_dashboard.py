import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from utils.auth import create_user

def load_admin_dashboard():
    # Load data
    tasks_df = pd.read_csv("data/tasks.csv")
    leaves_df = pd.read_csv("data/leaves.csv")
    timesheets_df = pd.read_csv("data/timesheets.csv")
    users_df = pd.read_csv("data/users.csv")

    # Sidebar navigation
    st.sidebar.header("Admin Controls")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard Overview", "Employee Management", "Task Approvals", "Leave Management"]
    )

    if page == "Dashboard Overview":
        display_dashboard_overview(tasks_df, leaves_df, timesheets_df)
    elif page == "Employee Management":
        manage_employees(users_df)
    elif page == "Task Approvals":
        manage_task_approvals(tasks_df)
    elif page == "Leave Management":
        manage_leave_requests(leaves_df)

def display_dashboard_overview(tasks_df, leaves_df, timesheets_df):
    st.header("Dashboard Overview")

    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tasks", len(tasks_df))
    with col2:
        st.metric("Pending Tasks", len(tasks_df[tasks_df['status'] != 'Completed']))
    with col3:
        st.metric("Pending Leaves", len(leaves_df[leaves_df['status'] == 'Pending']))
    with col4:
        total_hours = timesheets_df['hours_worked'].sum()
        st.metric("Total Hours Logged", f"{total_hours:.1f}")

    # Task Status Distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Task Status Distribution")
        if not tasks_df.empty:
            status_counts = tasks_df['status'].value_counts()
            fig = px.pie(values=status_counts.values, 
                        names=status_counts.index, 
                        title="Task Status Distribution",
                        color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig)

        # Severity Distribution
        severity_counts = tasks_df['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, 
                     y=severity_counts.values,
                     title="Task Severity Distribution",
                     color_discrete_sequence=['#2596be'])
        st.plotly_chart(fig)

    with col2:
        st.subheader("Employee Performance")
        if not timesheets_df.empty:
            employee_hours = timesheets_df.groupby('employee')['hours_worked'].sum().reset_index()
            fig = px.bar(employee_hours, 
                         x='employee', 
                         y='hours_worked',
                         title="Total Hours Worked by Employee",
                         color_discrete_sequence=['#2596be'])
            st.plotly_chart(fig)

def manage_employees(users_df):
    st.header("Employee Management")

    # Employee Creation Form
    with st.expander("Add New Employee", expanded=False):
        with st.form("add_employee_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if new_username and new_password:
                    success, message = create_user(new_username, new_password, "employee")
                    if success:
                        st.success(f"Employee {new_username} created successfully!")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields")

    # Employee List
    st.subheader("Employee List")
    employees = users_df[users_df['role'] == 'employee']
    if not employees.empty:
        for _, employee in employees.iterrows():
            with st.expander(f"Employee: {employee['username']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("Role:", employee['role'])
                with col2:
                    st.write("Status: Active")
                with col3:
                    if st.button(f"Reset Password ({employee['username']})", key=f"reset_{employee['username']}"):
                        # Implement password reset logic
                        st.info("Password reset functionality to be implemented")

def manage_task_approvals(tasks_df):
    st.header("Task Approvals")

    pending_tasks = tasks_df[
        (tasks_df['approved'] == False) & 
        (tasks_df['created_by'] != 'admin')
    ]

    if not pending_tasks.empty:
        for _, task in pending_tasks.iterrows():
            with st.expander(f"Task: {task['title']}"):
                st.write(f"Created by: {task['created_by']}")
                st.write(f"Description: {task['description']}")
                st.write(f"Severity: {task['severity']}")
                st.write(f"Deadline: {task['deadline']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve Task #{task['task_id']}", key=f"approve_{task['task_id']}"):
                        tasks_df.loc[tasks_df['task_id'] == task['task_id'], 'approved'] = True
                        tasks_df.to_csv("data/tasks.csv", index=False)
                        st.success("Task approved!")
                        st.rerun()
                with col2:
                    if st.button(f"Reject Task #{task['task_id']}", key=f"reject_{task['task_id']}"):
                        # Remove the task instead of keeping it as rejected
                        tasks_df = tasks_df[tasks_df['task_id'] != task['task_id']]
                        tasks_df.to_csv("data/tasks.csv", index=False)
                        st.error("Task rejected!")
                        st.rerun()
    else:
        st.info("No pending task approvals")

def manage_leave_requests(leaves_df):
    st.header("Leave Management")

    pending_leaves = leaves_df[leaves_df['status'] == 'Pending']
    if not pending_leaves.empty:
        for _, leave in pending_leaves.iterrows():
            with st.expander(f"Leave Request: {leave['employee']}"):
                st.write(f"Type: {leave['leave_type']}")
                st.write(f"Duration: {leave['start_date']} to {leave['end_date']}")
                st.write(f"Reason: {leave['reason']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve #{leave['leave_id']}", key=f"approve_leave_{leave['leave_id']}"):
                        leaves_df.loc[leaves_df['leave_id'] == leave['leave_id'], 'status'] = 'Approved'
                        leaves_df.to_csv("data/leaves.csv", index=False)
                        st.success("Leave approved!")
                        st.rerun()
                with col2:
                    if st.button(f"Reject #{leave['leave_id']}", key=f"reject_leave_{leave['leave_id']}"):
                        leaves_df.loc[leaves_df['leave_id'] == leave['leave_id'], 'status'] = 'Rejected'
                        leaves_df.to_csv("data/leaves.csv", index=False)
                        st.error("Leave rejected!")
                        st.rerun()
    else:
        st.info("No pending leave requests")

if __name__ == "__main__":
    if st.session_state.get('user_role') == 'admin':
        load_admin_dashboard()
    else:
        st.error("Access denied. Admin privileges required.")