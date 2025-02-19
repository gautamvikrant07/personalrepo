import streamlit as st
import logging
import pandas as pd
import xml.etree.ElementTree as ET
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOpenAI
from io import StringIO, BytesIO
from langchain.agents import AgentExecutor, Tool
from langchain.schema import AgentAction, AgentFinish
import numpy as np

logger = logging.getLogger(__name__)

def read_file(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(uploaded_file, header=0)
    elif file_extension == 'csv':
        df = pd.read_csv(uploaded_file, header=0)
    elif file_extension == 'xml':
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        data = []
        for child in root:
            data.append({elem.tag: elem.text for elem in child})
        df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # If there are still unnamed columns, rename them
    df.columns = [f'Column_{i}' if 'Unnamed' in col else col for i, col in enumerate(df.columns)]
    
    # Function to safely convert to string
    def safe_convert(val):
        if pd.isna(val):
            return None
        elif isinstance(val, (int, float, bool)):
            return str(val)
        elif isinstance(val, (list, dict)):
            return str(val)
        else:
            return str(val)

    # Convert all columns to appropriate types
    for col in df.columns:
        # Try to convert to numeric
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except ValueError:
            # If not numeric, convert to string safely
            df[col] = df[col].apply(safe_convert)

    return df

def validate_regulatory_data():
    try:
        st.header("Regulatory Data Validation")
        uploaded_file = st.file_uploader("Upload regulatory report for validation", 
                                         type=['xls', 'xlsx', 'csv', 'xml'])
        
        if uploaded_file is not None:
            st.write(f"Analyzing file: {uploaded_file.name}")
            
            # Read the file
            df = read_file(uploaded_file)
            
            # Limit the number of rows
            max_rows = 1000  # Adjust this number as needed
            df = df.head(max_rows)
            
            # Create the agent
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
            agent = create_pandas_dataframe_agent(
                llm, 
                df, 
                verbose=True, 
                allow_dangerous_code=True
            )

            max_attempts = 3
            for attempt in range(max_attempts):
                analysis_prompt = f"""
                Analyze this regulatory report as a regulator. Check for any issues or inconsistencies in the data.
                Highlight all data validation failures, including but not limited to:
                1. Missing or incomplete data
                2. Inconsistent data formats
                3. Outliers or suspicious values
                4. Compliance with regulatory standards
                5. Discrepancies between related fields

                Be extremely thorough and double-check your findings. This is attempt {attempt + 1} of {max_attempts}.
                If you find any issues, explain them in detail. If you don't find any issues, explicitly state that you've double-checked and are certain there are no issues.

                Provide a detailed report of your findings.
                """

                try:
                    analysis_result = agent.run(analysis_prompt)
                    st.subheader(f"Regulatory Analysis Results (Attempt {attempt + 1})")
                    st.write(analysis_result)

                    if "issues" in analysis_result.lower() or "inconsistencies" in analysis_result.lower():
                        st.warning("The agent has identified potential issues with the data.")
                        st.write("Please review the analysis results carefully.")
                    else:
                        st.success("No issues were identified by the agent.")

                    confirmation_prompt = """
                    Review your analysis again. Are you absolutely certain (200% sure) that you haven't missed any issues?
                    If you're certain, respond with 'CONFIRMED'. If you're not completely sure, respond with 'RECHECK'.
                    """

                    confirmation = agent.run(confirmation_prompt)
                    st.write("Agent's confirmation:", confirmation)

                    if 'CONFIRMED' in confirmation.strip().upper():
                        st.success("The agent is certain about its analysis.")
                        break
                    elif attempt < max_attempts - 1:
                        st.info("The agent is rechecking the data...")
                    else:
                        st.warning("The agent has reached the maximum number of attempts.")

                except Exception as e:
                    st.error(f"Error in analysis attempt {attempt + 1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        st.error("Failed to complete the analysis after maximum attempts.")

            # Additional data validation checks
            st.subheader("Additional Data Validation Checks")
            
            # Check for missing values
            missing_values = df.isnull().sum()
            if missing_values.sum() > 0:
                st.warning("Missing values detected:")
                st.write(missing_values[missing_values > 0])
            else:
                st.success("No missing values detected.")
            
            # Display a sample of the data
            st.subheader("Sample Data")
            st.write(df.head())

    except Exception as e:
        st.error(f"Error in data validation: {str(e)}")
        logger.error(f"Error in data validation: {str(e)}")
