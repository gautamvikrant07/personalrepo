import streamlit as st
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_scenario_analysis():
    try:
        st.header("Scenario Analysis")
        json_path = Path("json/scenarios.json")
        
        if json_path.exists():
            with open(json_path, "r") as f:
                scenarios = json.load(f)
            
            scenario_names = list(scenarios.keys())
            selected_scenario = st.selectbox("Select a scenario", scenario_names)
            
            scenario = scenarios.get(selected_scenario)
            
            if scenario:
                st.subheader(selected_scenario)
                st.write(f"Description: {scenario.get('description', 'No description available')}")
                st.write(f"Impact: {scenario.get('impact', 'N/A')}")
                st.write(f"Probability: {scenario.get('probability', 'N/A')}")
                
                st.subheader("Potential Effects:")
                effects = scenario.get('potential_effects', [])
                for effect in effects:
                    st.write(f"- {effect}")
                
                st.subheader("Stress Test Analysis")
                st.write("Based on this scenario, consider the following:")
                st.write("1. How would this scenario affect your institution's capital adequacy?")
                st.write("2. What would be the impact on your liquidity position?")
                st.write("3. How might this scenario affect your credit risk profile?")
                st.write("4. What operational challenges might arise from this scenario?")
                st.write("5. Are there any specific regulatory implications to consider?")
                
                user_analysis = st.text_area("Enter your analysis and mitigation strategies:")
                if st.button("Save Analysis"):
                    st.success("Analysis saved successfully!")
                    # Here you would typically save the user's analysis to a database or file
            else:
                st.warning("Selected scenario not found.")
        else:
            st.warning("No scenario analysis data found.")
    except Exception as e:
        st.error(f"Error in scenario analysis: {str(e)}")
        logger.error(f"Error in scenario analysis: {str(e)}")
