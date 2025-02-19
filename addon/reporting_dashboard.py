import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def display_reporting_dashboard():
    try:
        st.header("Reporting Dashboard")

        # Key Metrics
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Reports Submitted", value=10, delta=2)
        with col2:
            st.metric(label="Compliance Score", value="95%", delta="3%")
        with col3:
            st.metric(label="Open Issues", value=5, delta=-2)
        with col4:
            st.metric(label="Days Since Last Incident", value=30, delta=5)

        # Compliance Trend Chart
        st.subheader("Compliance Trend")
        dates = [datetime.now().date() - timedelta(days=x) for x in range(30, 0, -1)]
        scores = [95, 94, 96, 93, 97, 95, 94, 98, 96, 95] * 3
        df = pd.DataFrame({"Date": dates, "Compliance Score": scores})
        fig = px.line(df, x="Date", y="Compliance Score", title="30-Day Compliance Trend")
        st.plotly_chart(fig)

        # Recent Activity
        st.subheader("Recent Activity")
        activities = [
            "Quarterly report submitted",
            "Risk assessment updated",
            "New regulation alert received",
            "Compliance training completed",
            "Incident report filed"
        ]
        for i, activity in enumerate(activities, 1):
            st.write(f"{i}. {activity}")

        # Issue Tracker
        st.subheader("Open Issues")
        issues = [
            {"ID": 1, "Description": "Update privacy policy", "Priority": "High"},
            {"ID": 2, "Description": "Review vendor contracts", "Priority": "Medium"},
            {"ID": 3, "Description": "Conduct security audit", "Priority": "High"},
            {"ID": 4, "Description": "Update employee handbook", "Priority": "Low"},
            {"ID": 5, "Description": "Implement new data retention policy", "Priority": "Medium"}
        ]
        df_issues = pd.DataFrame(issues)
        st.dataframe(df_issues)

        # Action Items
        st.subheader("Action Items")
        action_item = st.text_input("Add new action item")
        if st.button("Add"):
            st.success(f"Action item added: {action_item}")

    except Exception as e:
        st.error(f"Error displaying reporting dashboard: {str(e)}")
        logger.error(f"Error displaying reporting dashboard: {str(e)}")
