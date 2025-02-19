import logging
from typing import List, Tuple
import json
import streamlit as st
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_checklist() -> List[Tuple[str, bool]]:
    try:
        with open('json/compliance_checklist.json', 'r') as f:
            data = json.load(f)
        return [(item['task'], item['completed']) for item in data]
    except FileNotFoundError:
        logger.warning("json/compliance_checklist.json not found. Using sample data.")
        return [
            ("Annual report filed", True),
            ("KYC procedures updated", False),
            ("Staff training completed", True),
            ("Risk assessment performed", False),
            ("Basel III capital requirements met", True),
            ("Stress testing conducted", True),
            ("FATCA reporting completed", False),
            ("AML transaction monitoring system updated", True),
            ("GDPR compliance audit performed", False),
            ("Liquidity Coverage Ratio (LCR) calculated", True),
            ("Volcker Rule compliance verified", False),
            ("CCAR (Comprehensive Capital Analysis and Review) submitted", True),
            ("BCBS 239 risk data aggregation implemented", False),
            ("MiFID II transaction reporting reviewed", True),
            ("Dodd-Frank Act stress testing completed", False)
        ]

def display_compliance_checklist():
    try:
        st.header("Compliance Checklist")
        json_path = Path("json/compliance_checklist.json")
        
        if json_path.exists():
            with open(json_path, "r") as f:
                checklist_items = json.load(f)
            
            for item in checklist_items:
                st.checkbox(item['task'], value=item['completed'])
        else:
            st.warning("No compliance checklist data found.")
    except Exception as e:
        st.error(f"Error displaying compliance checklist: {str(e)}")
        logger.error(f"Error displaying compliance checklist: {str(e)}")
