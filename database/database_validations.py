import streamlit as st
import pandas as pd
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback

def get_table_info(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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

def database_validations():
    st.header("Regulatory Data Validation")

    rules_file = st.file_uploader("Upload validation rules file", type=['txt'])
    
    if 'db_file' not in st.session_state or not st.session_state['db_file']:
        st.error("Please load a database file first.")
        return

    if rules_file is not None:
        rules = [line.strip() for line in rules_file.getvalue().decode("utf-8").split('\n') if line.strip()]

        if not rules:
            st.warning("No rules found in the uploaded file.")
            return

        table_info = get_table_info(st.session_state['db_file'])
        table_info_str = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in table_info.items()])

        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

        answer_prompt = PromptTemplate.from_template(
            """You are an SQL expert tasked with writing queries to validate data rules. Given the following validation rule and complete database schema information, write an SQL query that will return ONLY the records that violate this rule:

            Rule: {question}
            
            Complete Database Schema:
            {table_info}
            
            Important guidelines:
            1. Use the exact table and column names provided in the schema information.
            2. Ensure your query is compatible with SQLite syntax.
            3. When joining tables, select only specific columns to avoid duplicates.
            4. For aggregations, use subqueries or CTEs (Common Table Expressions) if necessary.
            5. Your query should return records that violate the rule, not records that comply with it.
            6. Pay close attention to the specific requirements of each rule, including any conditions or exceptions mentioned.
            
            Respond ONLY with the SQL query, nothing else. Do not include any explanations or additional text.
            SQL Query:"""
        )

        answer = answer_prompt | llm | StrOutputParser()

        st.subheader("Validation Results")

        for rule in rules:
            with st.expander(f"Rule: {rule}"):
                max_retries = 3
                previous_attempt = ""
                for attempt in range(max_retries):
                    try:
                        with st.spinner(f"Validating rule (Attempt {attempt + 1}/{max_retries})..."):
                            with get_openai_callback() as cb:
                                sql_query = answer.invoke({
                                    "question": rule, 
                                    "table_info": table_info_str,
                                    "previous_attempt": previous_attempt
                                })
                                st.write(f"Total Tokens: {cb.total_tokens}")
                                st.write(f"Total Cost (USD): ${cb.total_cost:.4f}")

                        st.write(f"**Generated SQL Query (Attempt {attempt + 1}):**")
                        st.code(sql_query, language="sql")

                        # Execute the query
                        conn = sqlite3.connect(st.session_state['db_file'])
                        df = pd.read_sql_query(sql_query, conn)
                        conn.close()

                        if df.empty:
                            st.success("✅ Validation rule passed.")
                        else:
                            st.error("❌ Validation rule failed.")
                            st.write("**Failing Records:**")
                            st.dataframe(df)

                        # If we reach here, the query was successful, so we break the retry loop
                        break

                    except Exception as e:
                        if attempt < max_retries - 1:
                            st.warning(f"Error in attempt {attempt + 1}: {str(e)}. Retrying...")
                            previous_attempt = sql_query
                        else:
                            st.error(f"Error validating rule after {max_retries} attempts: {str(e)}")
                            st.write("**Error Details:**")
                            st.write(f"SQL Query: {sql_query}")
                            st.write("**Table Information:**")
                            st.write(table_info_str)

    else:
        st.info("Please upload a file containing validation rules.")

if __name__ == "__main__":
    database_validations()
