from io import BytesIO
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


def handle_regulatory_reports() -> None:
    """Handle the Interact with Regulatory Reports section."""
    data_frames = upload_excel_files()
    if data_frames:
        compare_excel_reports(data_frames)
        selected_file = st.selectbox("Select a file to analyze:", options=list(data_frames.keys()))
        analyze_excel_report(data_frames[selected_file])


class AnalysisResult(BaseModel):
    key_findings: List[str] = Field(description="List of key findings from the report")
    compliance_issues: List[str] = Field(description="Potential compliance issues identified")
    trends: List[str] = Field(description="Noteworthy trends or anomalies observed")
    recommendations: List[str] = Field(description="Recommendations for further action")


def upload_excel_files():
    """
    Handles the upload of Excel files for COREP reports.

    Returns:
    - dict: A dictionary where the keys are filenames and the values are the corresponding DataFrames.
    """
    st.header("Upload Regulatory Reporting Templates")
    uploaded_files = st.file_uploader("Choose Excel files", accept_multiple_files=True, type=['xlsx'])
    data_frames = {}
    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            data_frames[uploaded_file.name] = df
            st.session_state[uploaded_file.name] = df
        st.success("Files uploaded successfully!")
    return data_frames


def compare_excel_reports(data_frames):
    """
    Compares two selected Excel reports and displays the differences.

    Parameters:
    - data_frames (dict): A dictionary containing the uploaded Excel files as DataFrames.
    """
    st.header("Compare Regulatory Reports")
    if len(data_frames) < 2:
        st.warning("Please upload at least two Excel files for comparison.")
        return

    file_options = list(data_frames.keys())
    file1 = st.selectbox("Select the first file for comparison:", options=file_options)
    file2 = st.selectbox("Select the second file for comparison:", options=file_options)

    if st.button("Compare Files"):
        df1 = data_frames[file1]
        df2 = data_frames[file2]

        if not df1.equals(df2):
            diff_df = pd.concat([df1, df2]).drop_duplicates(keep=False)
            st.dataframe(diff_df)
            st.write("Differences are highlighted above.")
        else:
            st.info("The files are identical.")


def analyze_excel_report(df):
    """
    Analyzes the selected Excel report using an LLM acting as a regulatory reporting expert.

    Parameters:
    - df (DataFrame): The DataFrame representing the Excel report to analyze.
    """
    st.header("Excel Report Analysis Using LLM")

    if df is None or df.empty:
        st.error("No data available for analysis.")
        return

    st.subheader("Summary Statistics")
    summary_stats = df.describe(include='all')
    st.write(summary_stats)

    sample_data = df.head(5)
    sample_description = sample_data.to_dict()

    prompt = f"""You are a regulatory reporting expert. Analyze the following Excel report data and provide insights.

    Summary Statistics:
    {summary_stats}

    Sample Data:
    {sample_description}

    Please provide a detailed analysis focusing on:
    1. Key findings
    2. Potential compliance issues
    3. Noteworthy trends or anomalies
    4. Recommendations for further action

    Format your response as follows:
    Key Findings:
    - Finding 1
    - Finding 2
    ...

    Compliance Issues:
    - Issue 1
    - Issue 2
    ...

    Trends:
    - Trend 1
    - Trend 2
    ...

    Recommendations:
    - Recommendation 1
    - Recommendation 2
    ...
    """

    chat = ChatOpenAI(temperature=0.2)

    try:
        message = HumanMessage(content=prompt)
        response = chat.generate([[message]])
        analysis = response.generations[0][0].text

        st.subheader("LLM Analysis")
        st.write(analysis)

    except Exception as e:
        st.error(f"An error occurred during LLM analysis: {e}")

    # New feature: Export Analysis
    st.subheader("Export Analysis")
    if st.button("Export Analysis to Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            summary_stats.to_excel(writer, sheet_name='Summary Statistics')
            sample_data.to_excel(writer, sheet_name='Sample Data')
            pd.DataFrame({'Analysis': [analysis]}).to_excel(writer, sheet_name='LLM Analysis', index=False)

        output.seek(0)
        st.download_button(
            label="Download Excel file",
            data=output,
            file_name="regulatory_report_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# New feature: Trend Analysis
def trend_analysis(data_frames):
    st.header("Trend Analysis")
    if len(data_frames) < 2:
        st.warning("Please upload at least two Excel files for trend analysis.")
        return

    file_options = list(data_frames.keys())
    selected_files = st.multiselect("Select files for trend analysis:", options=file_options)

    if len(selected_files) >= 2:
        common_columns = set.intersection(*[set(data_frames[file].columns) for file in selected_files])
        selected_column = st.selectbox("Select a column for trend analysis:", options=list(common_columns))

        trend_data = []
        for file in selected_files:
            trend_data.append(data_frames[file][selected_column].mean())

        fig = px.line(x=selected_files, y=trend_data, labels={'x': 'Files', 'y': f'Average {selected_column}'})
        fig.update_layout(title=f"Trend Analysis of {selected_column}")
        st.plotly_chart(fig)
