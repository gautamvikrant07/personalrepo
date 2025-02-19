import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from utils.session_management import save_session_history
import sqlite3

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_table_info(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    table_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        table_info[table_name] = [column[1] for column in columns]
    
    conn.close()
    return table_info

def impact_analysis():
    st.header("Impact Analysis")

    if 'db_file' not in st.session_state or not st.session_state['db_file']:
        st.error("Please load the database first.")
        return

    # Get table information using our custom function
    table_info = get_table_info(st.session_state['db_file'])

    # Create schema_info string
    schema_info = "\n".join([f"Table: {table}\nColumns: {', '.join(columns)}" for table, columns in table_info.items()])

    requirement_text = st.text_area("Enter the requirement text for impact analysis:")

    if st.button("Run Impact Analysis"):
        if requirement_text:
            try:
                # Generate impact analysis using OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant that analyzes database impact. Here's the database schema:\n{schema_info}"},
                        {"role": "user", "content": f"Based on the following requirement, identify the tables and columns that would be impacted. Return the result as a JSON object with 'impacted_tables' as the key and a list of dictionaries as the value. Each dictionary should have 'table_name' and 'columns' keys. Requirement: {requirement_text}"}
                    ]
                )
                impact_analysis = response.choices[0].message.content.strip()

                # Parse the JSON response
                import json
                impact_data = json.loads(impact_analysis)

                # Create a DataFrame from the impact data
                impact_df = pd.DataFrame([(table['table_name'], ', '.join(table['columns'])) 
                                          for table in impact_data['impacted_tables']], 
                                         columns=['Table', 'Impacted Columns'])

                st.write("Impact Analysis Results:")
                st.dataframe(impact_df)

                save_session_history(requirement_text, impact_df, "Impact Analysis")

                # Generate additional insights
                insights_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides insights on impact analysis results."},
                        {"role": "user", "content": f"Provide insights on the following impact analysis results:\n{impact_df.to_string()}"}
                    ]
                )
                insights = insights_response.choices[0].message.content.strip()

                st.write("Additional Insights:")
                st.write(insights)

            except Exception as e:
                st.error(f"An error occurred during impact analysis: {str(e)}")
        else:
            st.warning("Please enter a requirement text for impact analysis.")
