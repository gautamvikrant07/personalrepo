import logging
import os
from typing import Dict
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_templates() -> Dict[str, str]:
    try:
        template_dir = "report_templates"
        templates = {}
        for filename in os.listdir(template_dir):
            if filename.endswith(".docx"):
                name = filename.replace("_", " ").replace(".docx", "").title()
                templates[name] = filename
        return templates
    except FileNotFoundError:
        logger.warning("report_templates directory not found. Using sample data.")
        return {
            "Annual Financial Report": "template_annual_financial.docx",
            "Quarterly Compliance Update": "template_quarterly_compliance.docx",
            "Risk Assessment Summary": "template_risk_assessment.docx"
        }

def display_report_templates():
    try:
        st.header("Regulatory Report Templates")
        
        # Use the get_templates function to dynamically load templates
        templates = get_templates()
        selected_template = st.selectbox("Select a template", list(templates.keys()))
        
        st.write(f"You selected: {selected_template}")
        
        # Display template details
        st.subheader("Template Details")
        st.write(f"Filename: {templates[selected_template]}")
        
        # Add input fields for report parameters
        st.subheader("Report Parameters")
        reporting_period = st.date_input("Reporting Period End Date")
        entity_name = st.text_input("Entity Name")
        
        # Add a file uploader for additional data
        st.subheader("Additional Data")
        uploaded_file = st.file_uploader("Upload supporting documents", type=["csv", "xlsx"])
        
        if st.button("Generate Report"):
            if uploaded_file is not None:
                # Here you would add logic to process the uploaded file and generate the report
                st.success(f"Report generated for {entity_name} for the period ending {reporting_period}")
                st.download_button(
                    label="Download Report",
                    data=b"Your report content here",  # Replace with actual report content
                    file_name=f"{selected_template}_{entity_name}_{reporting_period}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.warning("Please upload supporting documents before generating the report.")
        
    except Exception as e:
        st.error(f"Error displaying report templates: {str(e)}")
        logger.error(f"Error displaying report templates: {str(e)}")
