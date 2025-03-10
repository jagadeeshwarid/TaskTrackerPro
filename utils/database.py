import pandas as pd
import os

def initialize_database():
    """Initialize CSV files if they don't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Users database
    if not os.path.exists("data/users.csv"):
        users_df = pd.DataFrame({
            'username': ['admin'],
            'password': ['8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'],  # admin
            'role': ['admin']
        })
        users_df.to_csv("data/users.csv", index=False)
    
    # Tasks database
    if not os.path.exists("data/tasks.csv"):
        tasks_df = pd.DataFrame({
            'task_id': [],
            'title': [],
            'description': [],
            'assigned_to': [],
            'deadline': [],
            'severity': [],
            'status': [],
            'created_by': [],
            'approved': []
        })
        tasks_df.to_csv("data/tasks.csv", index=False)
    
    # Leaves database
    if not os.path.exists("data/leaves.csv"):
        leaves_df = pd.DataFrame({
            'leave_id': [],
            'employee': [],
            'start_date': [],
            'end_date': [],
            'leave_type': [],
            'status': [],
            'reason': []
        })
        leaves_df.to_csv("data/leaves.csv", index=False)
    
    # Timesheets database
    if not os.path.exists("data/timesheets.csv"):
        timesheets_df = pd.DataFrame({
            'timesheet_id': [],
            'employee': [],
            'date': [],
            'hours_worked': [],
            'task_id': [],
            'description': []
        })
        timesheets_df.to_csv("data/timesheets.csv", index=False)
