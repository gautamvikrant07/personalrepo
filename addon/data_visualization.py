import os
import streamlit as st
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from io import StringIO

# Import necessary components from LangChain
from langchain import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase

# Set the API key for OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize the OpenAI LLM
llm = OpenAI(openai_api_key=openai_api_key, temperature=0)

# Function to create SQLite database from uploaded CSV
def create_sqlite_db(csv_file):
    df = pd.read_csv(csv_file)
    engine = create_engine('sqlite:///uploaded_data.db')
    df.to_sql('data_table', engine, if_exists='replace', index=False)
    return engine

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def select_visualization(df):
    if df.empty:
        st.write("No data to display.")
        return

    # Determine data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    date_cols = df.select_dtypes(include=['datetime64']).columns

    # Determine the best visualization based on data structure
    if len(df.columns) == 1:
        col = df.columns[0]
        if df[col].dtype in ['int64', 'float64']:
            fig = px.histogram(df, x=col, title=f"Distribution of {col}")
        else:
            value_counts = df[col].value_counts()
            fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Frequency of {col}")

    elif len(df.columns) == 2:
        col1, col2 = df.columns
        if df[col1].dtype in ['int64', 'float64'] and df[col2].dtype in ['int64', 'float64']:
            fig = px.scatter(df, x=col1, y=col2, title=f"{col2} vs {col1}")
        elif df[col1].dtype == 'datetime64[ns]':
            fig = px.line(df, x=col1, y=col2, title=f"{col2} over Time")
        else:
            fig = px.bar(df, x=col1, y=col2, title=f"{col2} by {col1}")

    elif len(df.columns) == 3:
        if len(numeric_cols) == 1 and len(categorical_cols) == 2:
            fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], color=categorical_cols[1],
                         title=f"{numeric_cols[0]} by {categorical_cols[0]} and {categorical_cols[1]}")
        elif len(numeric_cols) == 2 and len(categorical_cols) == 1:
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], color=categorical_cols[0],
                             title=f"{numeric_cols[1]} vs {numeric_cols[0]} by {categorical_cols[0]}")
        else:
            fig = px.parallel_categories(df, title="Parallel Categories Plot")

    else:
        if len(numeric_cols) >= 2:
            fig = make_subplots(rows=2, cols=2)
            for i, col in enumerate(numeric_cols[:4]):
                row = i // 2 + 1
                col = i % 2 + 1
                fig.add_trace(go.Box(y=df[col], name=col), row=row, col=col)
            fig.update_layout(title="Box Plots of Numeric Columns", height=800)
        else:
            fig = px.parallel_categories(df.iloc[:, :4], title="Parallel Categories Plot")

    # Update layout for better appearance
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=12),
        title_font=dict(size=20),
        legend_title_font=dict(size=14),
        legend_font=dict(size=12)
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Always display the dataframe for reference
    st.subheader("Data Table")
    st.dataframe(df)

# Streamlit App
def display_data_visualization():
    st.title("Natural Language Data Visualization App")

    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    if uploaded_file:
        st.success("CSV file uploaded successfully.")
        engine = create_sqlite_db(uploaded_file)
        db = SQLDatabase(engine)

        # Input for natural language question
        user_question = st.text_input("Enter your data analysis question:")
        if user_question:
            # Initialize the SQLDatabaseChain
            db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, return_intermediate_steps=True)

            # Generate SQL query from natural language question
            try:
                result = db_chain(user_question)
                
                # Debug information
                st.subheader("Debug Information:")
                st.json(result)
                
                # Extract SQL query from intermediate steps
                sql_query = None
                for step in result['intermediate_steps']:
                    if isinstance(step, str) and step.strip().upper().startswith("SELECT"):
                        sql_query = step
                        break
                
                if sql_query is None:
                    raise ValueError("SQL query not found in intermediate steps")

                st.write("Generated SQL Query:")
                st.code(sql_query, language='sql')

                # Execute SQL query and fetch results
                query_result = pd.read_sql_query(sql_query, engine)

                # Display the visualization
                st.write("Visualization:")
                select_visualization(query_result)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Full error details:")
                st.exception(e)
    else:
        st.info("Please upload a CSV file to proceed.")

    # Add information about testing and demonstration
    st.sidebar.header("Testing and Demonstration")
    st.sidebar.info("""
    To test this application:
    1. Upload a CSV file with sample data.
    2. Enter natural language questions about the data.
    3. View the generated visualizations.
    """)

if __name__ == "__main__":
    display_data_visualization()