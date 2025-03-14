import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def load_task_management():
    st.title("Task Management")

    # Load data
    tasks_df = pd.read_csv("data/tasks.csv")
    users_df = pd.read_csv("data/users.csv")
    employees = users_df[users_df['role'] == 'employee']['username'].tolist()
    admins = users_df[users_df['role'] == 'admin']['username'].tolist()

    # Task list
    st.subheader("Task List")
    if st.session_state.user_role == 'admin':
        tasks_view = tasks_df
    else:
        tasks_view = tasks_df[
            (tasks_df['assigned_to'] == st.session_state.username) |
            (tasks_df['created_by'] == st.session_state.username)
        ]

    if not tasks_view.empty:
        for _, task in tasks_view.iterrows():
            with st.expander(f"Task: {task['title']}"):
                st.write(f"*Task Title:* {task['title']}")
                st.write(f"*Description:* {task['description']}")
                st.write(f"*Assigned to:* {task['assigned_to']}")
                st.write(f"*Deadline:* {task['deadline']}")
                st.write(f"*Severity:* {task['severity']}")

                # Status selection
                status_options = ["Not Started", "In Progress", "Completed"]
                current_status = task['status']
                selected_status = st.selectbox(f"Status of Task #{task['task_id']}", options=status_options, index=status_options.index(current_status))

                if st.button(f"Update Status of Task #{task['task_id']}"):
                    tasks_df.loc[tasks_df['task_id'] == task['task_id'], 'status'] = selected_status
                    tasks_df.to_csv("data/tasks.csv", index=False)
                    st.success("Task status updated!")
                    st.rerun()

                st.write(f"*Current Status:* {selected_status}")
                st.write(f"*Created by:* {task['created_by']}")

                if st.session_state.user_role == 'admin':
                    if st.button(f"Delete Task #{task['task_id']}"):
                        tasks_df = tasks_df[tasks_df['task_id'] != task['task_id']]
                        tasks_df.to_csv("data/tasks.csv", index=False)
                        st.success("Task deleted!")
                        st.rerun()

    # Task creation form
    st.subheader("Create New Task")
    with st.form("task_form"):
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")

        # Conditional logic for "Assign To" selectbox
        if st.session_state.user_role == 'admin':
            assigned_to = st.selectbox("Assign To", employees)
        else:
            assigned_to = st.selectbox("Assign To", [st.session_state.username])

        deadline = st.date_input("Deadline")
        severity = st.select_slider("Severity", options=["Low", "Medium", "High"])

        submitted = st.form_submit_button("Create Task")

        if submitted:
            if title and description and assigned_to:
                new_task = pd.DataFrame({
                    'task_id': [str(uuid.uuid4())],
                    'title': [title],
                    'description': [description],
                    'assigned_to': [assigned_to],
                    'deadline': [deadline.strftime("%Y-%m-%d")],
                    'severity': [severity],
                    'status': ["Not Started"],
                    'created_by': [st.session_state.username],
                    'approved': [True if st.session_state.user_role == 'admin' else False]
                })

                tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
                tasks_df.to_csv("data/tasks.csv", index=False)
                st.success("Task created successfully!")
                st.rerun()
            else:
                st.error("Please fill all required fields")

if _name_ == "_main_":
    if st.session_state.get('authenticated'):
        load_task_management()
    else:
        st.error("Please login to access task management.")