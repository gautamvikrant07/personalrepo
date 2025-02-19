import streamlit as st
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, time
from collections import Counter
import pandas as pd
import random

logger = logging.getLogger(__name__)

def display_audit_trail():
    try:
        st.header("Audit Trail")
        json_path = Path("json/audit_trail.json")
        
        if not json_path.exists():
            st.warning("Audit trail file not found. Generating sample data...")
            generate_sample_audit_data(json_path)
        
        with open(json_path, "r") as f:
            audit_entries = json.load(f)
        
        st.write(f"Total entries in file: {len(audit_entries)}")
        
        # Find the date range of the existing entries
        if audit_entries:
            earliest_date = min(datetime.fromisoformat(entry['time']).date() for entry in audit_entries)
            latest_date = max(datetime.fromisoformat(entry['time']).date() for entry in audit_entries)
        else:
            earliest_date = latest_date = datetime.now().date()

        # Set default date range to the last 7 days of data, or the full range if less than 7 days
        default_end_date = min(latest_date, datetime.now().date())
        default_start_date = max(earliest_date, default_end_date - timedelta(days=6))

        # Add filters
        st.sidebar.subheader("Filters")
        date_range = st.sidebar.date_input("Date Range", [default_start_date, default_end_date])
        action_filter = st.sidebar.multiselect("Action", list(set(entry['action'] for entry in audit_entries)))
        user_filter = st.sidebar.multiselect("User", list(set(entry['user'] for entry in audit_entries)))
        
        # Convert date_range to datetime objects
        start_date = datetime.combine(date_range[0], time.min)
        end_date = datetime.combine(date_range[1], time.max)
        
        st.write(f"Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"Action filter: {', '.join(action_filter) if action_filter else 'All'}")
        st.write(f"User filter: {', '.join(user_filter) if user_filter else 'All'}")
        
        # Apply filters
        filtered_entries = [
            entry for entry in audit_entries
            if start_date <= datetime.fromisoformat(entry['time']) <= end_date
            and (not action_filter or entry['action'] in action_filter)
            and (not user_filter or entry['user'] in user_filter)
        ]
        
        st.write(f"Filtered entries: {len(filtered_entries)}")
        
        if filtered_entries:
            # Display filtered entries
            st.subheader("Audit Log Entries")
            for entry in filtered_entries:
                with st.expander(f"{entry['time']} - {entry['action']} by {entry['user']}", expanded=False):
                    st.write(f"**Time:** {entry['time']}")
                    st.write(f"**Action:** {entry['action']}")
                    st.write(f"**User:** {entry['user']}")
                    if 'details' in entry:
                        st.write(f"**Details:** {entry['details']}")
                    else:
                        st.write("**Details:** Not available")
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entries", len(filtered_entries))
            with col2:
                st.metric("Unique Users", len(set(entry['user'] for entry in filtered_entries)))
            with col3:
                action_counts = Counter(entry['action'] for entry in filtered_entries)
                if action_counts:
                    most_common_action = action_counts.most_common(1)[0][0]
                    st.metric("Most Common Action", most_common_action)
                else:
                    st.metric("Most Common Action", "N/A")
            
            # Display action distribution
            st.subheader("Action Distribution")
            action_df = pd.DataFrame.from_dict(action_counts, orient='index', columns=['count'])
            action_df = action_df.sort_values('count', ascending=False)
            st.bar_chart(action_df)
            
            # Display user activity
            st.subheader("User Activity")
            user_counts = Counter(entry['user'] for entry in filtered_entries)
            user_df = pd.DataFrame.from_dict(user_counts, orient='index', columns=['count'])
            user_df = user_df.sort_values('count', ascending=False)
            st.bar_chart(user_df)
        else:
            st.info("No entries found matching the current filters.")
        
        # Display sample entry
        st.subheader("Sample Entry (first in file)")
        if audit_entries:
            st.json(audit_entries[0])
        else:
            st.write("No entries in file")

    except Exception as e:
        st.error(f"Error displaying audit trail: {str(e)}")
        logger.error(f"Error displaying audit trail: {str(e)}")

def generate_sample_audit_data(json_path):
    actions = [
        "Login", "Logout", "Fund Transfer", "Account Creation", "Password Change",
        "Trade Execution", "Loan Approval", "Customer Profile Update", "Document Upload",
        "Risk Assessment", "Compliance Check", "Suspicious Activity Report"
    ]
    users = [
        "john.doe", "jane.smith", "michael.johnson", "emily.brown", "david.wilson",
        "sarah.taylor", "robert.anderson", "olivia.martinez", "william.thomas", "emma.garcia"
    ]
    departments = [
        "Retail Banking", "Corporate Banking", "Investment Banking", "Risk Management",
        "Compliance", "IT", "Human Resources", "Finance", "Operations", "Legal"
    ]

    audit_entries = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    for _ in range(1000):  # Generate 1000 sample entries
        timestamp = start_date + (end_date - start_date) * random.random()
        action = random.choice(actions)
        user = random.choice(users)
        department = random.choice(departments)

        details = generate_action_details(action, user, department)

        entry = {
            "time": timestamp.isoformat(),
            "action": action,
            "user": user,
            "department": department,
            "details": details
        }
        audit_entries.append(entry)

    # Sort entries by timestamp
    audit_entries.sort(key=lambda x: x["time"])

    with open(json_path, "w") as f:
        json.dump(audit_entries, f, indent=2)

def generate_action_details(action, user, department):
    if action == "Login":
        return f"User {user} logged in from IP 192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    elif action == "Logout":
        return f"User {user} logged out"
    elif action == "Fund Transfer":
        amount = round(random.uniform(100, 10000), 2)
        return f"Transfer of ${amount} from account A to account B"
    elif action == "Account Creation":
        return f"New account created for customer ID: CUS{random.randint(10000, 99999)}"
    elif action == "Password Change":
        return f"Password changed for user {user}"
    elif action == "Trade Execution":
        return f"Executed trade of {random.randint(100, 10000)} shares of STOCK{random.randint(1, 100)}"
    elif action == "Loan Approval":
        amount = round(random.uniform(10000, 1000000), 2)
        return f"Loan of ${amount} approved for customer ID: CUS{random.randint(10000, 99999)}"
    elif action == "Customer Profile Update":
        return f"Updated profile for customer ID: CUS{random.randint(10000, 99999)}"
    elif action == "Document Upload":
        return f"Uploaded document: {random.choice(['Passport', 'Drivers License', 'Bank Statement', 'Proof of Address'])}"
    elif action == "Risk Assessment":
        return f"Completed risk assessment for customer ID: CUS{random.randint(10000, 99999)}"
    elif action == "Compliance Check":
        return f"Performed compliance check on transaction ID: TRX{random.randint(100000, 999999)}"
    elif action == "Suspicious Activity Report":
        return f"Filed SAR for account: ACC{random.randint(10000, 99999)}"
    else:
        return "Action details not available"

# ... rest of the code ...
