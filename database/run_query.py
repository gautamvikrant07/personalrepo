import os
import re
import json
import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from sqlite3 import Error
from utils.session_management import save_session_history
from langchain_community.utilities import SQLDatabase

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def call_openai_for_sql(validation_rule, schema_context):
    schema_info = f"The database contains the following tables and columns: {json.dumps(schema_context)}. " \
                  "Use this information to generate correct SQL queries."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": schema_info},
            {"role": "user", "content": f"Generate a SQL query to validate the following rule:\n{validation_rule}"}
        ],
        max_tokens=150,
        temperature=0.5
    )

    sql_query = response.choices[0].message.content.strip()

    match = re.search(r"```sql(.*?)```", sql_query, re.DOTALL)

    if match:
        sql_query = match.group(1).strip()
    else:
        sql_start = sql_query.find("SELECT")
        if sql_start != -1:
            sql_query = sql_query[sql_start:].strip()

    return sql_query

def run_sql_query(query):
    if 'db_file' not in st.session_state:
        st.error("Database file not loaded. Please load the database first.")
        return None

    db = SQLDatabase.from_uri(f"sqlite:///{st.session_state['db_file']}")
    
    try:
        result = db.run(query)
        df = pd.DataFrame(result)
        if df.empty:
            return None
        return df
    except Error as e:
        st.error(f"Error running SQL query: {e}")
        return None

def run_query():
    st.header("Run SQL Queries")

    user_query = st.text_area("Enter your query in natural language:")

    if st.button("Run Query"):
        schema_context = st.session_state.get('schema')

        if schema_context:
            sql_query = call_openai_for_sql(user_query, schema_context)

            if sql_query:
                result_df = run_sql_query(sql_query)

                if result_df is not None:
                    st.write("**Query Result:**")
                    st.dataframe(result_df)

                    save_session_history(user_query, result_df, "Run Query")

                    result_txt = result_df.to_csv(index=False, sep='\t')

                    st.download_button(
                        label="Save to File",
                        data=result_txt,
                        file_name='query_result.txt',
                        mime='text/plain'
                    )
                else:
                    st.error("No valid results were found or an error occurred.")
            else:
                st.error("Could not generate a valid SQL query from the provided input.")
        else:
            st.error("Schema context is missing. Please load the database first.")
