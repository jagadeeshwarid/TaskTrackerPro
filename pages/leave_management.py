import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def load_leave_management():
    st.title("Leave Management")
    
    # Load data
    leaves_df = pd.read_csv("data/leaves.csv")

    # Leave request form
    with st.form("leave_form"):
        st.subheader("Submit Leave Request")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        leave_type = st.selectbox("Leave Type", ["Vacation", "Sick Leave", "Work from Home"])
        reason = st.text_area("Reason")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if start_date <= end_date:
                new_leave = pd.DataFrame({
                    'leave_id': [str(uuid.uuid4())],
                    'employee': [st.session_state.username],
                    'start_date': [start_date.strftime("%Y-%m-%d")],
                    'end_date': [end_date.strftime("%Y-%m-%d")],
                    'leave_type': [leave_type],
                    'status': ['Pending'],
                    'reason': [reason]
                })
                
                leaves_df = pd.concat([leaves_df, new_leave], ignore_index=True)
                leaves_df.to_csv("data/leaves.csv", index=False)
                st.success("Leave request submitted successfully!")
                st.experimental_rerun()
            else:
                st.error("End date must be after start date")

    # Leave request list
    st.subheader("My Leave Requests")
    user_leaves = leaves_df[leaves_df['employee'] == st.session_state.username]
    
    if not user_leaves.empty:
        for _, leave in user_leaves.iterrows():
            with st.expander(f"Leave Request ({leave['start_date']} to {leave['end_date']})"):
                st.write(f"Type: {leave['leave_type']}")
                st.write(f"Status: {leave['status']}")
                st.write(f"Reason: {leave['reason']}")
                
                if leave['status'] == 'Pending':
                    if st.button(f"Cancel Request #{leave['leave_id']}"):
                        leaves_df = leaves_df[leaves_df['leave_id'] != leave['leave_id']]
                        leaves_df.to_csv("data/leaves.csv", index=False)
                        st.success("Leave request cancelled!")
                        st.experimental_rerun()

if __name__ == "__main__":
    if st.session_state.get('authenticated'):
        load_leave_management()
    else:
        st.error("Please login to access leave management.")
