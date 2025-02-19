import streamlit as st

st.set_page_config(page_title="CapGenie Regulatory Suite AI", layout="wide")

import os
from typing import Dict, Any

os.environ['USER_AGENT'] = "capgenie/1.0 (support@capgenie.ai)"

# Imports from your existing structure
from corep.excel_processing import handle_regulatory_reports
from database.interact_with_database import interact_with_database
from web.interact_with_web import interact_with_web
from xbrl.interact_with_xbrl import interact_with_xbrl
from utils.session_management import display_session_history
from utils.settings import settings as manage_settings
from auth.user_management import handle_authentication, initialize_session_state
from corep.knowledge_base import display_knowledge_base
from utils.feedback import feedback_section
from utils.monitoring import display_system_health as display_dashboard
from corep.earnings_report_analyzer import analyze_earnings_report
from utils.header import render_header, render_home
from addon.regulatory_calendar import display_regulatory_calendar
from addon.news_feed import display_regulatory_news
from addon.compliance_checklist import display_compliance_checklist
from addon.report_templates import display_report_templates
from addon.regulatory_qa import display_regulatory_qa
from addon.scenario_analysis import run_scenario_analysis
from addon.audit_trail import display_audit_trail
from addon.data_validation import validate_regulatory_data
from addon.reporting_dashboard import display_reporting_dashboard
from addon.jira_integration import interact_with_jira
from corep.process_pdf import PDFProcessor
from addon.data_visualization import display_data_visualization


def render_navigation() -> str:
    """Render navigation sidebar and return selected tab."""
    return st.sidebar.radio(
        "Navigation",
        ["Home", "Dashboard", "Regulatory Reports", "Knowledge Base", "Earnings Analyzer",
         "Data Management", "Regulatory Tools", "Monitoring & Compliance",
         "Settings & History"],
        format_func=lambda x: {
            "Home": "🏠 Home",
            "Dashboard": "📊 Dashboard",
            "Regulatory Reports": "📑 Regulatory Reports",
            "Knowledge Base": "🧠 Knowledge Base",
            "Earnings Analyzer": "📈 Earnings Analyzer",
            "Data Management": "💾 Data Management",
            "Regulatory Tools": "🛠️ Regulatory Tools",
            "Monitoring & Compliance": "🔍 Monitoring & Compliance",
            "Settings & History": "⚙️ Settings & History"
        }[x]
    )


def render_footer() -> None:
    """Render the footer with legal notice."""
    st.sidebar.markdown(
        "<div style='font-size: small;'>This application contains proprietary information. "
        "© 2024 CapGenie Regulatory Suite AI. All rights reserved.</div>",
        unsafe_allow_html=True
    )


def main() -> None:
    """
    Main function to run the CapGenie Regulatory Suite AI application.

    This function initializes the application, handles user authentication, and
    provides navigation through different functional sections focused on regulatory reporting tasks.
    """
    render_header()
    initialize_session_state()
    handle_authentication()

    if st.session_state['logged_in']:
        selected_section = render_navigation()

        section_functions: Dict[str, Any] = {
            "Home": render_home,
            "Dashboard": display_dashboard,
            "Regulatory Reports": handle_regulatory_reports,
            "Knowledge Base": display_knowledge_base,
            "Earnings Analyzer": analyze_earnings_report,
            "Data Management": data_management_submenu,
            "Regulatory Tools": regulatory_tools_submenu,
            "Monitoring & Compliance": monitoring_compliance_submenu,
            "Settings & History": settings_history_submenu
        }

        section_functions.get(selected_section, lambda: None)()

        render_footer()
        feedback_section()


def data_management_submenu():
    submenu = st.sidebar.radio(
        "💾 Data Management",
        ["Database Interface", "Web Scraper", "XBRL Processor", "PDF Processor", "Data Visualization"],
        format_func=lambda x: {
            "Database Interface": "🗃️ Database Interface",
            "Web Scraper": "🕸️ Web Scraper",
            "XBRL Processor": "📊 XBRL Processor",
            "PDF Processor": "📄 PDF Processor",
            "Data Visualization": "📈 Data Visualization"
        }[x]
    )
    if submenu == "Database Interface":
        interact_with_database()
    elif submenu == "Web Scraper":
        interact_with_web()
    elif submenu == "XBRL Processor":
        interact_with_xbrl()
    elif submenu == "PDF Processor":
        pdf_processor = PDFProcessor()
        pdf_processor.run()
    elif submenu == "Data Visualization":
        display_data_visualization()


def regulatory_tools_submenu():
    submenu = st.sidebar.radio(
        "🛠️ Regulatory Tools",
        ["Regulatory Calendar", "News Feed", "Compliance Checklist", "Report Templates", "Regulatory Q&A",
         "Scenario Analysis"],
        format_func=lambda x: {
            "Regulatory Calendar": "📅 Regulatory Calendar",
            "News Feed": "📰 News Feed",
            "Compliance Checklist": "✅ Compliance Checklist",
            "Report Templates": "📋 Report Templates",
            "Regulatory Q&A": "❓ Regulatory Q&A",
            "Scenario Analysis": "🔮 Scenario Analysis"
        }[x]
    )
    if submenu == "Regulatory Calendar":
        display_regulatory_calendar()
    elif submenu == "News Feed":
        display_regulatory_news()
    elif submenu == "Compliance Checklist":
        display_compliance_checklist()
    elif submenu == "Report Templates":
        display_report_templates()
    elif submenu == "Regulatory Q&A":
        display_regulatory_qa()
    elif submenu == "Scenario Analysis":
        run_scenario_analysis()


def monitoring_compliance_submenu():
    submenu = st.sidebar.radio(
        "🔍 Monitoring & Compliance",
        ["Audit Trail", "Data Validation", "Reporting Dashboard", "JIRA & GIT Integration"],
        format_func=lambda x: {
            "Audit Trail": "🔎 Audit Trail",
            "Data Validation": "✔️ Data Validation",
            "Reporting Dashboard": "📊 Reporting Dashboard",
            "JIRA & GIT Integration": "🎫 JIRA & GIT Integration"
        }[x]
    )
    if submenu == "Audit Trail":
        display_audit_trail()
    elif submenu == "Data Validation":
        validate_regulatory_data()
    elif submenu == "Reporting Dashboard":
        display_reporting_dashboard()
    elif submenu == "JIRA & GIT Integration":
        interact_with_jira()


def settings_history_submenu():
    submenu = st.sidebar.radio(
        "⚙️ Settings & History",
        ["Settings", "Session History"],
        format_func=lambda x: {
            "Settings": "🔧 Settings",
            "Session History": "🕒 Session History"
        }[x]
    )
    if submenu == "Settings":
        manage_settings()
    elif submenu == "Session History":
        display_session_history()


if __name__ == "__main__":
    main()
